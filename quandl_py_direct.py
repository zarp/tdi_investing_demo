#v3.0 
import quandl
import pandas as pd
import datetime as dt
from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components
import os
import re
from bokeh.models import CheckboxGroup, CustomJS # for checkboxes
from bokeh.layouts import row,column, widgetbox, layout #,HBox,VBox #for checkboxes

#import quandl_MACD_online
from quandl_MACD_online import MACD
from bokeh.palettes import Spectral10
#from bokeh.palettes import RdGy10 #RdGy

from importlib import import_module

def get_quandl_API_key(): 
    return os.environ['MY_QUANDL_API_KEY']

def load_file_as_list(CURR_FILENAME):
    """
    returns file contents as a list where each line is a element of the list
    """
    inFile = open(CURR_FILENAME)
    lines = inFile.readlines()
    inFile.close()
    return lines

def write_string_to_file(CURR_FILENAME, string_to_write):
    """
    Writes a string (string_to_write) to CURR_FILENAME
    """
    inFile=open(CURR_FILENAME,'w')
    inFile.write(string_to_write)
    inFile.close()
    return None

##def get_stock_price(stock_symbol):
##    quandl.ApiConfig.api_key = get_quandl_API_key()
##    data = quandl.get("WIKI/" + stock_symbol)
##
##    col_names=list(data)
##    print('col lol=', col_names)
##    date = dt.date.today()
##    last_mo_data=data.ix[pd.datetime(date.year,date.month-1,1) : pd.datetime(date.year,date.month-1,data.index.days_in_month[-2])]
##
##    output_file(os.path.join("templates","lines.html"))
##
##    p = figure(title="Interactive stock chart", x_axis_label='Date', x_axis_type="datetime", y_axis_label='Close price, USD')
##    p.line(last_mo_data['Close'].index, last_mo_data['Close'], legend=stock_symbol, line_width=2)
##
##    script, div = components(p)
##    save(p)
##    return script, div

def get_data_series(database='BCHARTS',dataset='coinbaseUSD',column='all'):
    """ returns them as a pandas dataframe"""
    quandl.ApiConfig.api_key = get_quandl_API_key()
    #print('checking:', database + "/" + dataset)
    data = quandl.get(database + "/" + dataset)
    if column=='all':
        return data
    else:
        return pd.DataFrame(data[column])
    
def plot_data(df, y_axis_label='Closing price, USD', x_axis_label='Date'):
    """FIX THIS FOR GENERAL-PURPOSE PLOTTING"""
    #print 'ttteeest=', myind % len(col_names)
    col_names=list(df)

    p = figure(title="Interactive BTC price chart", x_axis_label=x_axis_label, x_axis_type="datetime", y_axis_label=y_axis_label)
    for myind, column in enumerate(df):
        p.line(df[column].index, df[column], legend=column, line_width=2, color=Spectral10[myind % len(col_names)] )  #color="#F0027F"
        script, div = components(p)

    save(p)
    #print('types: ', type(script),' and ', type(div))
    return script, div  

def plot_multiline_with_checkboxes(df,active_checkboxes='all'):
    """works for arbitrary number of lines"""
    col_names=list(df)
    #print 'cc=',col_names
    p = figure(title="Interactive BTC chart", x_axis_label='Date', x_axis_type="datetime", y_axis_label='BTC price, USD')
    p.legend.location = "bottom_left" #can remove this line. default = top right
    lines=[]
    for myind, column in enumerate(df): #legend=column
        #print Spectral10[df.columns.get_loc(column)]
        lines.append(   p.line(df[column].index, df[column], legend=column, line_width=2, color=Spectral10[myind % len(col_names)] )   ) #color=Spectral10[myind % len(col_names)]

    if active_checkboxes=='all':
        active=list(range(len(col_names)))
    else: #must be a list! doesn't work quite as well. for now just call this function without specifying active ones
        active=active_checkboxes
    # df.columns.get_loc("thisiscolumnname")
    checkbox = CheckboxGroup(labels=col_names, active=active, width=200) #active=list(range(len(col_names))
    #in the line above 'active' says which checkboxes are ticked off (i.e. ON) by default. e.g.  active=[0, 1] will activate by default first two checkboxes
    codestring=""
    for ind,item in enumerate(lines):
        codestring+="p"+str(ind)+".visible = " + str(ind) + " in checkbox.active;" 

    myargs=dict()
    for ind, line in enumerate(lines):
        myargs['p'+str(ind)]=lines[ind]
    myargs['checkbox']=checkbox
    checkbox.callback = CustomJS(args=myargs, lang="coffeescript", code=codestring)

    layout = row(checkbox, p)
    script, div = components(layout)

    return script, div

