from flask import Flask, render_template, request, jsonify, send_file
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from db_utils import get_solar_data
import base64
import io
import json
from datetime import datetime, timedelta
import math

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'solar_hydrogen_project_2024'

# Inicializar Dash
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.DARKLY])
dash_app.title = "Dashboard Solar - Proyecto Hidrógeno"

# Obtener fechas mínimas y máximas para inicializar el selector
_df_init = get_solar_data()
if not _df_init.empty and 'timestamp' in _df_init.columns:
    min_date = _df_init['timestamp'].min().date()
    max_date = _df_init['timestamp'].max().date()
else:
    # Valores por defecto si no hay datos
    min_date = datetime.now().date()
    max_date = datetime.now().date()
del _df_init

# ==================== RUTAS FLASK ====================

@app.route('/')
def home():
    """Página de inicio con resumen de métricas clave"""
    # Obtener métricas básicas
    df_recent = get_solar_data(column="slrw_avg")
    if not df_recent.empty:
        df_recent = df_recent.tail(24)  # Últimas 24 horas
        avg_irradiance = df_recent['slrw_avg'].mean()
        max_irradiance = df_recent['slrw_avg'].max()
        total_energy = df_recent['slrw_avg'].sum() * 2 * (10/60) / 1000  # kWh para panel de 2m²
    else:
        avg_irradiance = max_irradiance = total_energy = 0
    
    return render_template('home.html', 
                         avg_irradiance=avg_irradiance,
                         max_irradiance=max_irradiance,
                         total_energy=total_energy)

@app.route('/calculations')
def calculations():
    """Página de cálculos avanzados"""
    return render_template('calculations.html')

@app.route('/api/solar-efficiency', methods=['POST'])
def calculate_solar_efficiency():
    """API para cálculos de eficiencia solar"""
    data = request.get_json()
    
    # Parámetros de entrada
    irradiance = data.get('irradiance', 1000)  # W/m²
    temperature = data.get('temperature', 25)   # °C
    panel_area = data.get('panel_area', 2)     # m²
    panel_efficiency = data.get('panel_efficiency', 0.15)  # 15%
    
    # Cálculos
    # Efecto de temperatura en eficiencia (coeficiente típico: -0.4% por °C)
    temp_coefficient = -0.004
    temp_correction = 1 + temp_coefficient * (temperature - 25)
    adjusted_efficiency = panel_efficiency * temp_correction
    
    # Potencia generada
    power_watts = irradiance * panel_area * adjusted_efficiency
    
    # Energía diaria (asumiendo 5 horas de sol pico)
    daily_energy_kwh = power_watts * 5 / 1000
    
    # Ángulo óptimo (simplificado)
    optimal_angle = 90 - (23.5 * math.cos(math.radians(30)))  # Para latitud ~30°
    
    return jsonify({
        'power_watts': round(power_watts, 2),
        'daily_energy_kwh': round(daily_energy_kwh, 2),
        'adjusted_efficiency': round(adjusted_efficiency * 100, 2),
        'optimal_angle': round(optimal_angle, 1)
    })

@app.route('/api/climate-simulation', methods=['POST'])
def climate_simulation():
    """API para simulación de condiciones climáticas"""
    data = request.get_json()
    simulation_type = data.get('type', 'clear')
    
    # Simulaciones climáticas
    simulations = {
        'clear': {'irradiance': 1000, 'efficiency_factor': 1.0},
        'cloudy': {'irradiance': 400, 'efficiency_factor': 0.8},
        'rainy': {'irradiance': 200, 'efficiency_factor': 0.6},
        'optimal': {'irradiance': 1200, 'efficiency_factor': 1.1}
    }
    
    sim = simulations.get(simulation_type, simulations['clear'])
    
    # Calcular producción para diferentes escenarios
    panel_area = 2
    base_efficiency = 0.15
    
    results = {}
    for condition, params in simulations.items():
        power = params['irradiance'] * panel_area * base_efficiency * params['efficiency_factor']
        daily_energy = power * 5 / 1000
        results[condition] = {
            'power_watts': round(power, 2),
            'daily_energy_kwh': round(daily_energy, 2)
        }
    
    return jsonify(results)

