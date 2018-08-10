import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_table_experiments as dt
from dash.dependencies import Input, Output

app  = dash.Dash()
data = pd.read_csv('C:\\dev\\Python\\dash_test\\data\\data.csv', sep = ',')

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children = html.Div([
            'Drag and Drop or ',
            html.A('Select csv data file')
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
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    try:
        if 'csv' in filename:
            data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            data = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file. File type not supported?'])
    return html.Div([
        html.H1(filename),
        dt.DataTable(rows=data.to_dict('records'))
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

if __name__ == '__main__':
    app.run_server(debug=False)
