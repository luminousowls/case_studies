
import pandas as pd
csv_path = "./data/case2"


# #function to proportionally allocate demand given supply and demand dfs
# def allocate_supply(demand_df, supply_df,protect_list):
#     #initialize difference df for supply
#     supply_dif_df = supply_df.diff().fillna(supply_df).astype(float)
#     #initialize containers to keep track of past allocation and remaining supply
#     allocation_df = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
#     remaining_supply = 0


#     #for each week in the demand_df, update allocation_df
#     for i in range(len(demand_df.index)):
#         week = demand_df.index[i]
#         prev_week = demand_df.index[i-1] if i > 0 else None
#         #current_demand is cumulative demand - past allocation
#         current_demand = demand_df.loc[week] - (allocation_df.loc[prev_week] if prev_week is not None else 0)

#         #weekly total supply and weekly total demand (for all products)
#         weekly_supply = supply_dif_df.loc[week] + remaining_supply
#         weekly_demand = current_demand.sum()
#         if weekly_demand > 0:
#             for column in demand_df.columns:
#                 product_demand = current_demand[column]    
            
#                 to_allocate = max(weekly_supply * (product_demand / weekly_demand), 0)
#                 to_allocate = min(to_allocate, product_demand)
#                 to_allocate = round(to_allocate)
#                 allocation_df.at[week, column] = to_allocate + (allocation_df.at[prev_week, column] if prev_week else 0)
#             #remaining supply
#             remaining_supply = weekly_supply - allocation_df.loc[week].sum() 
#     return allocation_df 

#function to proportionally allocate demand given supply and demand dfs




def allocate_supply(demand_df, supply_df, protect_df):
    #initialize containers to keep track of past allocation and remaining supply
    allocation_df = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)

    for week in demand_df.index:
        weekly_supply = supply_df.loc[week]
        current_demand = demand_df.loc[week]
        weekly_demand = current_demand.sum()

        print(f"Week: {week}, Weekly Supply: {weekly_supply}, Weekly Demand: {weekly_demand}, Current Demand: {current_demand}")

        if weekly_demand > 0:
            weekly_temp = weekly_supply
            for column in demand_df.columns:
                product_demand = current_demand[column]
                to_allocate = max(weekly_supply * (product_demand / weekly_demand), 0)
                print('max',to_allocate)
                to_allocate = min(to_allocate, product_demand)
                print('min',to_allocate,product_demand)
                to_allocate = round(to_allocate)
                allocation_df.at[week, column] = to_allocate

                weekly_temp -= to_allocate
                
            weekly_supply = weekly_temp
            
           
        if week != demand_df.index[0]:
            for column in demand_df.columns:
                if allocation_df.at[week, column] < allocation_df.at[demand_df.index[demand_df.index.get_loc(week)-1], column]:
                    allocation_df.at[week, column] = allocation_df.at[demand_df.index[demand_df.index.get_loc(week)-1], column]

    print(allocation_df)
    return allocation_df
