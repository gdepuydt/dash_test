import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State

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
                'data': [
                    {
                    'x': data.iloc[:,1],
                    'y': data.iloc[:,0],
                    #'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                    'name': 'Trace 1',
                    'mode': 'markers',
                    'marker': {'size': 12}

                    }
                ],
                'layout': {
                    'height' : 800
                }
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
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    
    marker = {'color': ['#0074D9']*len(dff), 'size':12}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig={
            'data': [{
                'x': dff.iloc[:,0],
                'y': dff.iloc[:,1],
                'name': 'Trace 1',
                'mode': 'markers',
                'marker': marker

            }]
    }
        
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)
