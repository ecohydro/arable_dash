# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Organization import Organization
import plotly.graph_objs as go
import numpy as np
from Device import VARIABLES

Org = Organization()
devices_df = Org.devices_df


def generate_table(dataframe, max_rows=60):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


app = dash.Dash(__name__)

app.config.supress_callback_exceptions = True

app.layout = html.Div(children=[
    html.H1(children='WSC Arable Mark Dashboard'),

    html.Div([  # Viz output for Marks
        html.Div([
            html.Div([  # Dropdown selection of device.
                html.Div(children='''Device Name'''),
                dcc.Dropdown(
                            id='Device',
                            options=[
                                {'label': x.name, 'value': x.name} for x in Org.Devices],  # NOQA
                            value='A000360'
                        )
            ], style={'width': '48%', 'display': 'inline-block'}),  # NOQA
            html.Div([  # Dropdown selection of device state.
                html.Div(children='''Variable'''),
                dcc.Dropdown(
                            id='Variable',
                            options=[
                                {'label': i, 'value': i} for i in VARIABLES['L1']],  # NOQA
                            value='Tair'
                        )
            ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})  # NOQA
        ]),
    ]),
    html.Div([
        dcc.Graph(
            id='mark-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'line', 'name':'Marky-Mark'},   # NOQA
                ],
            }
        )
    ]),

    html.Div([  # Input options for refining the device table display.
        html.Div([  # Interactive text input for ID selection
            html.Div(children='''Device Name'''),
            dcc.Input(id='Name', value='A000', type="text")
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([  # Dropdown selection of device state.
            html.Div(children='''Device State'''),
            dcc.Dropdown(
                        id='State',
                        options=[
                            {'label': i, 'value': i} for i in devices_df['state'].unique()],  # NOQA
                        value='Active'
                    )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    html.Div(id='test'),
    # Table of proposals by PI
    html.Table(id='device-table'),

])


@app.callback(
    Output(component_id='mark-graph', component_property='figure'),
    [
        Input(component_id='Device', component_property='value'),
        Input(component_id='Variable', component_property='value')
    ])
def update_mark_graph(name, variable):
    df = Org.device(name=name).get_data(var_list=[variable])
    data = [go.Scatter(
                # x=df['time'],
                x=np.arange(len(df)),
                y=df[variable],
                marker={'color': 'red', 'symbol': 104, 'size': "10"},
                mode="markers+lines"
            )]
    return {
        'data': data,
        'layout': go.Layout(
            xaxis={'type': 'linear', 'title': 'Time'},
            yaxis={'title': variable},
            # margin={'l': 40, 'b': 40, 't': 10, 'r': 1},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


@app.callback(
    Output(component_id='device-table', component_property='children'),
    [
        Input(component_id='Name', component_property='value'),
        Input(component_id='State', component_property='value')
    ]
)
def update_mark_search(name, state):
    this_df = devices_df.loc[
        (devices_df['name'].str.contains(name)) &
        (devices_df['state'] == state)]
    # this_df = devices
    # return generate_table(devices)
    return generate_table(this_df.filter(
                items=[
                    # 'firmware',
                    # 'flags',
                    # 'id',
                    'last_deploy',
                    'last_post',
                    'last_seen',
                    'location',
                    'model',
                    'name',
                    # 'reported_fw',
                    'signal_strength',
                    'state',
                    'sync_interval'
                ]
            ).sort_values(
                ['last_seen', 'signal_strength'],
                ascending=[False, False]),
    )

app.css.append_css(
   {"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


if __name__ == '__main__':
    app.run_server(debug=True)
