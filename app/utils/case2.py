
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
    protect_df = pd.DataFrame({'Weeks': index, 'Protect':[0] * len(index)})
    protect_df = protect_df.set_index('Weeks')
    for week, product, qty in protect_list:
        protect_df.loc[week:, 'Protect'] += qty
    return protect_df

#adjusts protect_list so it doesn't allocate more than total material TO CHANGE
def adjust_protect(total_material, total_protect, protect_list):
    '''
    adjusts protect list so that it doesn't allocate more than total material
    returns adjusted protect_list and remaining total_material
    '''
    if total_material < total_protect:
        for i in range(len(protect_list)):
            protect_list[i][2] *= total_material/total_protect
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
        df.insert(0, 'Build Time', [0]*len(df.index))
    return df

#TO CHANGE
def adjust_csd(csd_df, wk1_builds):
    """
    removes wk1builds from demand df
    returns adjusted demand df 
    """
    for prod in csd_df:
        csd_df[prod] -= wk1_builds[prod][0]
        csd_df[csd_df[prod] < 0] = 0
    return csd_df

#TO CHANGE
def calculate_supply(a_df, csd_df):
    """
   calculate amount of supply to allocate to superman plus.
   based on amt of material a, superman and superman mini demand and priority
   returns superman plus supply
    """
    sp_supply_df = a_df.iloc[0] - csd_df['Superman'] - csd_df['Superman Mini']
    sp_supply_df = sp_supply_df.clip(lower=0)
    s_sm_supply_df = a_df.iloc[0] - sp_supply_df
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
    #read csv data into df
    csd_df = csv_to_df(csv_path, 'Demand FCT', transpose=True) #cumulative demand for all 3 programs
    wk1_builds = csv_to_df(csv_path, 'Wk1 Builds') #builds at week 2
    cpd_df = csv_to_df(csv_path, 'plus_demand', transpose=True) #cumulative demand for all venders of plus

    #find amt of material/protect TOCHANGE  find it at the given week instead
    total_material = a_df.iloc[0, -1] 
    total_protect = 0
    for date,prod,qty in protect_list:
        total_protect += qty
        
    #create cumulative protect_df
    protect_df = create_protect_df(cpd_df.index, protect_list)
    
    #make sure total protect is not greater than total material, update protect to reflect any lowered values
    total_protect, protect_list = adjust_protect(total_material, total_protect, protect_list)

    csd_df = adjust_csd(csd_df, wk1_builds)

    #supply available for superman plus after fulfilling superman and superman mini
    sp_supply_df, s_sm_supply_df = calculate_supply(a_df, csd_df)

    #allocate for superman and superman mini
    s_sm_allocation = allocate_supply(csd_df[['Superman', 'Superman Mini']],s_sm_supply_df,protect_list)

    sp_supply_df = add_wk1_builds(sp_supply_df, wk1_builds, "Superman Plus")
    sp_allocation = allocate_supply(cpd_df, sp_supply_df, protect_list)

    #allocate superman plus
    sp_allocation = allocate_supply(cpd_df,sp_supply_df,protect_list)
    print(sp_allocation)

    total_allocation = pd.concat([s_sm_allocation, sp_allocation], axis=1)
    total_allocation.reset_index(inplace=True)
    total_allocation.rename(columns={'index': 'Weeks'}, inplace=True)

    return total_allocation
a_df = csv_to_df(csv_path, 'Material A supply') # amount of supply


print(a_df)
allocate(a_df, protect_list)