import numpy as np 
import pandas as pd 

class Risk():
    def __init__(self, risk_path='distribution.csv'):
        all_risk = pd.read_csv(risk_path)