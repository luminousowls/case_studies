import pandas as pd
import numpy as np

csv_path = "./data/case2"

# Function to proportionally allocate demand given supply and demand dfs
def allocate_supply(demand_df, supply_df, protect_df):
    # Initialize difference df for supply
    supply_dif_df = supply_df.diff().fillna(supply_df).astype(float)
    # Initialize containers to keep track of past allocation and remaining supply
    allocation_df = pd.DataFrame(index=demand_df.index, columns=demand_df.columns).fillna(0)
    remaining_supply = [0] * len(demand_df)

    # For each week in the demand_df, update allocation_df
    for i in range(len(demand_df.index)):
        week = demand_df.index[i]
        prev_week = demand_df.index[i-1] if i > 0 else None

        # Current demand is cumulative demand - past allocation
        if i == 0:
            current_demand = demand_df.loc[week]
        else:
            current_demand = demand_df.loc[week] - allocation_df.loc[prev_week]

        # Weekly total supply and weekly total demand (for all products)
        weekly_supply = supply_dif_df.loc[week] + (remaining_supply[i-1] if i > 0 else 0)
        weekly_demand = current_demand.sum()

        # Determine available protection
        available_protection = protect_df.at[week, 'Protect']
        if available_protection > weekly_supply:
            # If protection is greater than supply, adjust protection and redistribute remainder
            excess_protection = available_protection - weekly_supply
            protect_df.at[week, 'Protect'] -= excess_protection
            excess_protection_per_product = excess_protection / len(demand_df.columns)
            for column in demand_df.columns:
                protect_df.at[week, column] += excess_protection_per_product

        # Allocate protected items first
        for column in demand_df.columns:
            if protect_df.at[week, column] > 0:
                allocation_df.at[week, column] = min(protect_df.at[week, column], weekly_supply)
                weekly_supply -= allocation_df.at[week, column]

        # Subtract demand from remaining supply
        weekly_supply -= current_demand.sum()

        # Allocate remaining supply proportionally
        if weekly_demand > 0:
            for column in demand_df.columns:
                if protect_df.at[week, column] == 0:  # Only allocate if not protected
                    product_demand = current_demand[column]
                    to_allocate = min(weekly_supply * (product_demand / weekly_demand), product_demand)
                    allocation_df.at[week, column] += to_allocate
                    weekly_supply -= to_allocate

        # Update remaining supply
        remaining_supply[i] = weekly_supply

    return allocation_df


protect_list_plus = [
    ['Jan Wk4', 'PAC', 35]
]

protect_list_superman = [
    ['Jan Wk4', 'Superman', 20],
    ['Jan Wk4', 'Superman Mini', 15]
]

def allocate(protect_list_plus, protect_list_superman):
    # Read demand data for Superman and Superman Mini
    csd_df = pd.read_csv(csv_path+'/Demand FCT.csv', index_col=0).transpose()
    csd_df.columns = csd_df.iloc[0]
    csd_df = csd_df[1:]

    # Read cumulative material supply data
    a_df = pd.read_csv(csv_path+'/Material A supply.csv', index_col=0).transpose()
    total_material = a_df.iloc[0, -1]

    # Read week 1 builds data
    wk1_builds = pd.read_csv(csv_path+'/Wk1 Builds.csv', index_col=0)

    # Read demand data for Superman Plus
    cpd_df = pd.read_csv(csv_path+'/plus_demand.csv', index_col=0).transpose()
    cpd_df.columns = cpd_df.iloc[0]
    cpd_df = cpd_df[1:].drop('Reseller Partners', axis=1)

    # Initialize protection dataframes
    protect_df_plus = pd.DataFrame({'Protect': [0] * len(cpd_df.index)}, index=cpd_df.index)
    protect_df_superman = pd.DataFrame({'Protect': [0] * len(csd_df.index)}, index=csd_df.index)

    for week, product, qty in protect_list_plus:
        protect_df_plus.loc[week:, 'Protect'] += qty

    for week, product, qty in protect_list_superman:
        protect_df_superman.loc[week:, 'Protect'] += qty

    # Adjust protection values if total exceeds material
    total_protect = sum(qty for _, _, qty in protect_list_plus) + sum(qty for _, _, qty in protect_list_superman)
    if total_material < total_protect:
        adjust_factor = total_material / total_protect
        for i in range(len(protect_list_plus)):
            protect_list_plus[i][2] *= adjust_factor
        for i in range(len(protect_list_superman)):
            protect_list_superman[i][2] *= adjust_factor
        total_protect = total_material

    # Deduct initial builds from demand
    csd_df['Superman'] -= wk1_builds['Superman']
    csd_df['Superman Mini'] -= wk1_builds['Superman Mini']
    csd_df = csd_df.clip(lower=0)

    # Calculate supply available for Superman Plus after fulfilling Superman and Superman Mini
    sp_supply_df = a_df - csd_df[['Superman', 'Superman Mini']].sum(axis=1).clip(lower=0)
    
    # Supply for Superman and Superman Mini
    s_sm_supply_df = a_df - sp_supply_df.clip(lower=0)

    # Allocate for Superman and Superman Mini
    s_sm_allocation = allocate_supply(csd_df[['Superman', 'Superman Mini']], s_sm_supply_df, protect_df_superman)

    # Add week 1 builds to Superman Plus supply
    for i in range(len(sp_supply_df)):
        sp_supply_df.iloc[i] += wk1_builds['Superman Plus'][0]
    
    # Allocate for Superman Plus
    sp_allocation = allocate_supply(cpd_df, sp_supply_df, protect_df_plus)

    # Concatenate allocations and save to CSV
    total_allocation = pd.concat([s_sm_allocation, sp_allocation], axis=1)
    total_allocation.to_csv(csv_path + '/allocation.csv')

    return total_allocation

protect_list = [
    ['Jan Wk4', 'PAC', 35]
]


allocate(protect_list, 0)
