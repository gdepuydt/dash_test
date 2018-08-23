import base64
import io
import dash
import numpy as np
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table_experiments as dt
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from datetime import datetime

app  = dash.Dash()
app.config['suppress_callback_exceptions']=True

MarkDownText1 = '''
# Reporting to pharma prototype
Please drag a demo csv file into the box below.
'''

MarkDownText2 = '''
You can have a look at some Dash examples [here](https://dash.plot.ly/gallery).
Enjoy!  
'''

app.layout = html.Div([
    html.Div([dcc.Markdown(MarkDownText1)]),
    dcc.Upload(
        id='upload-data',
        children = html.Div([
            'Drop or ',
            html.A('Select csv Data File')
        ]),
        style = {
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True  
    ),
    html.Div(id='output-data-upload'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    html.Div([dcc.Markdown(MarkDownText2)])
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            print(data.columns[0])

        elif 'xls' in filename:
            data = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file. File type not supported?'])

    hospital_connections = go.Scatter(x=data.iloc[:,1], y=data.iloc[:,0], name='', opacity =1, mode = 'markers')

    diagnose_start_dates = [datetime.strptime(dat, '%Y-%m-%d').date() for dat in data.iloc[:,2]]
    diagnose_end_dates = [datetime.strptime(dat, '%Y-%m-%d').date() for dat in data.iloc[:,3]]
    covered_diagnose_timespans = []
    for i in range (0,len(data.iloc[:,0])):
        hosp=[data.iloc[i,0],data.iloc[i,0]]
        dates=[diagnose_start_dates[i],diagnose_end_dates[i]]
        covered_diagnose_timespan = go.Scatter(x=dates, y=hosp, name='', opacity =1)
        covered_diagnose_timespans.append(covered_diagnose_timespan)
    return html.Div([
        html.H1(filename),
        dt.DataTable(
            rows=data.to_dict('records'),
            row_selectable = True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            max_rows_in_viewport = 50,
            id='datatable-hospitals'
        ),
        dcc.Graph(
            id='datagraph-hospitals',
            figure={
                'data': [hospital_connections],
                'layout': go.Layout(title='Hospital connection dates', height=800)
            }
        ),
        dcc.Graph(
            id='chart-diagnose-coverage',
            figure={
                'data': covered_diagnose_timespans,
                'layout' : go.Layout(title='Covered diagnose timespans per hospital', height=800)
            }
        )
    ])

@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename'),
               Input('upload-data', 'last_modified')])
def update_output(content, name, date):
    if content is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in zip(content, name, date)
        ]
        return children

@app.callback(
    Output('datatable-hospitals', 'selected_row_indices'),
    [Input('datagraph-hospitals', 'clickData')],
    [State('datatable-hospitals', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices

@app.callback(
    Output('datagraph-hospitals', 'figure'),
    [Input('datatable-hospitals', 'rows'),
     Input('datatable-hospitals', 'selected_row_indices')])
def update_hospital_connections_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    custom_markers = []*len(dff)
    for l in range (0, len(dff)):
        custom_markers = dict(color=['#0074D9']*len(dff), size=12)
    for i in (selected_row_indices or []):
        custom_markers['color'][i] = '#FF851B'
    hospital_connections = go.Scatter(x=dff['Connection Date'], y=dff['Site'], name='', opacity =1, mode = 'markers', marker = custom_markers)
    fig={
           'data': [hospital_connections],
           'layout': go.Layout(title='Hospital connection dates', height=800)
    }
        
    return fig


@app.callback(
    Output('chart-diagnose-coverage', 'figure'),
    [Input('datatable-hospitals', 'rows')])
def update_hospital_connections_figure(rows):
    dff = pd.DataFrame(rows)
    diagnose_start_dates = [datetime.strptime(dat, '%Y-%m-%d').date() for dat in dff['Diagnoses Start Date']]
    diagnose_end_dates = [datetime.strptime(dat, '%Y-%m-%d').date() for dat in dff['Diagnoses End Date']]
    covered_diagnose_timespans = []
    for i in range (0,len(dff.iloc[:,0])):
        hosp=[dff.loc[i,'Site'],dff.loc[i,'Site']]
        dates=[diagnose_start_dates[i],diagnose_end_dates[i]]
        covered_diagnose_timespan = go.Scatter(x=dates, y=hosp, name='', opacity =1)
        covered_diagnose_timespans.append(covered_diagnose_timespan)
    fig={
        'data': covered_diagnose_timespans,
        'layout' : go.Layout(title='Covered diagnose timespans per hospital', height=800)
    }
        
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)
