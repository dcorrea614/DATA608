# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)


colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=spc_common,count(tree_id)' +\
        '&$group=spc_common').replace(' ', '%20')

species = pd.read_json(soql_url)


app.layout =  html.Div( children=[
    html.H1(
        children='DATA608 - HW 4',
        style={
            'textAlign': 'center'
        }
    ),

    html.Div(children='''
    
        Build a dash app for a arborist studying the health of various tree species (as defined by the
        variable ‘spc_common’) across each borough (defined by the variable ‘borough’). This
        arborist would like to answer the following two questions for each species and in each
        borough:
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),
    html.Br(),

    html.Div(children='''
        1. What proportion of trees are in good, fair, or poor health according to the ‘health’
        variable?
    ''', style={
        'margin' : '0px 0px 0px 85px'
    }),

    html.Div(children='''
        2. Are stewards (steward activity measured by the ‘steward’ variable) having an impact
        on the health of trees?
    ''', style={
        'margin' : '0px 0px 0px 85px'
    }),

    html.Br(),

    html.Div([

        html.Div([
            html.Label('Tree Species'),
            dcc.Dropdown(
                species['spc_common'].unique(),
                'black walnut',
                id='xaxis-column'
            )
        ], style={'margin' : '10px 0px 0px 70px', 'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='tree_health_plot'),
    ], style={'width':'49%', 'display':'inline-block','padding':'0 20'}),
    
    html.Div([
        dcc.Graph(id='steward_health_plot')
    ], style={'width':'49%', 'display':'inline-block','padding':'0 20'})
])


@app.callback(
    Output('tree_health_plot', 'figure'),
    Input('xaxis-column', 'value')
   )

def update_figure1(selected_species):

    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
            '$select=boroname,spc_common,health,count(tree_id)' +\
            '&$where=spc_common=\''+selected_species+'\'' +\
            '&$group=boroname,spc_common,health').replace(' ', '%20')

    df = pd.read_json(soql_url)
    df = df.astype(object).replace(np.nan, 'None')

    fig = px.bar(df, x="health", y="count_tree_id", 
                    color="boroname", 
                    title="Health of Trees by Borough",
                    category_orders={"health": ["Poor", "Fair", "Good"]}
                    )

    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output('steward_health_plot', 'figure'),
    Input('xaxis-column', 'value')
   )

def update_figure2(selected_species):

    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
            '$select=steward,health,count(tree_id)' +\
            '&$where=spc_common=\''+selected_species+'\'' +\
            '&$group=steward,health').replace(' ', '%20')

    df = pd.read_json(soql_url)
    df = df.astype(object).replace(np.nan, 'None')

    fig = px.bar(df, x="steward", y="count_tree_id",
                color='health',
                title="Steward by Health of Trees",
                    category_orders={"health": ["Poor", "Fair", "Good"],
                                    'steward':['None','1or2','3or4','4orMore']})

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

