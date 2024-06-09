
import pandas as pd
csv_path = "./data/case2"


#read csv into df
def csv_to_df(csv_path, filename, transpose=False):
    '''
    returns a df that has been read in from a csv file
    '''
    df = pd.read_csv(f"{csv_path}/{filename}.csv")
    if transpose:
        df = df.transpose()
        df.columns = df.iloc[0]
        df = df[1:]
    return df

csd_df = csv_to_df(csv_path, 'Demand FCT', transpose=True) #cumulative demand for all 3 programs
cpd_df = csv_to_df(csv_path, 'plus_demand', transpose=True) #cumulative demand for all venders of plus
