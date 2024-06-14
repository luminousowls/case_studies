
import pandas as pd
csv_path = "./data/case2"

from app.utils.allocate_supply import allocate_supply 

protect_list = [
    ['Jan Wk4', 'PAC', 35]
]

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

#from a list of weeks and list of protected items, creates df to track protected items
def create_protect_df(index, protect_list):
    '''
        creates a protect_df from a list of protected items
    '''
    protect_df = pd.DataFrame({'Weeks': index})
    protect_df = protect_df.set_index('Weeks')

    products = {product for _, product, _ in protect_list}
    for product in products:
        protect_df[product] = float('nan')

    for week, product, qty in protect_list:
        protect_df.loc[week, product] = qty

    protect_df.ffill(inplace=True)
    protect_df.bfill(inplace=True)

    for product in products:
        max_value = protect_df[product].max()
        protect_df[product] = max_value

    return protect_df

#adjusts protect_list so it doesn't allocate more than total material TO CHANGE
def adjust_protect(total_material, total_protect, protect_list):
    '''
    adjusts protect list so that it doesn't allocate more than total material
    returns adjusted protect_list and remaining total_material
    '''
    if total_material < total_protect:
        for i in range(len(protect_list)):
            protect_list[i][2] *= total_material / total_protect
        total_protect = total_material
        total_material = max(total_material - total_protect, 0)
    return total_protect, protect_list

#add build time to material A df 
def add_build_time(df, build_time):
    '''
    shifts material A df to the right according to build time.
    returns adjusted df
    '''
    for i in range(build_time):
        df.insert(0, 'Build Time', [0] * len(df.index))
    return df


#adjust CSD DataFrame
def adjust_csd(csd_df, wk1_builds):
    """
    removes wk1builds from demand df
    returns adjusted demand df 
    """
    adjusted_csd_df = csd_df - wk1_builds.iloc[0]
    adjusted_csd_df[adjusted_csd_df < 0] = 0
    return adjusted_csd_df


#calculate supply for Superman Plus
def calculate_supply(a_df, csd_df):
    """
   calculate amount of supply to allocate to superman plus.
   based on amt of material a, superman and superman mini demand and priority
   returns superman plus supply
    """    
    #calculate demand for Superman and Superman Mini
    total_demand_s_sm = csd_df['Superman'] + csd_df['Superman Mini']
    
    #allocate supply to Superman Plus
    sp_supply_df = a_df.copy()
    sp_supply_df -= total_demand_s_sm  # Deduct demand for Superman and Superman Mini from available supply
    sp_supply_df = sp_supply_df.clip(lower=0).transpose().squeeze()  # Clip negative values to zero
    
    #calculate remaining supply for Superman and Superman Mini
    s_sm_supply_df = a_df.copy()
    s_sm_supply_df -= sp_supply_df  # Deduct allocated supply for Superman Plus
    s_sm_supply_df = s_sm_supply_df.clip(lower=0).transpose().squeeze()  # Clip negative values to zero
    return sp_supply_df, s_sm_supply_df

#adds wk1 builds to available supply
def add_wk1_builds(supply_df, wk1_builds, column):
    """
    add wk1 builds to supply df
    returns adjusted supply df
    """
    for i in range(len(supply_df)):
        supply_df.iloc[i] += wk1_builds[column][0]
    return supply_df

def allocate(a_df, protect_list):
    csd_df = csv_to_df(csv_path, 'Demand FCT', transpose=True)
    wk1_builds = csv_to_df(csv_path, 'Wk1 Builds')
    cpd_df = csv_to_df(csv_path, 'plus_demand', transpose=True)

    cpd_df = cpd_df.drop('Reseller Partners', axis=1)
    total_material = a_df.iloc[0, -1]
    total_protect = sum([qty for date, prod, qty in protect_list])
    protect_df = create_protect_df(cpd_df.index, protect_list)
    print('protect_df',protect_df)
    total_protect, protect_list = adjust_protect(total_material, total_protect, protect_list)

    s_sm_wk1_allocation = pd.concat([
        allocate_supply(csd_df[['Superman']], pd.DataFrame({"Superman": [wk1_builds['Superman'].iloc[0]] * len(cpd_df.index)}).set_index(cpd_df.index).squeeze(), protect_df),
        allocate_supply(csd_df[['Superman Mini']], pd.DataFrame({'Superman Mini': [wk1_builds['Superman Mini'].iloc[0]] * len(cpd_df.index)}).set_index(cpd_df.index).squeeze(), protect_df)
    ], axis=1)
    s_sm_wk1_allocation = s_sm_wk1_allocation[['Superman', 'Superman Mini']]
    sp_wk1_allocation = allocate_supply(cpd_df, pd.DataFrame({"Superman Plus": [wk1_builds['Superman Plus'].iloc[0]] * len(cpd_df.index)}).set_index(cpd_df.index).squeeze(), protect_df)
    csd_df = csd_df - pd.concat([s_sm_wk1_allocation, sp_wk1_allocation], axis=1)
    sp_supply_df, s_sm_supply_df = calculate_supply(a_df, csd_df)
    cpd_df -= sp_wk1_allocation
    s_sm_allocation = allocate_supply(csd_df[['Superman', 'Superman Mini']], s_sm_supply_df, protect_df)
    sp_allocation = allocate_supply(cpd_df, sp_supply_df, protect_df)

    total_allocation = pd.concat([
        s_sm_wk1_allocation.add(s_sm_allocation, fill_value=0),
        sp_allocation.add(sp_wk1_allocation, fill_value=0)
    ], axis=1)
    total_allocation.reset_index(inplace=True)
    total_allocation.rename(columns={'index': 'Weeks'}, inplace=True)
    print(total_allocation)
    return total_allocation

#read input data and run allocation
a_df = csv_to_df(csv_path, 'Material A supply') # Amount of supply
allocate(a_df, protect_list)