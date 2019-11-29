import numpy as np 
from math import erf, sqrt

def beta(x, mu, sigma):
    x_norm = (x-mu) / sigma

    pass 

def gauss(x, mu, sigma):
    x_norm = (x-mu) / sigma
    return (1.0 + erf(x_norm/sqrt(2))) / 2

def find_index(arr, ele):
    for i in range(len(arr)):
        if arr[i]==ele:
            return i 
    return None

