import base64
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


img_path = "app/static/images"
csv_path = "./data/case1"
#read princess plus data into df
princess_df = pd.read_csv(csv_path+'/princess.csv')
princess_df = princess_df.transpose()
header = princess_df.iloc[0]
princess_df = princess_df[1:]
princess_df.columns = header
princess_price = 200

#read dwarf plus data into df
dwarf_df = pd.read_csv(csv_path+'/dwarf.csv')
dwarf_df = dwarf_df.transpose()
header = dwarf_df.iloc[0]
dwarf_df = dwarf_df[1:]
dwarf_df.columns = header
dwarf_price = 120

#sns themes
sns.set_theme(style = "whitegrid",rc={'xtick.color': 'white', 'ytick.color': 'white','axes.labelcolor': 'white', 'axes.titlecolor': 'white', 'font.family':  'Courier'})
princess_palette = 'rocket'
dwarf_palette = 'viridis'
fig, ax = plt.subplots(figsize=(8, 6), dpi=100) 

#lineplot
princess_plt = sns.lineplot(data=princess_df,palette=princess_palette)
princess_plt.set(xlabel='Week', ylabel='Sales', title='Princess Plus Historical Sales')
princess_plt.grid(False)
plt.ylim(0, 400)
plt.savefig(img_path+"/princess.png",transparent=True)
plt.clf()

dwarf_plt = sns.lineplot(data=dwarf_df,palette=dwarf_palette)
dwarf_plt.set(xlabel='Week', ylabel='Sales', title='Dwarf Plus Historical Sales')
dwarf_plt.grid(False)
plt.ylim(0, 400)
plt.savefig(img_path+"/dwarf.png",transparent=True)
plt.clf()


#create superman lineplot (num sales), returns name of file, total num of sales, and total income
def predict_prices(current_price):
    plt.switch_backend('Agg') 
    superman = {}
    superman_total_sales = 0
    for region in princess_df: 
        superman[region] = [0]*len(dwarf_df[region])
        for i in range(len(dwarf_df[region])):
            slope = (princess_df[region].iloc[i] - dwarf_df[region].iloc[i] )/(princess_price - dwarf_price)
            y_int = princess_df[region].iloc[i] - slope * princess_price
            superman[region][i] = max(0,current_price * slope + y_int)
            superman_total_sales += superman[region][i]
    superman_df = pd.DataFrame.from_dict(superman)

    #sns themes
    sns.set_theme(style = "whitegrid",rc={'xtick.color': 'white', 'ytick.color': 'white','axes.labelcolor': 'white', 'axes.titlecolor': 'white', 'font.family':  'Courier'})
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100) 
    superman_plt = sns.lineplot(data=superman_df,palette='RdYlBu')
    superman_plt.set(xlabel='Week', ylabel='Sales', title='Superman Plus Predicted Sales')
    superman_plt.grid(False)
    plt.ylim(0, 500)
    plt.show
    plt.savefig(img_path+"/superman.png",transparent=True)


    #create img buffer and turn into base 64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.clf()
    superman_total_sales = int(superman_total_sales)

    return img_data, superman_total_sales

predict_prices(205) 



#create remaining visualizations
# Bar Chart for Regional Sales Comparison
plt.figure(figsize=(10, 6))
sns.barplot(data=princess_df, palette=princess_palette, errorbar=None)
plt.xlabel('Region')
plt.ylabel('Total Sales')
plt.title('Princess Plus Regional Sales Comparison')
plt.savefig("app/static/images/princess_regional_sales.png", transparent=True)
plt.clf()

plt.figure(figsize=(10, 6))
sns.barplot(data=dwarf_df, palette=dwarf_palette, errorbar=None)
plt.xlabel('Region')
plt.ylabel('Total Sales')
plt.title('Dwarf Plus Regional Sales Comparison')
plt.savefig("app/static/images/dwarf_regional_sales.png", transparent=True)
plt.clf()