##def insert_html(orig_template_filename, location_to_insert, text_to_insert, output_html):
##    lines=load_file_as_list(orig_template_filename)
##    replaced_text=re.sub(location_to_insert, text_to_insert, "".join(lines))
##    write_string_to_file(output_html, replaced_text)
##    return None

def insert_htmls(orig_template_filename, locations_n_texts, output_html):
    """
    original template and output_html are strings = filenames of input and output files
    locations_n_texts is a list of tuples:
    [(str_to_be_replaced1,newstring1),(str_to_be_replaced2,newstring2), ...]
    """
    lines=load_file_as_list(orig_template_filename)
    htmltext="".join(lines)
    for item in locations_n_texts:
        location_to_insert = item[0]
        #print('loc=',location_to_insert)
        text_to_insert = item[1]
        #print('text=',text_to_insert)
        htmltext=re.sub(location_to_insert, text_to_insert, htmltext) 

    write_string_to_file(output_html, htmltext)
    return None

def insert_plot_into_html(orig_template, script, div, output_html):
    locs_n_texts=[("<!-- mpict0.*-->",bokeh_belowheaders), ("<!-- mpict1.*-->", div + script)]
    insert_htmls(orig_template, locs_n_texts, output_html)
    return None

def daily_price_comparison():
    """redo with quandl the chart you've done before with bitcoinchartsAPI """
    #data=get_data_series(database='BCHARTS',dataset='coinbaseUSD',column='Close'):
    datanames=load_file_as_list(os.path.join("data","bcharts_USD.txt")) #bcharts_USD_short.txt")
    datanames=["BCHARTS/"+x[:-1] for x in datanames]
    data=pd.DataFrame(columns=["High","Low","Weighted Price"])
    #print('datanames=',datanames)
    quandl.ApiConfig.api_key = get_quandl_API_key()

    data = quandl.get(datanames, collapse="") #monthly
    #data.to_csv('bchartsUSD_all_columns.csv', sep=',')
    
    for column in data:
        if ("High" not in column) and ("Low" not in column) and ("Weighted Price" not in column) and ("Volume (Currency)" not in column):
            data.drop([column], inplace=True, axis=1)

    data.to_csv('bchartsUSD_Highs_lows_VolInCurrency_and_weightedprices.csv', sep=',') #'baverage_allUSD_merged_daily.csv'
    print('data downloaded!')
    return data

def daily_price_plotting(): #no input if u switch to file loading
    """ a proper way is to creat a multiindex dataframe (with several subcolumns for each exchange), but """
    #p.circle([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="navy", alpha=0.5)
    from bokeh.models.widgets import Panel, Tabs
    #from bokeh.io import output_file, show #REMOVE IF ALREADY LOADED
    #from bokeh.plotting import figure #REMOVE IF ALREADY LOADED

    #bchartsUSD_Highs_lows_VolInCurrency_and_weightedprices.csv
    data=pd.read_csv(os.path.join("data",'bchartsUSD_Highs_lows_VolInCurrency_and_weightedprices.csv'))
    data.set_index(['Date'],inplace=True)
    
    data=data.tail(1) #last x rows corresponding to last x days
    
    datanames=load_file_as_list(os.path.join("data","bcharts_USD.txt")) #bcharts_USD_short.txt")
    datanames=["BCHARTS/"+x[:-1] for x in datanames]

    ydatatoplot=pd.DataFrame(index=data.index)
    xdatatoplot=pd.DataFrame(index=data.index)
    circlesizes=pd.DataFrame(index=data.index)
    labels=[]
    #print datatoplot
    for ind,column in enumerate(data):
        if "High" in column:
            dbname,dsname=column.split("/")
            exchname=dsname.split(" - ")[0]
##            print 'exch name=',exchname
            labels.append(exchname[:-3]) #:-3 to remove "USD"
##            print 'high ind=',ind, 'and its name=', column
##            print 'and its low=', data.columns[ind+1] #data.ix[:, ind+1]
            ydatatoplot[dbname+"/"+exchname+ " - High-Low"]=data[column]-data[data.columns[ind+1]]
        
        if "Weighted Price" in column:
            xdatatoplot[column]=data[column]
        if "Volume (Currency)" in column:
            circlesizes[column]=data[column]
    
    TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"
    p1 = figure(plot_width=600, plot_height=600, x_axis_label='Average daily price (weighted)',y_axis_label="Daily BTC price spread (High-Low)", tools=TOOLS)
    
    #p1.circle(xdatatoplot.values[0], ydatatoplot.values[0], size=20, color="navy", alpha=0.5) #[XVALUESLIST], [YVALUESLIST]
    from bokeh.models.sources import ColumnDataSource
    from bokeh.models import HoverTool
    from collections import OrderedDict

    source = ColumnDataSource(
    data=dict(
        x=xdatatoplot.values[0], #x=xdatatoplot.values[0],
        y=ydatatoplot.values[0], #y=ydatatoplot.values[0],
        label=labels ))
    
    import numpy as np
    circlesizes = np.ma.array(circlesizes.values[0], mask=np.isnan(circlesizes.values[0])) # Use a mask to mark the NaNs

    norm_circlesizes  = 20* circlesizes / np.max(circlesizes) # The sum function ignores the masked values.
    p1.circle('x','y',size=norm_circlesizes, color="navy", alpha=0.5, source=source) #[XVALUESLIST], [YVALUESLIST]

