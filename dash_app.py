import dash
import pandas as pd
import sqlite3
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output


##CREATE DATABASE

df = pd.read_csv("/Users/josh/Documents/github/josh/Datasets/songs_normalize.csv")
connection = sqlite3.connect("/Users/josh/Documents/github/josh/spotify_data.db")
cursor = connection.cursor()
conn = sqlite3.connect('your_database_name.db')


df.to_sql(
    name = 'song_metrics',
    con = connection, 
    if_exists = 'replace', 
    index = False, 
    dtype = { 
        'artist':'text', 
        'song': 'text',
        'duration_ms': 'integer',
        'explicit': 'boolean',
        'year' : 'integer',
        'popularity' :'integer',
        'danceability': 'float',
        'energy' : 'float',
        'key': 'real',
        'loudness': 'float',
        'mode':'real',
        'speechiness': 'float',
        'acousticness':'float',
        'instrumentalness':'float',
        'liveness':'float',
        'valence':'float',
        'tempo':'float',
        'genre':'float'}
)

query = 'SELECT *  FROM song_metrics WHERE genre != "set()"  '

results = pd.read_sql_query(query, connection)
results['genre'] = results['genre'].str.split(',').str[0]
grouped = results.groupby(['genre', 'year'])
mean_values = grouped[['popularity']].mean().reset_index()

# mean_values.to_json('genre_year.json', orient='records', lines=True)
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': genre, 'value': genre}
            for genre in mean_values['genre'].unique()
        ],
        value=df['genre'].unique(),  # Set default to the first category
        multi = True,
        placeholder='Select genre'
    ),
    dcc.Graph(id='scatter-plot')
])

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_scatter_plot(selected_categories):
    filtered_df = mean_values[mean_values['genre'].isin(selected_categories)]

    fig = px.scatter(
        filtered_df,
        x='year',
        y='popularity',
        color='genre',
        labels={'year': 'Year', 'popularity': 'Popularity'},
        title='Average Popularity of Genres by Year'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)



