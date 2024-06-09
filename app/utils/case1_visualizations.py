import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# given csv, read into df 
def csv_to_df(file_path):
    df = pd.read_csv(file_path, index_col=0).transpose()
    return df

#create line charts using sns
def create_line_chart(df, palette, title, file_name):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    line_plot = sns.lineplot(data=df, palette=palette)
    line_plot.set(xlabel='Week', ylabel='Sales', title=title)
    line_plot.grid(False)
    plt.ylim(0, 400)
    plt.savefig(file_name, transparent=True)
    plt.clf()

#create line charts using sns
def create_bar_chart(df, palette, title, file_name):
    plt.figure(figsize=(10, 6))
    bar_plot = sns.barplot(data=df, palette=palette, errorbar=None)
    plt.xlabel('Region')
    plt.ylabel('Total Sales')
    plt.title(title)
    plt.savefig(file_name, transparent=True)
    plt.clf()

def find_monthly_average(df):
    region_means = df.mean # Compute the mean for each region
    deviations = df.sub(region_means, axis=1)  # Compute the deviations from the region mean for each week
    months = df.columns.str.split().str[0]  # Extract the month from each column name
    print("regional means", region_means)
    print("deviations", deviations)
    print("months",months)
    monthly_averages = {}

    for region in df.index:
        monthly_averages[region] = {}
        for month in df.columns:
            month_name = month.split()[0]
            if month_name not in monthly_averages[region]:
                monthly_averages[region][month_name] = []
            # Compute the monthly average of the deviations for this region and month
            monthly_average = deviations.loc[region][months == month_name].mean()
            monthly_averages[region][month_name].append(monthly_average)
    return pd.DataFrame(monthly_averages).transpose()


def create_heatmap(df, palette, title, file_name):
    plt.figure(figsize=(10, 6))
    heatmap = sns.heatmap(df, cmap=palette, annot=True, fmt=".1f", linewidths=.5)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=45)  # Rotate x-axis labels for better readability
    plt.xlabel("Month")
    plt.title(title)
    plt.savefig(file_name)




#define image and csv paths
img_path = "app/static/images"
csv_path = "./data/case1"


#read princess plus data into df
princess_df = csv_to_df(csv_path+'/princess_plus.csv')
princess_price = 200

#read dwarf plus data into df
dwarf_df = csv_to_df(csv_path+'/dwarf_plus.csv')
dwarf_price = 120

#create and save heatmaps
#find_monthly_average(princess_df)
#create_heatmap(find_monthly_average(princess_df), 'rocket', 'Princess Plus Monthly Sales', "app/static/images/princess_heatmap.png")
#create_heatmap(find_monthly_average(dwarf_df), 'viridis', 'Dwarf Plus Monthly Sales', "app/static/images/dwarf_heatmap.png")

princess_df = princess_df.reset_index()
dwarf_df = dwarf_df.reset_index()

#create and save line charts
create_line_chart(princess_df, 'rocket', 'Princess Plus Historical Sales', img_path+"/princess.png")
create_line_chart(dwarf_df, 'viridis', 'Dwarf Plus Historical Sales', img_path+"/dwarf.png")

#create and save  bar charts
create_bar_chart(princess_df, 'rocket', 'Princess Plus Regional Sales Comparison', "app/static/images/princess_regional_sales.png")
create_bar_chart(dwarf_df, 'viridis', 'Dwarf Plus Regional Sales Comparison', "app/static/images/dwarf_regional_sales.png")

