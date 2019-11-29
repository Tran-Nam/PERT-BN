import numpy as np 
import pandas as pd 

class Node():
    def __init__(self, name, predecessor):
        self.name = name 
        self.predecessor = predecessor
    
    def set_prob(self, prob):
        self.prob = prob
        return self

    def create_cpt(self, cpt):
        return self 

    def calc_prob(self):
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