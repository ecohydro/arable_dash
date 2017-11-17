# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Organization import Organization
import plotly.graph_objs as go
from Device import VARIABLES
from random import choice
import os

Org = Organization()
devices_df = Org.devices_df

initial_device = choice(Org.Devices)
initial_name = 'A000474'
initial_variable = {
    'L0': 'PARdw',
    'L1': 'PARdw',
    'L1_hourly': 'PARdw',
    'L1_daily': 'precip'
}
initial_measure = 'L1_daily'

df = Org.device(name=initial_name).get_data(
    var_list=[initial_variable[initial_measure]],
    measure=initial_measure,
    limit=1000).dropna()

data = [go.Scatter(
            # Here we are initializing the data with a temporal x-axis.
            x=df.index,
            y=df[initial_variable[initial_measure]],
        )]


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
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', None)


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
                            value=initial_name
                        )
            ], style={'width': '30%', 'display': 'inline-block'}),  # NOQA
            html.Div([  # Dropdown selection of measure
                html.Div(children="Measure"),
                dcc.Dropdown(
                    id='Measure',
                    options=[
                        {'label': i, 'value': i} for i in VARIABLES.keys()],
                    value=initial_measure
                    )
                ], style={'width': '30%', 'display': 'inline-block'}),
            html.Div([  # Dropdown selection of device variable.
                html.Div(children='''Variable'''),
                dcc.Dropdown(id='Variable')
            ], style={'width': '30%', 'float': 'right', 'display': 'inline-block'})  # NOQA
        ]),
    ]),
    html.Div([
        dcc.Graph(
            id='mark-graph',
            figure={
                'data': data
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
    dash.dependencies.Output(
        component_id='Variable', component_property='options'
    ),
    [dash.dependencies.Input(
        component_id='Measure', component_property='value'
    )]
)
def set_variable_options(selected_measure):
    return [{'label': i, 'value': i} for i in VARIABLES[selected_measure]]


@app.callback(
    dash.dependencies.Output(
        component_id='Variable', component_property='value'),
    [dash.dependencies.Input(
        component_id='Measure', component_property='value'
    )]
)
def set_variable_value(current_measure):
        return initial_variable[current_measure]


@app.callback(
    Output(component_id='mark-graph', component_property='figure'),
    [
        Input(component_id='Device', component_property='value'),
        Input(component_id='Measure', component_property='value'),
        Input(component_id='Variable', component_property='value')
    ])
def update_mark_graph(name, measure, variable):
    # Catch cases where we've updated measure and no variable has been set yet.
    # This generally only happens on initial page load.
    if not variable:
        variable = initial_variable[measure]

    # Gather the data and update the plot.
    this_df = Org.device(name=name).get_data(
        var_list=[variable], measure=measure, limit=1000).dropna()
    this_data = [go.Scatter(
                x=this_df.index,
                y=this_df[variable]
            )]
    return {
        'data': this_data,
        'layout': go.Layout(
            title='Arable Mark {id}, {measure} data, {var}'.format(
                id=name, measure=measure, var=variable),
            xaxis={'title': 'Time'},
            yaxis={'type': 'linear', 'title': variable},
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
