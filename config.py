import os

PROJECT_PATH = 'project_data/2.csv'
BASE_OUT_FIG = './fig_new'
RELATION_RISK_PATH = 'risk_data_generate/risk_relate.txt'
DISTRIBUTION_PATH = 'risk_data_generate/distribution_generate.txt'
# RELATION_RISK_PATH = 'risk_data/risk_relate.txt'
# DISTRIBUTION_PATH = 'risk_data/distribution.txt'
project_name = PROJECT_PATH.split('/')[-1].split('.')[0]
OUT_FIG = os.path.join(BASE_OUT_FIG, project_name)