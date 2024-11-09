import os
import pandas as pd
import matplotlib.pyplot as plt 
def load_data(path , load_json = False):
    db ={}
    # Load data from database
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, path)
    path = path if path else 'data'
    files = os.listdir(path)
    for file in files:
        print(file)
        if file.endswith('.csv'):
            file_name = file.split('.')[0]
            db[file_name] = pd.read_csv(f'{path}/{file}')
            if load_json:
                db[file_name] = db[file_name].to_json()
    return db
