import numpy as np 
import pandas as pd 
import itertools
from pomegranate import *

class Node():
    def __init__(self, name):
        self.name = name 
        # self.predecessor = predecessor

    def set_predecessor(self, predecessor):
        self.predecessor = []
        # print(predecessor)
        for pre in predecessor:
            self.predecessor.append(pre.prob)
        return self
    
    def set_prob(self, prob):
        self.prob = DiscreteDistribution({'1': prob, '0': 1-prob})
        return self

    def create_cpt(self, cpt):
        n_pres = len(self.predecessor)
        print(len(cpt), n_pres)
        if n_pres==0:
            self.cpt = []
            return self
        mat = list(itertools.product('10', repeat=n_pres+1))
        mat = [list(i) for i in mat]
        for i in range(len(mat)):
            mat[i].append(cpt[i-1])
        self.cpt = mat
        return self 

    def calc_prob(self):
        n_pres = len(self.predecessor)
        # print(self.cpt)
        node = ConditionalProbabilityTable(
            self.cpt,
            self.predecessor
        )
        # print(node)
        # print(self.name)
        model = BayesianNetwork(str(self.name))
        # print(model)
        
        node = State(node, name='node')
        model.add_state(node)
        # print(model)

        for i in range(len(self.predecessor)):
            # print(self.predecessor[i].prob)
            par_state = State(self.predecessor[i], name='par_{}'.format(i))
            model.add_state(par_state)
            model.add_edge(par_state, node)
        print('='*20)
        # print(model)
        model.bake()

        mat = list(itertools.product('10', repeat=n_pres))
        mat = [list(i) for i in mat]
        
        prob = 0
        for i in range(len(mat)):
            mat[i].append('1')
            # print(mat[i])
            prob += model.probability(mat[i])
        
        self.prob = DiscreteDistribution({'1': prob, '0': 1-prob})

        return self

class Risk():
    def __init__(self, n_risk=20, relation_path='risk_relate.txt', distribution_path='distribution.txt'):
        self.parents = []
        self.node = []
        self.prob_list = []
        mat = np.ones((n_risk, n_risk)).astype('int')
        with open(relation_path, 'r') as f:
            for i in range(n_risk):
                parent_nodes = f.readline()[:-1].split(',') ## last character is '\n'
                parent_nodes = [int(i) for i in parent_nodes]
                self.parents.append(parent_nodes)
                for node in parent_nodes:
                    
                    if node==0:
                        break
                    mat[i, node-1] = 0
        print(self.parents)
        self.order = []
        while len(self.order)!=n_risk:
            prod = np.prod(mat, axis=1)
            node_can_update = np.where(prod==1)[0]
            self.order.extend(node_can_update)
            for node_idx in node_can_update:
                mat[:, node_idx] = 1 # updated
                mat[node_idx, :] = 0

        ## create node in bayes net
        # with open(relation_path, 'r') as f_re:
        with open(distribution_path, 'r') as f_dis:
            for i in range(n_risk):
                # parent_nodes = f_re.readline()[:-1].split(',') ## last character is '\n'
                prob_list = f_dis.readline()[:-1].split(',')
                prob_list = [float(j) for j in prob_list]
                
                node = Node('{}'.format(i))
                self.node.append(node)
                self.prob_list.append(prob_list)
        # print(self.prob_list)

        for idx in self.order:
            if len(self.prob_list[idx])==2:
                self.node[idx].set_prob(self.prob_list[idx][0])
                # print(self.node[idx].prob)
                print('NOT HAVE PARENT')
            else:
                predecessor = []
                print(self.parents[idx])
                for j in self.parents[idx]:
                    predecessor.append(self.node[j-1])
                
                self.node[idx].set_predecessor(predecessor)
                print('Done set pre')
                print(len(self.prob_list[idx]))
                self.node[idx].create_cpt(self.prob_list[idx])
                
                print('Done create cpt')

                self.node[idx].calc_prob()
                print('Done calc prob')
                print('HAVE PARENT')
                    
                


            
        print(self.order)

        for i in range(n_risk):
            print(self.node[i].prob.parameters[0])


                
if __name__=='__main__':
    risk = Risk()