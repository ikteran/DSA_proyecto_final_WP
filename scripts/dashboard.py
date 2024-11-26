import dash
from dash import html, dcc
import folium
from folium.plugins import HeatMap
from scripts.countryCoordinates import country_coordinates as coords
import plotly.express as px
import pandas as pd
from dash import html, dcc

def initialize_app():
    app = dash.Dash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        assets_folder='../assets/'
    )
    app.title = "Dashboard de Arribos de Barcos"
    app.config.suppress_callback_exceptions = True
    return app

def generate_control_card(data):
    ship_list=data['Ship Name'].sort_values().unique()
    return html.Div(
        id="control-card",
        children=[
            html.P("Seleccionar un barco:"),
            dcc.Dropdown(
                id="dropdown-Ship-Name",
                options=ship_list
            ),
            html.Br(),
        ]
    )

def plot_heatmap(data,ShipName=None, country_coordinates=coords):
    if ShipName!=None:
        data=data[data['Ship Name']==ShipName] 
    country = data['Country'].value_counts()

    # Crear el mapa base centrado en el mundo
    world_map = folium.Map(location=[20, 0], zoom_start=2)

    # Crear una lista para almacenar las coordenadas y las frecuencias (para el HeatMap)
    heat_data = []

    # Recorrer las filas de la frecuencia de países y agregar los puntos con la frecuencia (intensidad)
    for country, count in country.items():
        if country in country_coordinates:
            # Agregar la coordenada y la frecuencia (count) como intensidad
            heat_data.append([country_coordinates[country][0], country_coordinates[country][1], count])

    # Crear el HeatMap y agregarlo al mapa
    HeatMap(heat_data).add_to(world_map)

    # Retornar el mapa en formato HTML
    return world_map._repr_html_()

def plot_time_in_port(data, ShipName=None, predicted_location=None):
    # Filtrar datos para el histograma
    filtered_data = data[(data['Ship Name'] == ShipName) 
                         & (data['Location'] == predicted_location)
                         & (data['Duration'] <= 30)]

    # Crear histograma del tiempo pasado en los puertos
    fig = px.histogram(
        filtered_data,
        x="Duration",
        color="Location",
        nbins=10,
        title=f"Histograma del tiempo en puerto del barco: {ShipName}",
        labels={"Duration": "Tiempo en el puerto (dias)", "Location": "Puerto"},
        barmode='group'
    )

    fig.update_layout(
        xaxis_title="Tiempo en el Puerto (dias)",
        yaxis_title="Frecuencia",
        legend_title="Puerto",
        title_font=dict(size=15, color='white'),
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        bargap=0.2
    )

    return fig

def plot_time_bw_arrives(data, ShipName=None, predicted_location=None):
    # Filtrar datos para el histograma
    data['Arrival'] = pd.to_datetime(data['Arrival'])
    data['Year'] = data['Arrival'].dt.year

    filtered_data = data[(data['Ship Name'] == ShipName)
                         & (data['Location'] == predicted_location)
                         & (data['Duration'] <= 30)]
                         
    # Crear histograma del tiempo pasado en los puertos, segmentado por año
    fig = px.histogram(
        filtered_data,
        x="Year",
        y="Duration",
        color="Location",
        nbins=len(filtered_data['Year'].unique()),  # Un bin por cada año único
        title=f"Histograma del tiempo en puerto por año" + (f" para el barco: {ShipName}" if ShipName else " (todos los barcos)"),
        labels={"Year": "Año", "Duration": "Tiempo en el puerto (días)", "Location": "Puerto"},
        barmode='group'
    )

    # Actualizar el diseño del gráfico
    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Duración acumulada en el Puerto (días)",
        legend_title="Puerto",
        title_font=dict(size=15, color='white'),
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente para paper
        plot_bgcolor='rgba(0,0,0,0)',   # Fondo transparente para plot
        bargap=0.2,
        xaxis=dict(
            tickmode='array',  # Definir el modo de los ticks
            tickvals=filtered_data['Year'].unique(),  # Solo los valores únicos de año
            ticktext=[str(year) for year in filtered_data['Year'].unique()],  # Mostrar solo los años como etiquetas
        ),
    )

    # Ajuste de los ejes para mejorar la visibilidad en modo oscuro
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='gray', zerolinecolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='gray', zerolinecolor='gray')

    return fig

def plot_time_bw_arrives_day(data, ShipName=None, predicted_location=None):
    # Filtrar datos para el gráfico de líneas
    data['Arrival'] = pd.to_datetime(data['Arrival'])
    data['DayOfWeek'] = data['Arrival'].dt.day_name()  # Extraer el nombre del día de la semana (Lunes, Martes, etc.)

    filtered_data = data[(data['Ship Name'] == ShipName)
                         & (data['Location'] == predicted_location)
                         ]
    
    # Agrupar los datos por día de la semana y calcular la media de la duración
    grouped_data = filtered_data.groupby('DayOfWeek')['Duration'].mean().reset_index()

    # Ordenar los días de la semana para que aparezcan de Lunes a Domingo
    grouped_data['DayOfWeek'] = pd.Categorical(grouped_data['DayOfWeek'], 
                                                categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
                                                ordered=True)
    
    # Crear gráfico de líneas
    fig = px.line(
        grouped_data,
        x="DayOfWeek",
        y="Duration",
        title=f"Promedio del tiempo en puerto por día de la semana" + (f" para el barco: {ShipName}" if ShipName else " (todos los barcos)"),
        labels={"DayOfWeek": "Día de la semana", "Duration": "Duración promedio en el puerto (días)"},
    )

    # Actualizar el diseño del gráfico
    fig.update_layout(
        xaxis_title="Día de la semana",
        yaxis_title="Duración promedio en el Puerto (días)",
        title_font=dict(size=15, color='white'),
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente para paper
        plot_bgcolor='rgba(0,0,0,0)',   # Fondo transparente para plot
    )

    # Ajuste de los ejes para mejorar la visibilidad en modo oscuro
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='gray', zerolinecolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='gray', zerolinecolor='gray')

    return fig

def create_histogram_container(id, title, graph_ids):
    if isinstance(graph_ids, list):
        graphs = [dcc.Graph(id=graph_id) for graph_id in graph_ids]
    else:
        graphs = [dcc.Graph(id=graph_ids)]
    
    return html.Div(
        id=id,
        children=[
            html.H4(
                title,
                style={
                    'margin': 'auto',
                    'text-align': 'center',
                    'font-size': '2.5rem',
                    'font-weight': 'bold',
                    'color': '#fff'
                }
            ),  # Título en blanco
            html.Div(
                children=graphs,
                style={
                    'display': 'flex',
                    'flex-direction': 'row',
                    'justify-content': 'space-around'
                }
            )
        ],
        style={
            'border': '2px solid #dcdcdc',
            'padding': '20px',
            'border-radius': '10px',
            'background-color': '#444',  # Fondo gris oscuro
            'margin': '20px 0',
            'box-shadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
        }
    )