@app.route('/api/trends-analysis')
def trends_analysis():
    """API para análisis de tendencias históricas"""
    # Obtener datos de los últimos 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = get_solar_data(start_date=start_date, end_date=end_date, column="slrw_avg")
    
    if df.empty:
        return jsonify({'error': 'No hay datos disponibles'})
    
    # Análisis de tendencias
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_avg = df.groupby('date')['slrw_avg'].mean().reset_index()
    
    # Calcular tendencia lineal
    x = np.arange(len(daily_avg))
    y = daily_avg['slrw_avg'].values
    slope, intercept = np.polyfit(x, y, 1)
    
    # Predicción para próximos 7 días
    future_days = np.arange(len(daily_avg), len(daily_avg) + 7)
    predictions = slope * future_days + intercept
    
    return jsonify({
        'trend_slope': round(slope, 2),
        'current_avg': round(daily_avg['slrw_avg'].iloc[-1], 2),
        'predictions': [round(p, 2) for p in predictions],
        'trend_direction': 'increasing' if slope > 0 else 'decreasing'
    })

# ==================== LAYOUT DASH ====================

dash_app.layout = dbc.Container([
    # Encabezado con navegación
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src="/assets/logo.png", height="60px", style={"marginRight": "20px"}),
                html.Div([
                    html.H1("Panel Solar - Proyecto Hidrógeno", style={"marginBottom": 0, "fontWeight": "bold"}),
                    html.H5("Dashboard de análisis y cálculo energético", style={"color": "#aaa"})
                ], style={"display": "inline-block", "verticalAlign": "middle"})
            ], style={"display": "flex", "alignItems": "center", "marginTop": "20px", "marginBottom": "20px"})
        ], width=12)
    ]),

    # Navegación
    dbc.Row([
        dbc.Col([
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Inicio", href="/", external_link=True)),
                dbc.NavItem(dbc.NavLink("Cálculos", href="/calculations", external_link=True)),
                dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard/", active=True)),
            ], pills=True, className="mb-4")
        ], width=12)
    ]),

    # Sección: Visualización general
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Visualización de Datos Solares")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Selecciona el rango de fechas"),
                            dcc.DatePickerRange(
                                id='date-range',
                                start_date=min_date,
                                end_date=max_date,
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                display_format='YYYY-MM-DD',
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Dato a visualizar"),
                            dcc.Dropdown(
                                id='data-type',
                                options=[
                                    {"label": "SlrW_Avg (W/m²)", "value": "slrw_avg"},
                                    {"label": "SlrW_2_Avg (W/m²)", "value": "slrw_2_avg"}
                                ],
                                value="slrw_avg"
                            )
                        ], width=6)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='main-graph'), width=8),
                        dbc.Col(html.Div(id='metrics-output'), width=4)
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Sección: Análisis de tendencias
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Análisis de Tendencias")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='trends-graph'), width=8),
                        dbc.Col(html.Div(id='trends-metrics'), width=4)
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Sección: Cálculo de energía solar
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Cálculo de Energía Solar (Método del Trapecio)")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Número de registros para cálculo de energía"),
                            dcc.Slider(
                                id='energy-records-slider',
                                min=50,
                                max=500,
                                step=50,
                                value=100,
                                marks={i: str(i) for i in [50, 100, 200, 300, 400, 500]},
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Área del panel (m²)"),
                            dcc.Input(
                                id='panel-area',
                                type='number',
                                value=2,
                                min=0.1,
                                max=100,
                                step=0.1,
                                style={'width': '100%'}
                            )
                        ], width=6)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='energy-graph'), width=8),
                        dbc.Col(html.Div(id='energy-metrics'), width=4)
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Sección: Simulación climática
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Simulación de Condiciones Climáticas")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Tipo de condición climática"),
                            dcc.Dropdown(
                                id='climate-simulation',
                                options=[
                                    {"label": "Cielo despejado", "value": "clear"},
                                    {"label": "Nublado", "value": "cloudy"},
                                    {"label": "Lluvioso", "value": "rainy"},
                                    {"label": "Condiciones óptimas", "value": "optimal"}
                                ],
                                value="clear"
                            )
                        ], width=6),
                        dbc.Col(html.Div(id='climate-results'), width=6)
                    ], className="mb-4"),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='climate-graph'), width=12)
                    ])
                ])
            ], className="mb-4")
        ], width=12)
    ]),

    # Sección: Tabla de datos procesados y exportación
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Datos Procesados para Cálculo de Energía", style={"display": "inline-block", "marginRight": "20px"}),
                    html.Button("Exportar a CSV", id="btn-csv", n_clicks=0, className="btn btn-primary", style={"float": "right"})
                ]),
                dbc.CardBody([
                    html.Div(id='energy-table'),
                    dcc.Download(id="download-csv")
                ])
            ])
        ], width=12)
    ])
], fluid=True)

