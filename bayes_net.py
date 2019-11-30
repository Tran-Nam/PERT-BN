import numpy as np 
import pandas as pd 
import itertools
from pomegranate import *

class Node():
    def __init__(self, name, predecessor):
        self.name = name 
        self.predecessor = predecessor
    
    def set_prob(self, prob):
        self.prob = DiscreteDistribution({'1': prob, '0': 1-prob})
        return self

    def create_cpt(self, cpt):
        n_pres = len(self.predecessor)
        mat = list(itertools.product('10', repeat=n_pres))
        mat = [list(i) for i in mat]
        for i in range(len(mat)):
            mat[i].append(cpt[i])
        self.cpt = mat
        return self 

    def calc_prob(self):
        node = ConditionalProbabilityTable(
            self.cpt,
            self.predecessor
        )

        model = BayesianNetwork(self.name)
        
        node = State(node, name='node')
        model.add_state(node)

        for i in range(len(self.predecessor)):
            par_state = State(self.predecessor[i], name='par_{}'.format(i))
            model.add_state(par_state)
            model.add_edge(par_state, node)
        
        model.bake()

        mat = list(itertools.product('10', repeat=n_pres))
        mat = [list(i) for i in mat]
        
        prob = 0
        for i in range(len(mat)):
            mat[i].append('1')
            prob += model.probability[mat[i]]
        
        self.prob = DiscreteDistribution({'1': prob, '0': 1-prob})

        return self

class Risk():
    def __init__(self, n_risk=20, relation_path='risk_relate.txt'):
        mat = np.ones((n_risk, n_risk)).astype('int')
        with open(relation_path, 'r') as f:
            for i in range(n_risk):
                parent_nodes = f.readline()[:-1].split(',') ## last character is '\n'
                for node in parent_nodes:
                    idx = int(node)
                    if idx==0:
                        break
                    mat[i, idx-1] = 0
        # print(mat)
        self.order = []
        while len(self.order)!=n_risk:
            prod = np.prod(mat, axis=1)
            node_can_update = np.where(prod==1)[0]
            self.order.extend(node_can_update)
            for node_idx in node_can_update:
                mat[:, node_idx] = 1 # updated
                mat[node_idx, :] = 0
            
        print(self.order)


                
if __name__=='__main__':
    risk = Risk()