##    #slider stuff starts here
##    from bokeh.models.widgets import Slider
##    from bokeh.io import output_file, show, vform
##    output_file("slider.html")
##    s1 = Slider(start=0, end=10, value=1, step=1, title="Stuff") #'value' is a start value
##    s1.callback  = CustomJS(args=dict(source=source), code="""
##        var data = source.get('data');
##        var f = cb_obj.get('value')
##        x = data['x']
##        y = data['y']
##        for (i = 0; i < x.length; i++) {
##            y[i] = Math.pow(x[i], f)
##        }
##        source.trigger('change');
##    """)
##
##    ##show(vform(slider))
##    #sliders end here
    
    hover =p1.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        #("index", "$index"),
        ("(x,y)", "(@x, @y)"),
        ("exchange", "@label"),
    ])

    tab1 = Panel(child=p1, title="Comparison of different exchanges")

    
    p2 = figure(plot_width=300, plot_height=300)
    p2.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)

    tab2 = Panel(child=p2, title="dummy line") #Panel(child=p2, title="dummy line")

    tabs = Tabs(tabs=[ tab1, tab2 ])

    script, div = components(p1) #tabs or p1 depending if u need tabs
    return script, div

def plot_predictions_with_tabs(data1,data2):
    #plot_multiline_with_checkboxes(df,active_checkboxes='all')
    #print 'pred=',predictions
    
    from bokeh.models.sources import ColumnDataSource
    from bokeh.models import HoverTool
    from collections import OrderedDict
    from bokeh.models.widgets import Panel, Tabs
    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    col_names=list(data1)
    p = figure(title="Interactive BTC chart", x_axis_label='Date', x_axis_type="datetime", y_axis_label='BTC price, USD') #, toolbar_location="left"
    p.legend.location = "bottom_left" #can remove this line. default = top right
    lines=[]
    for myind, column in enumerate(data1): #legend=column
        #print Spectral10[df.columns.get_loc(column)]
        lines.append(   p.line(data1[column].index, data1[column], legend=column, line_width=2, color=Spectral10[myind % len(col_names)] )   ) #color=Spectral10[myind % len(col_names)]

    active2=list(range(len(col_names)))
    checkbox = CheckboxGroup(labels=col_names, active=active2, width=200) #active=list(range(len(col_names))
    #in the line above 'active' says which checkboxes are ticked off (i.e. ON) by default. e.g.  active=[0, 1] will activate by default first two checkboxes
    codestring=""
    for ind,item in enumerate(lines):
        codestring+="p"+str(ind)+".visible = " + str(ind) + " in checkbox.active;" 

    myargs=dict()
    for ind, line in enumerate(lines):
        myargs['p'+str(ind)]=lines[ind]
    myargs['checkbox']=checkbox
    checkbox.callback = CustomJS(args=myargs, lang="coffeescript", code=codestring)

    custom = html_proginsertable() #Custom(text='<br> &#186; Close - closing price <br> &#186; EMA - Exponential Moving Average (typically 12 day "fast"and 26 day "slow" averages are  used) <br> &#186; MACD - Moving Average Convergence Divergence <br> &#186; Close_buy - line indicating which trading decision is likely to be profitable (buy BTC if >0, sell if <0)')
    #layout=column(checkbox, p, custom) #sizing_mode='fixed' #row(checkbox, p)
    #l1=layout([[checkbox], [custom],[p]])
    #l1=column(row(checkbox),row(custom),row(p))
    l1=layout([[checkbox, p, custom]])
    tab1 = Panel(child=l1, title="MACD indicator")  
    col_names=list(data2)
    
    p2 = figure(title="Predicted price", x_axis_label='Date', x_axis_type="datetime", y_axis_label='Weighted BTC price at COINBASE exchange')
    for column in data2:
        if ' - Weighted Price' in column:
            historical_data_field=column #'BCHARTS'+'/'+exchange+'USD - Weighted Price'
    p2.line(data2.index,data2['Prediction'],legend='Prediction', line_width=2, color=Spectral10[0])
    p2.line(data2.index,data2[historical_data_field],legend='Historical data', line_width=2, color=Spectral10[7]) 
