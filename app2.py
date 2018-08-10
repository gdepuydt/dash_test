import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash_table_experiments as dt
from textwrap import dedent as d
import json


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


app  = dash.Dash()
df = pd.read_csv('\\\\samba\\documents\\InSite\\Sites\\Data_coverage_of_hospitals.csv', sep = ';')

print(list(df.columns.values))

app.layout = html.Div([
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': df["Connection date"].tolist(),
                    'y': df["Hospital"].tolist(),
                    'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                    'name': 'Trace 1',
                    'mode': 'markers',
                    'marker': {'size': 12}
                }#,
                #{
                #    'x': [1, 2, 3, 4],
                #    'y': [9, 4, 1, 4],
                #    'text': ['w', 'x', 'y', 'z'],
                #    'customdata': ['c.w', 'c.x', 'c.y', 'c.z'],
                #    'name': 'Trace 2',
                #    'mode': 'markers',
                #    'marker': {'size': 12}
                #}
            ]
        }
    ),

    html.Div(className='row', children=[
        dt.DataTable(
            rows=df.to_dict('records')
        )
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
