#!/usr/bin/env python3

import sys
import configparser
from datetime import datetime, timedelta

import pandas as pd

import influxdb

import dash
from dash.dependencies import Input, Output, State
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

def make_app(dbc):
    # Get first measurement for the 
    first_meas = dbclient.query('SELECT time,value FROM coretemp LIMIT 1')['coretemp']
    if len(first_meas) < 1:
        start_date = datetime.datetime(2018,11,17)
    else:
        # Assign from first index value, set nanos
        start_date = first_meas.index[0].replace(nanosecond=0).to_pydatetime()

    # get data
    df = dbclient.query('SELECT time,value FROM coretemp')["coretemp"]
    
    # assign useful column names
    df.index.name = 'time'
    df.rename(columns={'value' : 'coretemp'})

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(children="Himbeerkuchen Environment Dashboard"),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),
        html.Div([html.H3('Window start / end date:'),
	        dcc.DatePickerRange(id='datepicker-coretemp',
						        min_date_allowed = start_date,
						        max_date_allowed = datetime.today(),
						        start_date = datetime.today() - timedelta(days=1),
						        end_date = datetime.today()
	        )
        ]),
        dcc.Graph(id='graph-coretemp')
    ])

    @app.callback(Output('graph-coretemp', 'figure'),
			    [Input('datepicker-coretemp', 'start_date'), Input('datepicker-coretemp', 'end_date')])
    def update_graph(start_date, end_date):
        print("Got start date: %s" % start_date)
        print("Got end date: %s" % end_date)
        start = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end = datetime.strptime(end_date[:10], '%Y-%m-%d')

        dff = df.loc[start:end].copy()

        figure={
            'data': [go.Scatter(
                x=dff.index,
                y=dff['value'],
                name="Core Temp"
            )],
            'layout': {
                'title': "SoC Core Temperature",
                'xaxis': { 'title' : "Time" },
                'yaxis': { 'title': "Temperature [°C]" }
            }
        }

        return figure


    return app


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-c', '--config', dest='configfile',
                        action='store', type=str, default=CONFIGPATH,
                        help='Config file location')

    parser.add_argument('--sd_notify', action='store_true')

    args = parser.parse_args()

    # read config from file
    with open(args.configfile, 'rt') as configfile:
        config.read_file(configfile, source=args.configfile)

    # create database connection
    dbclient = influxdb.DataFrameClient(
        config['db']['host'],
        config.getint('db', 'port'),
        config['db']['username'],
        config['db']['password'],
        config['db']['database'])

    print("Database connection established.", file=sys.stderr)

    app = make_app(dbclient)

    app.run_server(debug=True)

