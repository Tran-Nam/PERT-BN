import numpy as np 
import pandas as pd 
from pomegranate import *
from utils import *
import config



class Task():
    def __init__(self, name, mos, opt, pes):
        self.name = name
        self.ed = mos 
        self.ed_list = np.array([max(self.ed-2, 0), max(self.ed-1, 0), self.ed, self.ed+1, self.ed+2])
        self.opt = opt 
        self.pes = pes
        self.mu = (self.opt + 4*self.ed + self.pes) / 6
        self.sigma = (self.pes - self.opt) / 6

    def set_predecessor(self, predecessor):
        self.predecessor = predecessor
        return self
    
    def set_successor(self, successor):
        self.successor = successor
        return self

    def set_es(self, es):
        self.es = es
        return self 

    def set_lf(self, lf):
        self.lf = lf
        return self

    def set_td(self, td):
        self.td = td 
        return self

    def update(self):
        self.ef = self.es + self.ed 
        self.ls = self.lf - self.ed
        self.slack = self.ls - self.es

        # self.cpt = {
        #     '-2': gauss(self.ed-2, self.mu, self.sigma),
        #     '-1': gauss(self.ed-1, self.mu, self.sigma),
        #     '0': gauss(self.ed, self.mu, self.sigma),
        #     '1': gauss(self.ed+1, self.mu, self.sigma),
        #     '2': gauss(self.ed+2, self.mu, self.sigma)
        # }

        prob_list = [
            gauss(self.ed-2, self.mu, self.sigma),
            gauss(self.ed-1, self.mu, self.sigma),
            gauss(self.ed-0, self.mu, self.sigma),
            gauss(self.ed+1, self.mu, self.sigma),
            gauss(self.ed+2, self.mu, self.sigma),
        ]

        self.ed_prob = []
        for i in range(len(prob_list)):
            self.ed_prob.append(DiscreteDistribution({'1': prob_list[i], '0': 1-prob_list[i]}))

        return self

class Project():
    def __init__(self, proj_path=config.PROJECT_PATH):
        all_tasks = pd.read_csv(proj_path)
        self.id = list(all_tasks['id'])
        self.optimistic = list(all_tasks['optimistic'])
        self.mostlikely = list(all_tasks['moslikely'])
        self.pessimistic = list(all_tasks['pessimistic'])
        self.predecessor = list(all_tasks['Predecessor'])
        ## update successor
        self.successor = ['']*len(self.id)
        for i in range(len(self.id)):
            curr_id = self.id[i]
            for j in range(i, len(self.id)):
                if curr_id in self.predecessor[j]:
                    self.successor[i] += self.id[j] + ' '
        self.task = [None]*len(self.id)
    def update(self):

        # init task object
        # predecessor
        for i in range(len(self.id)):
            self.task[i] = Task(self.id[i], self.mostlikely[i], self.optimistic[i], self.pessimistic[i]) # init
            pres = self.predecessor[i].split(' ')
            pres_idx = []
            pres_task = []
            for pre in pres:
                idx = find_index(self.id, pre)
                if idx is not None:
                    pres_idx.append(idx)
            for idx in pres_idx:
                if idx is not None:
                    pres_task.append(self.task[idx])
            self.task[i].set_predecessor(pres_task)

        # successor
        for i in range(len(self.id)-1, -1, -1):
            sucs = self.successor[i].split(' ')
            sucs_idx = []
            sucs_task = []
            for suc in sucs:
                idx = find_index(self.id, suc)
                if idx is not None:
                    sucs_idx.append(idx)
            for idx in sucs_idx:
                if idx is not None:
                    sucs_task.append(self.task[idx])
            self.task[i].set_successor(sucs_task)


        # es for first task
        self.task[0].set_es(0)
        
        
        # set es for all task
        for i in range(1, len(self.id)):
            if len(self.task[i].predecessor) == 0:
                self.task[i].set_es(0)
            else:
                task_es = 0
                for j in range(len(self.task[i].predecessor)):
                    pre_ed = self.task[i].predecessor[j].ed 
                    pre_es = self.task[i].predecessor[j].es 
                    if pre_ed + pre_es > task_es:
                        task_es = pre_ed + pre_es
                self.task[i].set_es(task_es)

        # set lf for last task
        self.task[-1].set_lf(self.task[-1].es + self.task[-1].ed)

        # set lf for all task
        for i in range(len(self.id)-1, -1, -1):
            if len(self.task[i].successor) == 0:
                self.task[i].set_lf(self.task[i].es + self.task[i].ed)
            else:
                task_lf = 1000
                for j in range(len(self.task[i].successor)):
                    suc_ed = self.task[i].successor[j].ed 
                    suc_lf = self.task[i].successor[j].lf 
                    if suc_lf - suc_ed < task_lf:
                        task_lf = suc_lf - suc_ed
                self.task[i].set_lf(task_lf)

        # update all value in task
        for i in range(len(self.id)):
            self.task[i].update()

        # find critical path
        self.critical = []
        for i in range(len(self.id)):
            if self.task[i].slack==0:
                self.critical.append(i)
        # print(self.critical)

        return self 
    
    def check(self):
        print('Time for each task: ed, es, ef, ls, lf')
        for i in range(0, len(self.id)):
            print(i, self.task[i].ed, self.task[i].es, self.task[i].ef, self.task[i].ls, self.task[i].lf)
        print('Task in critical path')
        for i in range(0, len(self.id)):
            if self.task[i].slack == 0:
                print(self.task[i].name)
        print('Prob for each task')
        for i in range(len(self.id)):
            print('Task {}'.format(i))
            for j in range(len(self.task[i].ed_prob)):
                print(self.task[i].ed_prob[j].parameters)
                    
# proj = Project()
# proj.update()
# proj.check()


