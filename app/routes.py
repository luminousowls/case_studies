from flask import Blueprint, render_template, request, jsonify, Response, url_for, redirect
import app.utils.case1
import app.utils.case2
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('case1'))
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
def page2():
   return render_template('case2.html')

@main.route('/create-allocation', methods=['POST'])
def create_allocation():
    data = request.get_json()
    materialAsupply = data['materialAsupply']
    protected = data['protected']
    a_df = pd.DataFrame([materialAsupply], columns=['Jan Wk2', 'Jan Wk3', 'Jan Wk4', 'Jan Wk5'])

    allocation_df = app.utils.case2.allocate(a_df, protected)  # Replace with actual allocation logic

    return allocation_df.to_html(classes='data', header="true",index=False,index_names=False)