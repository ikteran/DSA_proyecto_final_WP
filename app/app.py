from scripts.dashboard import initialize_app, generate_control_card, plot_heatmap, plot_time_in_port, plot_time_bw_arrives, plot_time_bw_arrives_day,create_histogram_container
from scripts.ETL import load_data
from scripts.modelo import rand_class
from dash import html
from dash.dependencies import Input, Output


# Inicializar la aplicación
app = initialize_app()
server = app.server

# Cargar datos
datasource='./data/RTOP.csv'
data=load_data(datasource)
# Uso de la función con el dataset df_clean
location_accuracy,location_mse,location_r2,predicted_location=rand_class(data)

# Layout de la aplicación
app.layout = html.Div(
    id="app-container",
    children=[
        # Encabezado optimización de llegada de barcos
        html.Div(
            children=[
                html.H1("OPTIMIZACIÓN DE LLEGADA DE BARCOS - WAYPOINT LLC", 
                        style={'font-size': '4rem', 'font-weight': 'bold', 'color': '#fff', 'text-align': 'center'})
            ],
            style={
                'background-color': '#1b8ed1',  # Fondo azul
                'padding': '30px',  # Espaciado dentro del box
                'border-radius': '8px',  # Bordes redondeados
                'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',  # Sombra sutil
                'margin-top': '40px',
                'margin-bottom': '40px',  # Margen inferior para separación
                'width': '60%',  # Ancho del cuadro (puedes ajustarlo)
                'margin-left': 'auto',  # Centrado horizontal
                'margin-right': 'auto',  # Centrado horizontal
                'text-align': 'center',  # Asegura que el texto esté centrado
            }
        ),
        
        # Encabezado principal (ya existente)
        html.Div( 
            id="header", 
            children=[ 
                html.H1("Dashboard de predicción de barcos", style={'font-size': '2.5rem', 'font-weight': 'bold', 'color': '#fff'}),  # Títulos en blanco
                html.P("A continuación, puede seleccionar el barco en el siguiente menú desplegable para predecir el posible próximo puerto al que este va a llegar.", style={'font-size': '2rem', 'color': '#ccc'}),  # Texto en gris claro
                html.Div(generate_control_card(data), style={'width': '30%', 'margin': 'auto', 'padding': '20px', 'border-radius': '8px', 'background-color': '#444'}),  # Fondo gris oscuro para el control
                html.Br(),
                html.P("El modelo predice que el próximo puerto es:", style={'font-size': '2rem', 'font-weight': 'bold', 'color': '#fff'}),  # Texto en blanco
                html.H4(id='predicted-location', style={'color':'Red', 'font-size': '3rem', 'font-weight': 'bold'}),
            ], 
            style={'width': '100%', 'textAlign': 'center', 'padding': '30px 20px', 'background-color': '#333', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)', 'color': '#fff'}  # Fondo gris oscuro para el encabezado y texto blanco
        ),
        
        # Contenedor de estadísticas (acortado)
        html.Div(
            id="stats-container",
            className="row",
            children=[
                html.Div(
                    id="left-column",
                    className="four columns",
                    children=[
                        html.H4("Estadísticas del modelo", style={'font-size': '2.5rem', 'font-weight': 'bold', 'margin-bottom': '20px', 'color': '#fff'}),  # Título en blanco
                        html.P(id="location-accuracy", style={'font-size': '2.0rem', 'color': '#ccc'}),  # Texto en gris claro
                        html.P(id="location-precision", style={'font-size': '2.0rem', 'color': '#ccc'}),  # Texto en gris claro
                        html.P(id="location-f1", style={'font-size': '2.0rem', 'color': '#ccc'}),  # Texto en gris claro
                    ],
                    style={'background-color': '#444', 'padding': '10px', 'border-radius': '10px', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}  # Fondo gris ligeramente más claro
                ),
                html.Div(
                    id="right-column",
                    className="eight columns",
                    children=[
                        html.Div(
                            id="model_map",
                            children=[
                                html.H4("Mapa de calor de arribos", style={'margin': 'auto', 'text-align': 'center', 'font-size': '2.5rem', 'font-weight': 'bold', 'color': '#fff'}),  # Título en blanco
                                html.Iframe(id="folium-map", srcDoc=plot_heatmap(data), width="100%", height="600")
                            ],
                            style={'background-color': '#444', 'padding': '20px', 'border-radius': '10px', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}  # Fondo gris ligeramente más claro
                        )
                    ],
                ),
            ],
            style={'display': 'flex', 'justify-content': 'space-between', 'padding': '10px', 'background-color': '#333', 'border-radius': '10px', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}
        ),
        
        # Línea de corte
        html.Hr(style={
            'border': 'none',
            'border-top': '2px solid #dcdcdc',
            'margin': '40px 0',
        }),

        html.H3("Información histórica del barco seleccionado en el puerto predicho", style={'font-size': '3.2rem', 'font-weight': 'bold', 'color': '#1b8ed1', 'text-align': 'center'}),


        # Crear los contenedores de histogramas
        create_histogram_container(
            id="histogram-container",
            title="Histograma de tiempo en puerto predicho",
            graph_ids=["histogram-port-time"]
        ),

        create_histogram_container(
            id="histogram-by-year-container",
            title="Histograma del tiempo en puerto periodos",
            graph_ids=["histogram-port-time-by-year","histogram-by-day-container"]
        )
    ],
)



# Callback para actualizar la gráfica
@app.callback([
        Output("folium-map", "srcDoc"),
        Output("predicted-location", "children"),
        Output("location-accuracy", "children"),
        Output("location-precision", "children"),
        Output("location-f1", "children"),
        Output("histogram-port-time", "figure"),
        Output("histogram-port-time-by-year", "figure"),
        Output("histogram-by-day-container", "figure")
    ],
    [
        Input("dropdown-Ship-Name", "value")
    ]
)


def update_plot(ShipName):
    if not ShipName: 
        return "", "", "", "", "", {}, {}, {}
    map_html = plot_heatmap(data,ShipName)
    predicted_location,location_accuracy,location_mse,location_r2  = rand_class(data, ShipName) 
    accuracy_text = f"Exactitud de Ubicación (Clasificación): {location_accuracy * 100:.2f}%" 
    precision_text = f"Precision de Ubicación: {location_mse:.2f}" 
    f1_text = f"f1 de Ubicación: {location_r2:.2f}"
    his_timeinport = plot_time_in_port(data, ShipName, predicted_location)
    his_timeinport_yr = plot_time_bw_arrives(data, ShipName, predicted_location)
    his_timeinport_day = plot_time_bw_arrives_day(data, ShipName, predicted_location)

    return map_html, predicted_location,accuracy_text, precision_text, f1_text, his_timeinport, his_timeinport_yr, his_timeinport_day

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
