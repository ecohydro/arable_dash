# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from Organization import Organization

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

app.config.supress_callback_exceptions = False

app.layout = html.Div(children=[
    html.H1(children='WSC Arable Mark Dashboard'),

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
