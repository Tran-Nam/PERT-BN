import numpy as np 
import os 
import matplotlib.pyplot as plt 
from pomegranate import *

from bayes_net import Risk, Node
from dataset import Project
import config
from utils import gauss

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
    ['1', '0', '1', 0.5],
    ['0', '1', '1', 0.5],
    ['0', '0', '1', 0],
    ['1', '1', '0', 0],
    ['1', '0', '0', 0.5],
    ['0', '1', '0', 0.5],
    ['0', '0', '0', 1],
]

total_risk = Risk()
total_risk_prob = total_risk.get_risk_prob()
# print(total_risk_prob.parameters)

proj = Project()
proj.update()
# proj.check()

for i in range(len(proj.id)):
    # print('Processing task {} ...'.format(i))
    ed_task = proj.task[i].ed
    time_circum = []
    for datum in range(-config.n_datum, config.n_datum+1):
        # print(i)
        time_circum.append(max(ed_task+datum, 0))
    # time_circum = [max(ed_task-2, 0), max(ed_task-1, 0), ed_task, ed_task+1, ed_task+2] ########
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
    plt.title('Probability time completion for task {}'.format(proj.id[i]))
    plt.savefig(os.path.join(out_fig, 'Task_{}.png'.format(proj.id[i])))
    plt.close()
    plt.show()

############ Strategy 2: use bayes network ##### WRONG!
proj_completion_time_2 = np.zeros((2*config.n_datum+1, ))
proj_completion_prob_2 = [DiscreteDistribution({'1': 1, '0': 0})] * (2*config.n_datum+1)
for i in proj.critical:
    # print(proj_completion_time_2.shape, proj.task[i])
    proj_completion_time_2 += proj.task[i].ed_list
    for j in range(len(proj_completion_prob_2)):
        prob_node = Node('node')
        td_node = DiscreteDistribution({'1': proj.task[i].td[j], '0': 1-proj.task[i].td[j]})
        prob_node.set_predecessor([proj_completion_prob_2[j], td_node], prob=True)
        prob_node.set_cpt(CPT_ES_TD)
        prob_node.calc_prob()
        proj_completion_prob_2[j] = prob_node.prob

########## Use literature of PERT
####### calc mean of sigma of node total time #######
# proj_completion_time_3 = np.zeros((2*config.n_datum+1, ))
est_time_completion = 0
est_mu = 0
est_sigma = 0

# est_time_completion = proj.time_completion ###????
completion_node = Node('completion')
for i in proj.critical:
    est_time_completion += proj.task[i].ed
    est_mu += proj.task[i].mu
    est_sigma += proj.task[i].sigma**2
est_sigma = est_sigma**0.5 ##### formula

proj_completion_time_3 = []
proj_completion_prob_3 = [DiscreteDistribution({'1': 1, '0': 0})] * (2*config.n_datum+1)
for datum in range(-config.n_datum, config.n_datum+1):
    proj_completion_time_3.append(est_time_completion + len(proj.critical)*datum)
for i in range(len(proj_completion_time_3)):
    prob_node = Node('node')
    td_node_prob = gauss(proj_completion_time_3[i], est_mu, est_sigma)
    print(td_node_prob)
    td_node = DiscreteDistribution({'1': td_node_prob, '0': 1-td_node_prob})
    prob_node.set_predecessor([td_node, total_risk_prob], prob=True)
    prob_node.set_cpt(CPT_R_ED)
    prob_node.calc_prob()
    proj_completion_prob_3[i] = prob_node.prob.parameters[0]['1']



proj_completion_prob_2 = [i.parameters[0]['1'] for i in proj_completion_prob_2]
# print(proj_completion_prob_2)
print('='*50)
print('INFO TASK')
print(proj.info_task)
print('='*50)
print('Critical path: ', '-'.join(proj.critical_path))
print('Time to complete project: ', proj.time_completion)
print('='*50)

"""
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
"""
plt.plot(proj_completion_time_3, proj_completion_prob_3)
plt.scatter(proj_completion_time_3, proj_completion_prob_3)
for i in range(len(proj_completion_time_3)):
    plt.text(proj_completion_time_3[i], proj_completion_prob_3[i]+0.02, '{}'.format(round(100*proj_completion_prob_3[i], 2)))

plt.ylim([0, 1])
plt.xlabel('Time completion')
plt.ylabel('Probability')
plt.title('Probability for time completion of Project')
plt.savefig(os.path.join(out_fig, 'Time_completion.png'))


    



