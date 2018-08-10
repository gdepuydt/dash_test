import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.figure_factory as ff
import dash_table_experiments as dt

app  = dash.Dash()
df = pd.read_csv('D:\\Python Projects\\Dash_test\\data\\data.csv', sep = ';')

app.layout = html.Div([
    dt.DataTable(
        rows=df.to_dict('records')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
