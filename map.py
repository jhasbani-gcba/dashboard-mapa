import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import requests
from dash.exceptions import PreventUpdate

mapbox_access_token = 'pk.eyJ1Ijoiamhhc2JhbmkiLCJhIjoiY2szajQ5azVsMGZhZDNua29vemttNmVqMiJ9.T6WftYf3JpP6OJ3fXfeWCw'
coord = pd.read_csv('LPR_coordenadas.csv')

def get_layer(trayecto):
    layer = [dict(sourcetype="geojson",
                  source={
                      "type": "FeatureCollection",
                      "features": [
                          {
                              "type": "Feature",
                              "properties": {},
                              "geometry": {
                                  'type': 'LineString',
                                  'coordinates': trayecto
                              }
                          }
                      ]
                  },
                  type='line',
                  color='green',
                  line={'width': 3}
                  )
             ]
    return layer

#trayecto = [[-58.456535, -34.547394],[-58.459885, -34.544662],[-58.463448, -34.541351],[-58.466305, -34.53672],[-58.466183, -34.536659]]

#layer = get_layer(trayecto)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Store(id='memory'),
    html.Div([dcc.Graph(
            id = 'mapa_LPR')])

])

@app.callback(
    Output('memory','data'),
    [Input('mapa_LPR', 'clickData')],
    [State('memory', 'data')]
)
def on_click(clickData,data):
    if clickData is None:
        raise PreventUpdate

    data = data or {'origen':{},'destino':{}}
    if len(data['origen'])!=0 and len(data['destino'])!=0:
        data = {}

        data['origen'] = {'text': clickData['points'][0]['text'], 'lon': clickData['points'][0]['lon'],'lat': clickData['points'][0]['lat']}
        data['destino']={}

    elif len(data['origen'])==0:
        data['origen']={'text':clickData['points'][0]['text'], 'lon':clickData['points'][0]['lon'],'lat':clickData['points'][0]['lat']}
    elif len(data['origen']) != 0 and len(data['destino']) == 0:
        point = {'text': clickData['points'][0]['text'], 'lon': clickData['points'][0]['lon'],'lat': clickData['points'][0]['lat']}
        if point != data['origen']:
            data['destino'] = point
        else:
            None

    return data
@app.callback(
    Output('mapa_LPR', 'figure'),
    [Input('memory','modified_timestamp')],
    [State('memory', 'data')]
)
def display_route(ts,data):
    if data is None:
        layer = []
        scatter_origen = []
        scatter_destino = []
    else:
        if len(data['origen']) != 0 and len(data['destino']) == 0:
            layer = []
            scatter_origen = go.Scattermapbox(
                lat=[data['origen']['lat']],
                lon=[data['origen']['lon']],
                text=[data['origen']['text']],
                name='Origen',
                mode='markers',
                marker=dict(
                    size=10,
                    color='blue',
                    opacity=.8,
                )
            )
            scatter_destino = []
        elif len(data['origen']) != 0 and len(data['destino']) != 0:
            route = {}
            route['origen_lon'] = data['origen']['lon']
            route['origen_lat'] = data['origen']['lat']
            route['destino_lon'] = data['destino']['lon']
            route['destino_lat'] = data['destino']['lat']

            base_url = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
            url = base_url + str(route['origen_lon']) + \
                  ',' + str(route['origen_lat']) + \
                  ';' + str(route['destino_lon']) + \
                  ',' + str(route['destino_lat'])
            params = {
                'geometries': 'geojson',
                'access_token': mapbox_access_token
            }
            req = requests.get(url, params=params)
            route_json = req.json()
            coordinates = route_json['routes'][0]['geometry']['coordinates']
            layer = get_layer(coordinates)

            scatter_origen = go.Scattermapbox(
                lat=[data['origen']['lat']],
                lon=[data['origen']['lon']],
                text=[data['origen']['text']],
                name='Origen',
                mode='markers',
                marker=dict(
                    size=10,
                    color='green',
                    opacity=.8,
                ),

                    )
            scatter_destino = go.Scattermapbox(
                lat=[data['destino']['lat']],
                lon=[data['destino']['lon']],
                text=[data['destino']['text']],
                mode='markers',
                name='Destino',
                marker=dict(
                    size=10,
                    color='green',
                    opacity=.8,
                ),

            )


    # set the geo=spatial data
    data_scattermapbox = [go.Scattermapbox(
                            lat=coord['Latitud'],
                            lon=coord['Longitud'],
                            text=coord['Interseccion'],
                            mode='markers',
                            name='LPR',
                            marker=dict(
                                size=8,
                                color='red',
                                opacity=.8,
                            ),
                        ),
    ]
    if scatter_origen != [] and scatter_destino == []:
        data_scattermapbox.append(scatter_origen)
    if scatter_origen != [] and scatter_destino != []:
        data_scattermapbox.append(scatter_origen)
        data_scattermapbox.append(scatter_destino)


    # set the layout to plot
    layout = go.Layout(autosize=True,
                       mapbox=dict(accesstoken=mapbox_access_token,
                                   layers=layer,
                                   bearing=0,
                                   pitch=0,
                                   zoom=11,
                                   center=dict(lat=-34.60,
                                               lon=-58.43),
                                   style='open-street-map'),
                       width=800,
                       height=700,
                       title="Camaras LPR GCBA",
                       showlegend=False,
                       clickmode='event+select')

    fig = dict(data=data_scattermapbox, layout=layout)
    return fig

if __name__ == '__main__':
    app.run_server(host='10.78.162.120', port=8000, debug=True)