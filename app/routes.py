from flask import Blueprint, render_template, request, jsonify, Response
import app.utils.case1
import app.utils.case2
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('main.html')

@main.route('/case1')
def page1():
    return render_template('case1.html') 

@main.route('/update_estimate', methods=['POST'])
def update_estimate():
    data = request.get_json()
    value = int(data['value'])
    img, total_sold =  app.utils.case1.predict_prices(value)
    return jsonify({'img': img, 'total_sales': total_sold})
    
 
@main.route('/case2', methods=['GET', 'POST'])
def case2():
    if request.method == 'POST':
        demand_df = pd.DataFrame(request.form.lists()).set_index(0).transpose()
        supply_df = pd.DataFrame(request.form.lists()).set_index(0).transpose()
        protect_list = request.form.getlist('protected_demand')
        
        app.utils.case2.save_data_to_csv(demand_df, supply_df, protect_list)
        return render_template('results.html', tables=[s_sm_allocation.to_html(classes='data'), sp_allocation.to_html(classes='data')], titles=s_sm_allocation.columns.values)
    else:
        demand_df, supply_df, protect_list = app.utils.case2.read_data_from_csv()
        return render_template('case2.html', demand=demand_df, supply=supply_df, protect=protect_list)

@main.route('/process', methods=['POST'])
def process():
    demand_df = pd.read_csv('demand.csv', index_col=0)
    supply_df = pd.read_csv('supply.csv', index_col=0)
    protect_df = pd.read_csv('protect.csv')
    protect_list = protect_df.values.tolist()

    s_sm_allocation, sp_allocation = app.utils.case2.process_data(demand_df, supply_df, protect_list)
    
    return render_template('results.html', tables=[s_sm_allocation.to_html(classes='data'), sp_allocation.to_html(classes='data')], titles=s_sm_allocation.columns.values)