# ==================== CALLBACKS DASH ====================

@dash_app.callback(
    [Output('main-graph', 'figure'), Output('metrics-output', 'children')],
    [Input('date-range', 'start_date'), Input('date-range', 'end_date'), Input('data-type', 'value')]
)
def update_graph_and_metrics(start_date, end_date, data_type):
    df = get_solar_data(start_date, end_date, column=data_type)
    if df.empty:
        fig = px.line()
        metrics = html.Div("No hay datos para el rango seleccionado.")
        return fig, metrics
    
    fig = px.line(df, x='timestamp', y=data_type, title=f"{data_type} en el tiempo", markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=4))
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#222", paper_bgcolor="#222", font_color="#fff")
    
    avg = df[data_type].mean()
    max_v = df[data_type].max()
    min_v = df[data_type].min()
    
    metrics = dbc.Card([
        dbc.CardBody([
            html.H5("Métricas", className="card-title"),
            html.P(f"Promedio: {avg:.2f}", className="card-text", style={"color": "#00dca0", "fontWeight": "bold"}),
            html.P(f"Máximo: {max_v:.2f}", className="card-text", style={"color": "#f39c12"}),
            html.P(f"Mínimo: {min_v:.2f}", className="card-text", style={"color": "#e74c3c"}),
        ])
    ], className="mt-3")
    return fig, metrics

@dash_app.callback(
    [Output('trends-graph', 'figure'), Output('trends-metrics', 'children')],
    [Input('date-range', 'start_date'), Input('date-range', 'end_date')]
)
def update_trends(start_date, end_date):
    df = get_solar_data(start_date, end_date, column="slrw_avg")
    if df.empty:
        fig = px.line()
        metrics = html.Div("No hay datos para análisis de tendencias.")
        return fig, metrics
    
    # Análisis de tendencias
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_avg = df.groupby('date')['slrw_avg'].mean().reset_index()
    
    fig = px.line(daily_avg, x='date', y='slrw_avg', title="Tendencia Diaria de Irradiancia")
    fig.update_traces(line=dict(width=3, color='#00dca0'))
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#222", paper_bgcolor="#222", font_color="#fff")
    
    # Calcular tendencia
    x = np.arange(len(daily_avg))
    y = daily_avg['slrw_avg'].values
    slope, intercept = np.polyfit(x, y, 1)
    
    trend_direction = "↗️ Aumentando" if slope > 0 else "↘️ Disminuyendo"
    
    metrics = dbc.Card([
        dbc.CardBody([
            html.H5("Análisis de Tendencia", className="card-title"),
            html.P(f"Dirección: {trend_direction}", className="card-text", style={"color": "#00dca0", "fontWeight": "bold"}),
            html.P(f"Pendiente: {slope:.2f} W/m²/día", className="card-text"),
            html.P(f"Promedio actual: {daily_avg['slrw_avg'].iloc[-1]:.2f} W/m²", className="card-text"),
        ])
    ], className="mt-3")
    
    return fig, metrics

