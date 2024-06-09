
import pandas as pd
csv_path = "./data/case2"


#function to proportionally allocate demand given supply and demand dfs
def allocate_supply(demand_df, supply_df,protect_list):
    #initialize difference df for supply
    supply_dif_df = supply_df.diff().fillna(supply_df).astype(float)
    #initialize containers to keep track of past allocation and remaining supply
    allocation_df = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
    remaining_supply = [0] * len(demand_df)


    #pre-allocate protected demand
    protected_allocation = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
    for date, product, qty in protect_list:
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
                if (week, column) in [(p[0], p[1]) for p in protect_list]:
                    allocation_df.at[week, column] = protected_allocation.at[week, column]
                    to_allocate = 0
                else:
                    to_allocate = max(weekly_supply * (product_demand / weekly_demand), 0)
                    to_allocate = min(to_allocate, product_demand)
                    to_allocate = round(to_allocate)
                    allocation_df.at[week, column] = to_allocate + (allocation_df.at[prev_week, column] if prev_week else 0)
            #remaining supply
            remaining_supply[i] = weekly_supply - allocation_df.loc[week].sum() + protected_allocation.loc[week].sum()
    return allocation_df 

