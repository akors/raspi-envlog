#!/usr/bin/env python3

import sys
import configparser
import datetime

import influxdb

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go





THISCONF = 'dashboard'
CONFIGPATH = '/etc/raspi-envlog.conf'

config = configparser.ConfigParser(interpolation=None)

# default config values

config['db'] = {
  'host': "localhost",
  'port': "8086",
  'database': "envlog",
  # 'user' : 'root',
  # 'password' : 'root'
}

with open(CONFIGPATH, 'rt') as configfile:
    # read config from file
    config.read_file(configfile, source=CONFIGPATH)
#############################


dbclient = influxdb.DataFrameClient(
    config['db']['host'],
    config.getint('db', 'port'),
    config['db']['username'],
    config['db']['password'],
    config['db']['database'])
    
print("Database connection established.", file=sys.stderr)

df = dbclient.query("select * from coretemp where time > now() - 24h")["coretemp"]


print("Received datasets with %d time points" % len(df))

###########################



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Himbeerkuchen Environment Dashboard'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),
    html.Div([html.H3('Window start / end date:'),
	    dcc.DatePickerRange(id='datepicker-coretemp',
						    min_date_allowed = datetime.datetime(2018,11,17),
						    max_date_allowed = datetime.datetime.today(),
						    start_date = datetime.datetime(2018, 11, 18),
						    end_date = datetime.datetime.today()
	    )
    ]),
    dcc.Graph(
        id='graph-coretemp',
        figure={
            'data': [go.Scatter(
                x=df.index,
                y=df['value'],
                name="Core Temp"
            )],
            'layout': {
                'title': "SoC Core Temperature",
                'xaxis': { 'title' : "Time" },
                'yaxis': { 'title': "Temperature [°C]" }
            }
        }
    )
])

if __name__ == '__main__':

    app.run_server(debug=True)

