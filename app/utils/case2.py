import pandas as pd
csv_path = "./data/case2"

#function to proportionally allocate demand given supply and demand dfs
def allocate_supply(demand_df, supply_df,protect):
    #initialize difference df for supply
    supply_dif_df = supply_df.diff().fillna(supply_df).astype(float)
    #initialize containers to keep track of past allocation and remaining supply
    allocation_df = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
    remaining_supply = [0] * len(demand_df)


    #pre-allocate protected demand
    protected_allocation = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
    for date, product, qty in protect:
        if date in demand_df.index and product in demand_df.columns:
            protected_allocation.at[date, product] = qty
   
    #for each week in the demand_df, update allocation_df
    for i in range(len(demand_df.index)):
        week = demand_df.index[i]
        prev_week = demand_df.index[i-1]
        #current_demand is cumulative demand - past allocation
        if i == 0:
            current_demand = demand_df.loc[week]
        else:
            current_demand = demand_df.loc[week] - allocation_df.loc[prev_week]

        #weekly total supply and weekly total demand (for all products)
        weekly_supply = supply_dif_df.loc[week] + remaining_supply[i]
        weekly_demand = current_demand.sum()
        if weekly_demand > 0:
            for column in demand_df.columns:
                product_demand = current_demand[column]    
                #allocate protected items from preallocated df, or, if not protected, allocate proportionally from remaining supply
                if (week, column) in [(p[0], p[1]) for p in protect]:
                    allocation_df.at[week, column] = protected_allocation.at[week, column]
                    to_allocate = 0
                else:
                    to_allocate = max(weekly_supply * (product_demand / weekly_demand), 0)
                    to_allocate = min(to_allocate, product_demand)
                    allocation_df.at[week, column] = to_allocate + (allocation_df.at[prev_week, column] if prev_week else 0)
            #remaining supply
            remaining_supply[i] = weekly_supply - allocation_df.loc[week].sum() + protected_allocation.loc[week].sum()
    return allocation_df 

def first_allocation():
    protect = [
        ['Jan Wk4', 'PAC', 35]
    ]

    total_protect = 0
    for date,prod,qty in protect:
        total_protect += qty

    #read cumulative superman demand fct data into df
    csd_df = pd.read_csv(csv_path+'/Demand FCT.csv')
    csd_df = csd_df.transpose()
    header = csd_df.iloc[0]
    csd_df = csd_df[1:]
    csd_df.columns = header
    #print(csd_df)

    #read cumulative material fct data into df
    a_df = pd.read_csv(csv_path+'/Material A supply.csv')
    total_material = a_df.iloc[0, -1]

    #make sure total protect is not greater than total material, update protect to reflect any lowered values
    if total_material < total_protect:
        for i in range(len(protect)):
            protect[i][2] *= total_material/total_protect
        total_protect = total_material


    a_df.insert(0, 'Jan Wk1', [0]*len(a_df.index)) 

    #read week 1 existing builds data into df
    wk1_builds = pd.read_csv(csv_path+'/Wk1 Builds.csv')
    #print(wk1_builds)

    #read cumulative plus demand fct data into df
    cpd_df = pd.read_csv(csv_path+'/plus_demand.csv')
    cpd_df = cpd_df.transpose()
    header = cpd_df.iloc[0]
    cpd_df = cpd_df[1:]
    cpd_df.columns = header
    cpd_df = cpd_df.drop('Reseller Partners', axis=1)

    #loop through csd_df, product by product
    for prod in csd_df:
        #first, remove existing w1builds from demand
        csd_df[prod] -=  wk1_builds[prod][0]
        #remove negative numbers
        for i in range(len(csd_df[prod])):
            if csd_df.iloc[i][prod] < 0:
                csd_df.loc[csd_df.index[i], prod] = 0



    #supply available for superman plus after fulfilling superman and superman mini
    sp_supply_df = a_df.iloc[0] - csd_df['Superman'] - csd_df['Superman Mini']
    sp_supply_df = sp_supply_df.clip(lower=0)

    #supply available for superman and superman mini
    s_sm_supply_df = a_df.iloc[0] - sp_supply_df

    #allocate for superman and superman mini
    s_sm_allocation = allocate_supply(csd_df[['Superman', 'Superman Mini']],s_sm_supply_df,protect)

    for i in range(len(sp_supply_df)):
        #add wk1 builds to superman plus supply
        sp_supply_df.iloc[i] +=  wk1_builds['Superman Plus'][0]

    #allocate superman plus
    sp_allocation = allocate_supply(cpd_df,sp_supply_df,protect)
    print(sp_allocation)

    #save demand and supply data to CSV
    csd_df.to_csv(csv_path + '/cumulative_superman_demand.csv')
    a_df.to_csv(csv_path + '/cumulative_material_supply.csv')
    sp_allocation.to_csv(csv_path + '/cumulative_superman_allocation.csv')
    s_sm_allocation.to_csv(csv_path + '/cumulative_superman_allocation.csv')
    





#function to read demand and supply data from CSV
def read_demand_and_supply():
    demand_df = pd.read_csv(csv_path + '/cumulative_superman_demand.csv', index_col=0)
    supply_df = pd.read_csv(csv_path + '/cumulative_material_supply.csv', index_col=0)
    return demand_df, supply_df