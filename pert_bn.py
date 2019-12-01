import numpy as np 
import os 
import matplotlib.pyplot as plt 

from bayes_net import Risk, Node
from dataset import Project

out_fig = './fig'

CPT_R_ED = [
    ['1', '1', '1', 0.7],
    ['1', '0', '1', 1],
    ['0', '1', '1', 0],
    ['0', '0', '1', 0.3],
    ['1', '1', '0', 0.3],
    ['1', '0', '0', 0],
    ['0', '1', '0', 1],
    ['0', '0', '0', 0.7],
]

total_risk = Risk()
total_risk_prob = total_risk.get_risk_prob()
print(total_risk_prob.parameters)

proj = Project()
proj.update()
proj.check()

for i in range(len(proj.id)):
    ed_task = proj.task[i].ed
    time_circum = [ed_task-2, ed_task-1, ed_task, ed_task+1, ed_task+2]
    prob_circum = []
    prob_list_task = proj.task[i].ed_prob
    for j in range(len(prob_list_task)):
        ed_prob = prob_list_task[j]
        # print(prob)

        #### merge with risk
        prob = Node('prob')
        prob.set_predecessor([ed_prob, total_risk_prob], prob=True) # 2 parent, ed_prob - total_risk_prob
        prob.set_cpt(CPT_R_ED)
        prob.calc_prob()
        print('Risk', total_risk_prob.parameters[0])
        print('ED', ed_prob.parameters[0])
        print('TD', prob.prob.parameters[0])
        prob_circum.append([prob.prob.parameters[0]['1']])
    
    plt.plot(time_circum, prob_circum)
    plt.scatter(time_circum, prob_circum)
    plt.ylim([0, 1])
    plt.savefig(os.path.join(out_fig, 'Task_{}.png'.format(i)))
    plt.close()
    # plt.show()
    # input()

