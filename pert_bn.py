import numpy as np 
import os 
import matplotlib.pyplot as plt 
from pomegranate import *

from bayes_net import Risk, Node
from dataset import Project
import config

out_fig = config.OUT_FIG

if not os.path.exists(out_fig):
    os.makedirs(out_fig)

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

CPT_ES_TD = [
    ['1', '1', '1', 1],
    ['1', '0', '1', 0.7],
    ['0', '1', '1', 0.3],
    ['0', '0', '1', 0],
    ['1', '1', '0', 0],
    ['1', '0', '0', 0.3],
    ['0', '1', '0', 0.7],
    ['0', '0', '0', 1],
]

total_risk = Risk()
total_risk_prob = total_risk.get_risk_prob()
# print(total_risk_prob.parameters)

proj = Project()
proj.update()
# proj.check()

for i in range(len(proj.id)):
    print('Processing task {} ...'.format(i))
    ed_task = proj.task[i].ed
    time_circum = [max(ed_task-2, 0), max(ed_task-1, 0), ed_task, ed_task+1, ed_task+2]
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
        # print('Risk', total_risk_prob.parameters[0])
        # print('ED', ed_prob.parameters[0])
        # print('TD', prob.prob.parameters[0])
        prob_circum.append(prob.prob.parameters[0]['1'])
    
    # print(prob_circum)
    proj.task[i].set_td(prob_circum)
    # input()

    # plot result
    plt.plot(time_circum, prob_circum)
    plt.scatter(time_circum, prob_circum)
    for j in range(len(time_circum)):
        plt.text(time_circum[j], prob_circum[j]+0.02, '{}'.format(round(100*prob_circum[j], 2)))
    plt.ylim([0, 1])
    plt.xlabel('Time')
    plt.ylabel('Probability')
    plt.title('Probability time completion for task {}'.format(i))
    plt.savefig(os.path.join(out_fig, 'Task_{}.png'.format(i)))
    plt.close()
    plt.show()

### compute time completion for all project

############ Strategy 1: average
proj_completion_time = np.array([0, 0, 0, 0, 0])
proj_completion_prob = [1, 1, 1, 1, 1]
for i in range(len(proj.critical)):
    # critical_path.append(proj.task[proj.critical[i]].name)
    proj_completion_time += proj.task[i].ed_list
    # print(proj.task[i].td)
    for j in range(len(proj_completion_prob)):
        proj_completion_prob[j] = (proj_completion_prob[j] + proj.task[i].td[j])/2

############ Strategy 2: use bayes network
proj_completion_time_2 = np.array([0, 0, 0, 0, 0])
proj_completion_prob_2 = [DiscreteDistribution({'1': 1, '0': 0})]*5
for i in range(len(proj.critical)):
    proj_completion_time_2 += proj.task[i].ed_list
    for j in range(len(proj_completion_prob_2)):
        prob_node = Node('node')
        td_node = DiscreteDistribution({'1': proj.task[i].td[j], '0': 1-proj.task[i].td[j]})
        prob_node.set_predecessor([proj_completion_prob_2[j], td_node], prob=True)
        prob_node.set_cpt(CPT_ES_TD)
        prob_node.calc_prob()
        proj_completion_prob_2[j] = prob_node.prob

proj_completion_prob_2 = [i.parameters[0]['1'] for i in proj_completion_prob_2]
# print(proj_completion_prob_2)
print('Critical path: ', '-'.join(proj.critical_path))
print('Time to complete project: ', proj.time_completion)

fig, ax = plt.subplots(1, 2, figsize=(16, 6))

ax[0].plot(proj_completion_time, proj_completion_prob)
ax[0].scatter(proj_completion_time, proj_completion_prob)
for i in range(len(proj_completion_time)):
    ax[0].text(proj_completion_time[i], proj_completion_prob[i]+0.02, '{}'.format(round(100*proj_completion_prob[i], 2)))
ax[0].set_ylim([0, 1])
ax[0].set_title('Stategy 1')

ax[1].plot(proj_completion_time, proj_completion_prob_2)
ax[1].scatter(proj_completion_time, proj_completion_prob_2)
for i in range(len(proj_completion_time)):
    ax[1].text(proj_completion_time[i], proj_completion_prob_2[i]+0.02, '{}'.format(round(100*proj_completion_prob_2[i], 2)))
ax[1].set_ylim([0, 1])
ax[1].set_title('Stategy 2')


# plt.xlabel('Time completion')
# plt.ylabel('Probability')
# plt.title('Probability for time completion of Project')
plt.savefig(os.path.join(out_fig, 'Time_completion.png'))


    



