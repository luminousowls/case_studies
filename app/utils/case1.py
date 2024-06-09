import base64
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

img_path = "app/static/images"
csv_path = "./data/case1"

#read 
def csv_to_df(file_path):
    df = pd.read_csv(file_path, index_col=0).transpose()
    return df

def predict_prices(current_price):
    #read princess plus data into df
    princess_df = csv_to_df(csv_path+'/princess_plus.csv')
    princess_price = 200

    #read dwarf plus data into df
    dwarf_df = csv_to_df(csv_path+'/dwarf_plus.csv')
    dwarf_price = 120

    plt.switch_backend('Agg')
    # Reset the indices inside the function
    princess_df = princess_df.reset_index(drop=True)
    dwarf_df = dwarf_df.reset_index(drop=True)
    
    superman = {}
    superman_total_sales = 0
    for region in princess_df:
        superman[region] = [0]*len(dwarf_df[region])
        for i in range(len(dwarf_df[region])):
            slope = (princess_df[region].iloc[i] - dwarf_df[region].iloc[i]) / (princess_price - dwarf_price)
            y_int = princess_df[region].iloc[i] - slope * princess_price
            superman[region][i] = max(0, current_price * slope + y_int)
            superman_total_sales += superman[region][i]
    superman_df = pd.DataFrame.from_dict(superman)

    # Set sns themes
    sns.set_theme(style="whitegrid", rc={'xtick.color': 'white', 'ytick.color': 'white', 'axes.labelcolor': 'white', 'axes.titlecolor': 'white', 'font.family': 'Courier'})
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    superman_plt = sns.lineplot(data=superman_df, palette='RdYlBu')
    superman_plt.set(xlabel='Week', ylabel='Sales', title='Superman Plus Predicted Sales')
    superman_plt.grid(False)
    plt.ylim(0, 500)
    plt.show()
    plt.savefig(img_path+"/superman.png", transparent=True)

    # Create img buffer and turn into base 64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.clf()
    superman_total_sales = int(superman_total_sales)

    return img_data, superman_total_sales

# Predict prices
predict_prices(205)
