import numpy as np 
import os 
import matplotlib.pyplot as plt 


from bayes_net import Risk, Node
from dataset import Project
import config

out_fig = config.OUT_FIG

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
        prob_circum.append([prob.prob.parameters[0]['1']])
    
    # print(prob_circum)
    proj.task[i].set_td(prob_circum)
    # input()

    # plot result
    plt.plot(time_circum, prob_circum)
    plt.scatter(time_circum, prob_circum)
    plt.ylim([0, 1])
    plt.xlabel('Time')
    plt.ylabel('Probability')
    plt.title('Probability time completion for task {}'.format(i))
    plt.savefig(os.path.join(out_fig, 'Task_{}.png'.format(i)))
    plt.close()
    plt.show()

### compute time completion for all project
proj_completion_time = np.array([0, 0, 0, 0, 0])
proj_completion_prob = [1, 1, 1, 1, 1]
critical_path = []
for i in range(len(proj.critical)):
    critical_path.append(proj.task[proj.critical[i]].name)
    proj_completion_time += proj.task[i].ed_list
    # print(proj.task[i].td)
    for j in range(len(proj_completion_prob)):
        proj_completion_prob[j] = (proj_completion_prob[j] + proj.task[i].td[j][0])/2

print('Critical path: ', '-'.join(critical_path))

plt.plot(proj_completion_time, proj_completion_prob)
plt.scatter(proj_completion_time, proj_completion_prob)
plt.ylim([0, 1])
plt.xlabel('Time completion')
plt.ylabel('Probability')
plt.title('Probability for time completion of Project')
plt.savefig(os.path.join(out_fig, 'Time_completion.png'))


    



