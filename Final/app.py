# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json
import plotly.figure_factory as ff


app = Dash(__name__)

# Reading in data
# NYC Open Data Motor Vehicle Collision dataset
soql_url = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
        '$select=date_extract_y(crash_date),borough,zip_code,count(collision_id),sum(number_of_persons_killed)' +\
        '&$group=date_extract_y(crash_date),borough,zip_code' +\
        '&$limit=1000' +\
        '&$offset=0').replace(' ', '%20')

# saving into df
results1 = pd.read_json(soql_url)

soql_url = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
        '$select=date_extract_y(crash_date),borough,zip_code,count(collision_id),sum(number_of_persons_killed)' +\
        '&$group=date_extract_y(crash_date),borough,zip_code' +\
        '&$limit=1000' +\
        '&$offset=1000').replace(' ', '%20')

# saving into df
results2 = pd.read_json(soql_url)

soql_url = ('https://data.cityofnewyork.us/resource/h9gi-nx95.json?' +\
        '$select=date_extract_y(crash_date),borough,zip_code,count(collision_id),sum(number_of_persons_killed)' +\
        '&$group=date_extract_y(crash_date),borough,zip_code' +\
        '&$limit=1000' +\
        '&$offset=2000').replace(' ', '%20')

# saving into df
results3 = pd.read_json(soql_url)


results = pd.concat([results1,results2,results3])


# changing column names in new df
df = pd.DataFrame()
df['crash_year'] = results['date_extract_y_crash_date']
df['borough'] = results['borough']
df['zip_code'] = results['zip_code']
df['collision_count'] = results['count_collision_id']
df['number_of_persons_killed'] = results['sum_number_of_persons_killed']



# reading in  GeoJSON file
# this file is needed to display zipcodes
# this way take a very long time to load
# with urlopen('https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/ny_new_york_zip_codes_geo.min.json') as response:
#     zipcode_data = json.load(response)

f = open('ny_new_york_zip_codes_geo.min.json')
zipcode_data = json.load(f)


# identifying the feature id to use in map 
for feature in zipcode_data['features']:
        feature['id'] = feature['properties']['ZCTA5CE10']

# creating static variables and graphs
# display df table
table_fig =  ff.create_table(df[0:10])

# variable to use for zip code plots
map_df = df.groupby('zip_code').agg(Collision = ('collision_count', np.sum),
                                                Mortalities = ('number_of_persons_killed', np.sum)        
                                                ).reset_index()

# first zip code plot to display collisions
map_col_fig = px.choropleth_mapbox(
        data_frame=map_df,
        locations='zip_code',
        geojson=zipcode_data,
        color='Collision',
        mapbox_style='open-street-map',
        zoom=10,
        height=700,
        color_continuous_scale=['green', 'blue', 'gold', 'red'],
        title='Zipcode by Collision Count',
        labels={'Collision': 'Collision Count'},
        opacity=.7,
        center={
            'lat': 40.694436,
            'lon': -73.968304
        }
        )
map_col_fig.update_geos(fitbounds='locations', visible=False)
map_col_fig.update_layout(margin={"r": 0, "l": 0, "b": 0})


# second zip code plot to display mortalities
map_mor_fig = px.choropleth_mapbox(
        data_frame=map_df,
        locations='zip_code',
        geojson=zipcode_data,
        color='Mortalities',
        mapbox_style='open-street-map',
        zoom=10,
        height=700,
        color_continuous_scale=['green', 'blue', 'gold', 'red'],
        title='Zipcode by Mortalities',
        labels={'Mortalities': 'Mortalities'},
        opacity=.7,
        center={
            'lat': 40.694436,
            'lon': -73.968304
        }
        )
map_mor_fig.update_geos(fitbounds='locations', visible=False)
map_mor_fig.update_layout(margin={"r": 0, "l": 0, "b": 0})


# drop down options
measures = ['Collision','Mortalities']


