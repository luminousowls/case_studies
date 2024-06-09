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
    # Read cumulative superman demand fct data into df
    csd_df = pd.read_csv(csv_path+'/Demand FCT.csv')
    csd_df = csd_df.transpose()
    header = csd_df.iloc[0]
    csd_df = csd_df[1:]
    csd_df.columns = header

    # Read cumulative material fct data into df
    a_df = pd.read_csv(csv_path+'/Material A supply.csv')
    total_material = a_df.iloc[0, -1]

    # Read week 1 existing builds data into df
    wk1_builds = pd.read_csv(csv_path+'/Wk1 Builds.csv')

    # Read cumulative plus demand fct data into df
    cpd_df = pd.read_csv(csv_path+'/plus_demand.csv')
    cpd_df = cpd_df.transpose()
    header = cpd_df.iloc[0]
    cpd_df = cpd_df[1:]
    cpd_df.columns = header
    cpd_df = cpd_df.drop('Reseller Partners', axis=1)

    # Create protect_df for Superman Plus
    protect_df_plus = pd.DataFrame({'Weeks': cpd_df.index, 'Protect': [0] * len(cpd_df.index)})
    protect_df_plus = protect_df_plus.set_index('Weeks')
    for week, product, qty in protect_list_plus:
        protect_df_plus.loc[week:, 'Protect'] += qty

    # Create protect_df for Superman and Superman Mini
    protect_df_superman = pd.DataFrame({'Weeks': csd_df.index, 'Protect': [0] * len(csd_df.index)})
    protect_df_superman = protect_df_superman.set_index('Weeks')
    for week, product, qty in protect_list_superman:
        protect_df_superman.loc[week:, 'Protect'] += qty

    # Make sure total protect is not greater than total material, update protect to reflect any lowered values
    total_protect = sum(qty for _, _, qty in protect_list_plus) + sum(qty for _, _, qty in protect_list_superman)
    if total_material < total_protect:
        for i in range(len(protect_list_plus)):
            protect_list_plus[i][2] *= total_material / total_protect
        for i in range(len(protect_list_superman)):
            protect_list_superman[i][2] *= total_material / total_protect
        total_protect = total_material
        total_material = max(total_material - total_protect, 0)

    # Loop through csd_df, product by product
    for prod in csd_df:
        # Remove existing wk1builds from demand
        csd_df[prod] -= wk1_builds[prod][0]
        # Remove negative numbers
        csd_df[prod] = csd_df[prod].clip(lower=0)

    # Supply available for superman plus after fulfilling superman and superman mini
    sp_supply_df = a_df.iloc[0] - csd_df['Superman'] - csd_df['Superman Mini']
    sp_supply_df = sp_supply_df.clip(lower=0)
    
    # Supply available for superman and superman mini
    s_sm_supply_df = a_df.iloc[0] - sp_supply_df
    
    # Print statements for debugging
    print("Cumulative Superman Demand DataFrame (csd_df):")
    print(csd_df.head())
    print("\nWeek 1 Builds DataFrame (wk1_builds):")
    print(wk1_builds.head())
    print("\nSuperman Plus Supply DataFrame (sp_supply_df):")
    print(sp_supply_df.head())
    print("\nSuperman and Superman Mini Supply DataFrame (s_sm_supply_df):")
    print(s_sm_supply_df.head())
    
    # Allocate for superman and superman mini
    s_sm_allocation = allocate_supply(csd_df[['Superman', 'Superman Mini']], s_sm_supply_df, protect_list)
    
    # Add week 1 builds to superman plus supply
    for i in range(len(sp_supply_df)):
        sp_supply_df.iloc[i] += wk1_builds['Superman Plus'][0]
    
    # Allocate superman plus
    sp_allocation = allocate_supply(cpd_df, sp_supply_df, protect_list)
    print(sp_allocation)
    
    # Concatenate allocations and save to CSV
    total_allocation = pd.concat([s_sm_allocation, sp_allocation], axis=1)
    total_allocation.to_csv(csv_path + '/allocation.csv')

# Example usage
protect_list = [
    ['Jan Wk4', 'PAC', 35]
]


allocate(protect_list, 0)
