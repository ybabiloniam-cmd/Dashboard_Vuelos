"""Dashboard interactivo de retrasos de vuelos (tarea).

Ejecutar en desarrollo:
    python dashboard.py        ->  http://127.0.0.1:8050

Ejecutar en produccion (lo hace la plataforma de despliegue):
    gunicorn dashboard:server  ->  usa el objeto WSGI `server` de este modulo
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# --------------------------------------------------------------------- datos
# Los datos viajan CON el repositorio y se leen desde la carpeta del archivo.
# NO uses rutas absolutas: en el servidor las rutas son distintas.
DATA_FILE = Path(__file__).with_name("airline_data.csv")

df = pd.read_csv(
    DATA_FILE,
    encoding="ISO-8859-1",
    # Estos campos traen ceros a la izquierda: deben leerse como texto.
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

app = Dash(__name__)

# -------------------------------------------------------------------- layout
# TODO 1: construye app.layout con:
#   * html.H1  -> el titulo del tablero
#   * dcc.Input(id="input-year", type="number", value=2010, ...)
#   * cinco dcc.Graph con estos id EXACTOS:
#       carrier-plot, weather-plot, nas-plot, security-plot, late-plot
#   * bloques html.Div con style={"display": "flex"} para ordenarlos
app.layout = html.Div(
    children=[
        html.H1(
            children="Dashboard de retrasos de vuelos",
            style={"textAlign": "center"}
        ),

        html.Div(
            children=[
                html.Label("Seleccione el año: "),
                dcc.Input(
                    id="input-year",
                    type="number",
                    value=2010,
                    placeholder="Ingrese un año"
                ),
            ],
            style={
                "textAlign": "center",
                "marginBottom": "30px"
            }
        ),

        # Primera fila
        html.Div(
            children=[
                dcc.Graph(
                    id="carrier-plot",
                    style={"width": "50%"}
                ),
                dcc.Graph(
                    id="weather-plot",
                    style={"width": "50%"}
                ),
            ],
            style={"display": "flex"}
        ),

        # Segunda fila
        html.Div(
            children=[
                dcc.Graph(
                    id="nas-plot",
                    style={"width": "50%"}
                ),
                dcc.Graph(
                    id="security-plot",
                    style={"width": "50%"}
                ),
            ],
            style={"display": "flex"}
        ),

        # Tercera fila
        html.Div(
            children=[
                dcc.Graph(
                    id="late-plot",
                    style={"width": "100%"}
                )
            ],
            style={"display": "flex"}
        ),
    ]
)


# ------------------------------------------------------------------ calculos
def compute_info(datos, entered_year):
    """Devuelve 5 tablas (una por causa de retraso) para el ano pedido.

    Cada tabla debe tener las columnas: Month, Reporting_Airline y el
    promedio de la causa correspondiente.
    """
    # TODO 2: filtra por ano y agrupa por ["Month", "Reporting_Airline"]
    #         con .mean() sobre: CarrierDelay, WeatherDelay, NASDelay,
    #         SecurityDelay y LateAircraftDelay
        # Filtrar los datos por el año seleccionado
    datos_year = datos[datos["Year"] == entered_year]

    # Retraso promedio causado por la aerolínea
    carrier = (
        datos_year
        .groupby(["Month", "Reporting_Airline"], as_index=False)["CarrierDelay"]
        .mean()
    )

    # Retraso promedio causado por el clima
    weather = (
        datos_year
        .groupby(["Month", "Reporting_Airline"], as_index=False)["WeatherDelay"]
        .mean()
    )

    # Retraso promedio causado por el sistema aéreo nacional (NAS)
    nas = (
        datos_year
        .groupby(["Month", "Reporting_Airline"], as_index=False)["NASDelay"]
        .mean()
    )

    # Retraso promedio causado por seguridad
    security = (
        datos_year
        .groupby(["Month", "Reporting_Airline"], as_index=False)["SecurityDelay"]
        .mean()
    )

    # Retraso promedio causado por llegada tardía de la aeronave
    late = (
        datos_year
        .groupby(["Month", "Reporting_Airline"], as_index=False)["LateAircraftDelay"]
        .mean()
    )

    return carrier, weather, nas, security, late


# ------------------------------------------------------------------ callback
# TODO 3: un UNICO callback que reciba el ano y devuelva las cinco figuras.
#         Recuerda: el numero de Output debe coincidir con el numero de
#         elementos que retorna la funcion, y en el mismo orden.
#
def create_empty_figures(message):
    figures = []

    for _ in range(5):
        fig = px.line()
        fig.update_layout(
            title=message,
            xaxis_title="Mes",
            yaxis_title="Retraso promedio (minutos)"
        )
        figures.append(fig)

    return figures

@app.callback(
    [
        Output("carrier-plot", "figure"),
        Output("weather-plot", "figure"),
        Output("nas-plot", "figure"),
        Output("security-plot", "figure"),
        Output("late-plot", "figure"),
    ],
    Input("input-year", "value"),
)
def get_graph(entered_year):
    if entered_year is None:
        return create_empty_figures("Ingrese un año válido")

    carrier, weather, nas, security, late = compute_info(df, entered_year)

    if carrier.empty:
        return create_empty_figures(
            f"No hay datos disponibles para {entered_year}"
        )

    carrier_fig = px.line(
        carrier,
        x="Month",
        y="CarrierDelay",
        color="Reporting_Airline",
        title=f"Retraso por transportista - {entered_year}",
        labels={
            "Month": "Mes",
            "CarrierDelay": "Retraso promedio (minutos)",
            "Reporting_Airline": "Aerolínea"
        }
    )

    weather_fig = px.line(
        weather,
        x="Month",
        y="WeatherDelay",
        color="Reporting_Airline",
        title=f"Retraso por clima - {entered_year}",
        labels={
            "Month": "Mes",
            "WeatherDelay": "Retraso promedio (minutos)",
            "Reporting_Airline": "Aerolínea"
        }
    )

    nas_fig = px.line(
        nas,
        x="Month",
        y="NASDelay",
        color="Reporting_Airline",
        title=f"Retraso por NAS - {entered_year}",
        labels={
            "Month": "Mes",
            "NASDelay": "Retraso promedio (minutos)",
            "Reporting_Airline": "Aerolínea"
        }
    )

    security_fig = px.line(
        security,
        x="Month",
        y="SecurityDelay",
        color="Reporting_Airline",
        title=f"Retraso por seguridad - {entered_year}",
        labels={
            "Month": "Mes",
            "SecurityDelay": "Retraso promedio (minutos)",
            "Reporting_Airline": "Aerolínea"
        }
    )

    late_fig = px.line(
        late,
        x="Month",
        y="LateAircraftDelay",
        color="Reporting_Airline",
        title=f"Retraso por aeronave tardía - {entered_year}",
        labels={
            "Month": "Mes",
            "LateAircraftDelay": "Retraso promedio (minutos)",
            "Reporting_Airline": "Aerolínea"
        }
    )
    return (
        carrier_fig,
        weather_fig,
        nas_fig,
        security_fig,
        late_fig
    )    
        
# --------------------------------------------------------------- produccion
# RF9: objeto WSGI que consumira gunicorn. gunicorn IMPORTA este modulo y
# busca una variable llamada `server`; nunca ejecuta el bloque __main__.
server = app.server

if __name__ == "__main__":
    # debug=True recarga el servidor al guardar: comodo en desarrollo,
    # y NUNCA se usa en produccion.
    app.run(debug=True, port=8050)