# creating layout
app.layout =  html.Div( children=[
    html.H1(
        children='NYC Motor Vehicle Collision Analysis',
        style={'textAlign': 'center'}
    ),
    html.H3(
        children='Diego Correa',
        style={'textAlign': 'center'}
    ),

    html.H3(children='Overview', 
        style={'margin' : '10px 70px 10px 20px'}
    ),
    html.Div(children='''
    
        The Motor Vehicle Collisions table contains details on incidents in NYC, captured by a
        police report (MV104-N).  This report is required to be filled out for collisions where 
        someone is injured, killed, or where there is at least $1000 worth of damage.  Each record
        in the table is an event.
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Br(),

    html.Div(children='''
    
        The goal of the analysis is to identify the zip codes by its collision counts and mortalities.
        The analysis will attempt to make a connection between the two variables on an high level and 
        over time, from 2012 - 2022.
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),
    html.Br(),


    html.Div(children='''
    
        The data sources is the Motor Vehicle Collisions - Crashes table from the NYC Open Data 
        site and a GeoJSON file used for the map plots by zip code.
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Br(),

    html.Br(),

    html.H3(
        children='Motor Vehicle Collisions - Crashes table',
        style={'margin' : '10px 70px 10px 20px'}
    ),

    html.Div([
        dcc.Graph(figure=table_fig)
    ], style={'width':'90%', 'display':'inline-block', 'margin': '0 0 0 10'}),

    html.Br(),

    html.Br(),

    html.H3(
        children='Interactive Maps, 2012 - 2022',
        style={'margin' : '10px 70px 10px 20px'}
    ) ,

    html.Br(),

    html.Div(children='''
    
        The graphs below identifies that the higest amounts of collisions and mortalities are
        in Brooklyn.  Additionally, the graph on the left shows that the areas with the 
        highest collision counts are in tourist areas. However, this does not directly correlate to the 
        mortalities of the zip code.  Moreover, the graph on the left shows that the
        areas with lowest amount of collisions are on the borders of the city.
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),
    html.Br(),

    html.Br(),

    html.Br(),

    html.Div([
        dcc.Graph(figure=map_col_fig)
    ], style={'width':'49%', 'display':'inline-block','padding':'0 20'}),

    html.Div([
        dcc.Graph(figure=map_mor_fig)
    ], style={'width':'49%', 'display':'inline-block','padding':'0 20'}),
    
    html.Br(),

    html.Br(),

    html.Br(),

    html.H3(
        children='Scatter Plot of Zip Codes over Time',
        style={'margin' : '10px 70px 10px 20px'}
    ),

    html.Br(),

    html.Div(children='''
    
        The graphs below the outliers over time by borough.  We can see that during the pandemic the collision counts decrease
        ddrasticly but the mortalities seemed to increase.

        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Div([

        html.Div([
            html.Label('Measure'),
            dcc.Dropdown(
                measures,
                'Collision',
                id='xaxis-column'
            )
        ], style={'margin' : '10px 0px 0px 70px', 'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        dcc.Graph(id='scatter_plot'),
        dcc.Slider(
        df['crash_year'].min(),
        df['crash_year'].max(),
        step=None,
        id='year--slider',
        value=df['crash_year'].min(),
        marks={str(year): str(year) for year in df['crash_year'].unique()},
        )
    ], style={'display':'inline-block','width': '100%'}),

   
    html.Br(),

    html.Br(),

    html.Br(),
    
    html.H3(
        children='Conclusion',
        style={'margin' : '10px 70px 10px 20px'}
    ),

    html.Br(),

    html.Div(children='''
        The key take aways from the analysis are the areas that have high collisions do not translate to having high mortalities
        due to veichle collisions.  Additionally, it is interesting to note that tourist areas have a high frequency of collisions 
        while the edges show to have the least.  Lastly, the pandemic reduced the total amount of accident but the mortalities 
        seem to have increased.  This adds on to the point that based on this visualization, high collision frequency does
        not directly translate to high mortalities due to collisions.
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Br(),

    html.Br(),

    html.Br(),

    html.Br(),
    
    html.Br(),
    html.H3(
        children='Sources',
        style={'margin' : '10px 70px 10px 20px'}
    ),

    html.Br(),

    html.Div(children='''
        https://github.com/OpenDataDE/State-zip-code-GeoJSON/blob/master/ny_new_york_zip_codes_geo.min.json
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Br(),

    html.Div(children='''
        https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),
    html.Br(),

    html.Div(children='''
        https://www.latimes.com/world-nation/story/2021-12-08/traffic-deaths-surged-during-covid-19-pandemic-heres-why
        ''', style={
        'margin' : '10px 70px 10px 70px'
    }),

    html.Br(),

    html.Br(),

    html.Br(),

    html.Br(),
    
    html.Br()

])

@app.callback(
    Output('scatter_plot', 'figure'),
    Input('xaxis-column', 'value'),
    Input('year--slider', 'value')
   )

def update_figure(xaxis_column,year_value):

    scatter_df = df
    scatter_df['Zip Code'] = scatter_df['zip_code'].astype('category')
    scatter_df['Collision'] = scatter_df['collision_count']
    scatter_df['Mortalities'] = scatter_df['number_of_persons_killed']
    scatter_df['Mortality Ratio'] = scatter_df['number_of_persons_killed'].div(scatter_df['collision_count'])
    scatter_df.loc[~np.isfinite(scatter_df['Mortality Ratio']), 'Mortality Ratio'] = np.nan
    scatter_df = scatter_df.dropna()

    dff = scatter_df[scatter_df['crash_year'] == year_value]

    fig = px.scatter(dff, x='Zip Code', y=xaxis_column,
                     size='Mortality Ratio', color='borough',
                     size_max=55)
    
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_layout(transition_duration=500)
    # fig.update_xaxes('nan')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