##    for myind, column in enumerate(data2):
##        p2.line(data2[column].index, data2[column], legend=column, line_width=2, color=Spectral10[myind % len(col_names)] )
    
        
##    p2 = figure(plot_width=300, plot_height=300)
##    p2.line([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], line_width=3, color="navy", alpha=0.5)

    tab2 = Panel(child=row(p2), title="ARIMA model prediction")
    tabs = Tabs(tabs=[ tab2, tab1 ])
    script, div = components(tabs) #<<<<<<<<<<<<<<
    return script, div

##def html_proginsertable(): #temp for debugging, remove later
##    print 'are we here0?'
##    from bokeh.io import show
##    from bokeh.layouts import column
##    from bokeh.models import Slider
##    from bokeh.core.properties import String, Instance
##    from bokeh.models import LayoutDOM, Slider
##
##    class Custom(LayoutDOM):
##
##        __implementation__ = open("custom.coffee").read()
##
##        text = String(default="Custom text")
##
##        slider = Instance(Slider)
##
##    slider = Slider(start=0, end=10, step=0.1, value=0, title="value")
##    print 'are we here?'
##    #custom = Custom(text="Special Slider Display", slider=slider)
##    #custom = Custom(text='<IMG WIDTH=50% STYLE="border: none;" SRC="https://s3.amazonaws.com/dataincplots/dataincubplot1_combined.png" ALT="Google trends vs BTC price">', slider=slider)
##    custom = Custom(text="fwarfawefef")
##    #layout = column(slider, custom)
##    layout = column(custom)
##    script, div = components(layout)
##    show(layout)
##    return script, div#custom #script, div

def html_proginsertable(): #temp for debugging, remove later
    from bokeh.io import show
    from bokeh.layouts import column
    from bokeh.core.properties import String, Instance
    from bokeh.models import LayoutDOM

    class Custom(LayoutDOM):
        __implementation__ = open("custom.coffee").read()
        text = String(default="Custom text")

    #custom = Custom(text='<br> &#186; Close - closing price <br> &#186; EMA - Exponential Moving Average (typically 12 day "fast"and 26 day "slow" averages are  used) <br> &#186; MACD - Moving Average Convergence Divergence <br> &#186; Close_buy - line indicating which trading decision is likely to be profitable (buy BTC if >0, sell if <0)')
    custom = Custom(text='<br> &#186; Close - closing price <br> &#186; EMA - Exponential Moving Average (typically 12 day "fast"and 26 day "slow" averages are  used) <br> &#186; MACD - Moving Average Convergence Divergence <br> &#186; Close_buy - line indicating which trading decision is likely to be profitable (buy BTC if >0, sell if <0)')
    layout = column(custom)
    script, div = components(layout)
    #show(layout)
    return custom #script, div#custom #script, div

if __name__ == "__main__":
    script, div=html_proginsertable()
    orig_template="Bokeh Plot.htm"
    output_html="derpa.html"
    locs_n_texts=[("<!-- mpict1.*-->", div + script)]
    insert_htmls(orig_template, locs_n_texts, output_html)
    #daily_price_plotting()
    #daily_price_comparison() #use for downloading for quandl only. not for live use in yer app

##    dd=get_data_series(database='BCHARTS',dataset='coinbaseUSD',column=['Open','Close','High','Low','Weighted Price'])
##    print dd
    
    #insert_plot_into_html("select_rabbit.html",'bla','blergh',"select_rabbit_matched.html")
    #insert_html("select_rabbit.html", '<!-- mpicts1.*>', "QUEQUEQUEQUE", "select_rabbit_matched.html")
    #insert_html("select_rabbit_matched.html", "QUEQUEQUEQUE", "<!-- We're done testing -->", "select_rabbit_matched.html")

##    #stock_symbol = raw_input("dummy entry: ")
##    #get_stock_price(stock_symbol)
##    data=get_data_series()
##    #print 'cols=',list(data.columns.values)
##    data=MACD(data,"Close")
##    script, div = plot_data(data)
##    insert_plot_into_html(os.path.join("templates","index.html"), script, div, os.path.join("templates","plot.html"))

#v1: basic Quandl API functionality
#v2: MACD functionality (online) for a single dataseries
#v3: switching to embedded bokeh instead of half-assing it
#v4: added plot_multiline_with_checkboxes (working correctly), daily_price_comparison, daily_price_plotting
