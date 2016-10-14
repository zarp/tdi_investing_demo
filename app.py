from flask import Flask, render_template, request, redirect

from quandl_py_direct import *
from quandl_MACD_online import *
import os

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/exploratory', methods=['POST'])
def exploratory():
  return render_template('exploratory.html')
  
@app.route('/exploratory_plot', methods=['POST'])
def exploratory_plot():
    #print("expl func worked!")
    stock_symbol = request.form['exploratory_myvar'].upper()
    stock_symbol = stock_symbol + 'USD'
    #print('stock symb=', stock_symbol)
    data=get_data_series(database='BCHARTS',dataset=stock_symbol,column=['Open','Close','High','Low','Weighted Price']) #get_data_series(database='BCHARTS',dataset='coinbaseUSD',column='Close')
    script,div=plot_multiline_with_checkboxes(data) #plot_multiline_with_checkboxes(data) #plot_data(data) 
    #get_stock_price(stock_symbol)

    orig_template="exploratory.html"
    output_html="exploratory_plot.html"

    locs_n_texts=[("<!-- mpict1.*-->", div + script)]
    insert_htmls(os.path.join("templates",orig_template), locs_n_texts, os.path.join("templates",output_html))
    #insert_plot_into_html(os.path.join("templates",orig_template), script, div, os.path.join("templates",output_html))
    return render_template(output_html)

@app.route('/macd', methods=['POST']) #, methods=['POST']
def macd():
    data=get_data_series(database='BCHARTS',dataset='coinbaseUSD',column='Close')
    data=MACD(data,"Close")
    #predictions=pd.read_csv(os.path.join("data",'predictions_live.csv'))
    predictions=pd.read_csv(os.path.join("data",'predictions_ARIMA_COINBASEUSD_Weighted Price.csv')) #'predictions_ARIMA_COINBASEUSD.csv'
    predictions.set_index(['Date'], inplace=True)
    predictions.index=predictions.index.to_datetime()
    script,div= plot_predictions_with_tabs(data,predictions)

    #script,div=plot_multiline_with_checkboxes(data) #script,div=plot_data(data) #data['Close_buy']=data['Close_buy'].apply(buy_to_bull)
    orig_template="macd.html"
    output_html="macd_plot.html"

####    predictions=pd.read_csv(os.path.join("data",'predictions_live.csv'))
####    predictions.set_index(['Date'], inplace=True)
####    predictions.index=predictions.index.to_datetime()
####    div,script=plot_data(predictions)
    locs_n_texts=[("<!-- mpict1.*-->", div + script)]
    insert_htmls(os.path.join("templates",orig_template), locs_n_texts, os.path.join("templates",output_html))
    return render_template(output_html)

##@app.route('/macd', methods=['POST']) #, methods=['POST']
##def macd():
##    data=get_data_series()
##    data=MACD(data,"Close")
##    #data['Close_buy']=data['Close_buy'].apply(buy_to_bull)
##    #script,div=plot_data(data)
##    script,div=plot_multiline_with_checkboxes(data)
##    orig_template="macd.html"
##    output_html="macd_plot.html"
##    locs_n_texts=[("<!-- mpict1.*-->", div + script)]
##    insert_htmls(os.path.join("templates",orig_template), locs_n_texts, os.path.join("templates",output_html))
##    return render_template(output_html)
  

##@app.route('/macd_plot', methods=['POST'])
##def macd_plot(): # IF NO TIME - JUST PREMAKE macd_plot.html and render it
##    stock_symbol = request.form['macd_myvar'].upper()
##    print('done')
##    #get_stock_price(stock_symbol)
##
####    data=get_data_series()
####    data=MACD(data,"Close")
####    #data['Close_buy']=data['Close_buy'].apply(buy_to_bull)
####    plot_data(data)
####
##    
##    data=get_data_series()
##    data=MACD(data,"Close")
##    #data['Close_buy']=data['Close_buy'].apply(buy_to_bull)
##    plot_data(data)
##    
##    orig_template="macd.html"
##    output_html="macd_plot.html"
##    insert_plot_into_html(os.path.join("templates",orig_template), script, div, os.path.join("templates",output_html))
##    #insert_plot_into_html(os.path.join("templates",orig_template), os.path.join("templates","lines.html"), os.path.join("templates",output_html)) #must be called after get_stock_price()
##
##    return render_template(output_html)

@app.route('/misc', methods=['POST']) #, methods=['POST']
def misc():
    #data=daily_price_comparison() #if this is commented out - need to refresh datafile ('bchartsUSD_Highs_lows_VolInCurrency_and_weightedprices.csv') periodically
    ##that said, grabbing all this data in realtime is slow. will need to run a scheduler on heroku or update datafile from my machine
    script,div=daily_price_plotting()
    
    orig_template="misc.html"
    output_html="misc_plot.html"
    locs_n_texts=[("<!-- mpict1.*-->", div + script)]
    insert_htmls(os.path.join("templates",orig_template), locs_n_texts, os.path.join("templates",output_html))
    return render_template(output_html)
  
if __name__ == '__main__':
  app.config.update(TEMPLATES_AUTO_RELOAD=True)
  app.run(port=33507)