@dash_app.callback(
    [Output('energy-graph', 'figure'), Output('energy-metrics', 'children'), Output('energy-table', 'children'), Output('download-csv', 'data')],
    [Input('energy-records-slider', 'value'), Input('panel-area', 'value'), Input('btn-csv', 'n_clicks')],
    [State('energy-table', 'children')]
)
def update_energy_calculation(records_limit, panel_area, n_clicks, table_children):
    ctx = dash.callback_context
    df = get_solar_data(column="slrw_avg")
    if df.empty:
        fig = px.line()
        metrics = html.Div("No hay datos disponibles para el cálculo de energía.")
        table = html.Div("No hay datos para mostrar en la tabla.")
        return fig, metrics, table, None
    
    df = df.tail(records_limit).copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["delta_horas"] = df["timestamp"].diff().dt.total_seconds() / 3600
    df["slrw_avg_shift"] = df["slrw_avg"].shift()
    df["energia_tramo_Wh"] = ((df["slrw_avg"] + df["slrw_avg_shift"]) / 2) * df["delta_horas"]
    
    energia_total_Wh = df["energia_tramo_Wh"].sum()
    energia_total_kWh = energia_total_Wh / 1000
    energia_panel_Wh = energia_total_Wh * panel_area
    energia_panel_kWh = energia_panel_Wh / 1000
    
    fig = px.line(df, x="timestamp", y="slrw_avg", title="Radiación Solar (W/m²) - Últimos Registros", markers=True)
    fig.update_traces(line=dict(width=2), marker=dict(size=4))
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), plot_bgcolor="#222", paper_bgcolor="#222", font_color="#fff")
    
    metrics = dbc.Card([
        dbc.CardBody([
            html.H5("Cálculo de Energía Solar", className="card-title"),
            html.P(f"Energía total por m²: {energia_total_Wh:.2f} Wh/m²", className="card-text", style={"color": "#00dca0", "fontWeight": "bold"}),
            html.P(f"Energía total por m²: {energia_total_kWh:.4f} kWh/m²", className="card-text"),
            html.P(f"Energía para panel de {panel_area} m²: {energia_panel_Wh:.2f} Wh", className="card-text", style={"color": "#f39c12"}),
            html.P(f"Energía para panel de {panel_area} m²: {energia_panel_kWh:.4f} kWh", className="card-text"),
            html.P(f"Registros procesados: {len(df)}", className="card-text", style={"color": "#aaa"}),
        ])
    ], className="mt-3")
    
    df_table = df.copy()
    df_table["timestamp"] = df_table["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df_table["slrw_avg"] = df_table["slrw_avg"].round(2)
    df_table["delta_horas"] = df_table["delta_horas"].round(4)
    df_table["energia_tramo_Wh"] = df_table["energia_tramo_Wh"].round(4)
    df_table = df_table.drop(columns=["slrw_avg_shift"])
    
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df_table.columns],
        data=df_table.to_dict("records"),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white'
        }
    )
    
    # Exportar a CSV
    triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    csv_data = None
    if triggered == 'btn-csv' and n_clicks > 0:
        csv_buffer = io.StringIO()
        df_table.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_data = dict(content=csv_buffer.getvalue(), filename="energia_solar.csv")
    
    return fig, metrics, table, csv_data

@dash_app.callback(
    [Output('climate-results', 'children'), Output('climate-graph', 'figure')],
    [Input('climate-simulation', 'value')]
)
def update_climate_simulation(climate_type):
    # Simulaciones climáticas
    simulations = {
        'clear': {'irradiance': 1000, 'efficiency_factor': 1.0, 'color': '#00dca0'},
        'cloudy': {'irradiance': 400, 'efficiency_factor': 0.8, 'color': '#f39c12'},
        'rainy': {'irradiance': 200, 'efficiency_factor': 0.6, 'color': '#e74c3c'},
        'optimal': {'irradiance': 1200, 'efficiency_factor': 1.1, 'color': '#9b59b6'}
    }
    
    sim = simulations.get(climate_type, simulations['clear'])
    panel_area = 2
    base_efficiency = 0.15
    
    # Calcular para todas las condiciones
    results = {}
    for condition, params in simulations.items():
        power = params['irradiance'] * panel_area * base_efficiency * params['efficiency_factor']
        daily_energy = power * 5 / 1000
        results[condition] = {
            'power_watts': round(power, 2),
            'daily_energy_kwh': round(daily_energy, 2),
            'color': params['color']
        }
    
    # Crear gráfico comparativo
    conditions = list(results.keys())
    powers = [results[c]['power_watts'] for c in conditions]
    colors = [results[c]['color'] for c in conditions]
    
    fig = go.Figure(data=[
        go.Bar(x=conditions, y=powers, marker_color=colors, name='Potencia (W)')
    ])
    fig.update_layout(
        title="Comparación de Potencia por Condición Climática",
        xaxis_title="Condición Climática",
        yaxis_title="Potencia (W)",
        plot_bgcolor="#222",
        paper_bgcolor="#222",
        font_color="#fff"
    )
    
    # Resultados para la condición seleccionada
    selected_result = results[climate_type]
    results_display = dbc.Card([
        dbc.CardBody([
            html.H5("Resultados de Simulación", className="card-title"),
            html.P(f"Potencia: {selected_result['power_watts']} W", className="card-text", style={"color": "#00dca0", "fontWeight": "bold"}),
            html.P(f"Energía diaria: {selected_result['daily_energy_kwh']} kWh", className="card-text"),
            html.P(f"Factor de eficiencia: {sim['efficiency_factor']:.1f}", className="card-text"),
        ])
    ], className="mt-3")
    
    return results_display, fig

if __name__ == '__main__':
    # Para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Para producción (Render)
    app = app
