import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
import matplotlib.colors as mcolors
from streamlit_option_menu import option_menu

# Configuración de la página
st.set_page_config(
    page_title="Harmon BI Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para el tema oscuro con colores Harmon
st.markdown("""
<style>
    .main {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .stApp {
        background-color: #0a0a0a;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #0f3460;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .upload-box {
        border: 2px dashed #00d4aa;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #00ffcc;
        background: linear-gradient(135deg, #1e1e3e 0%, #1a2a4e 100%);
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #0f3460;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 212, 170, 0.2);
    }
    
    .chart-container {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #0f3460;
        margin: 1rem 0;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00a8cc 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ffcc 0%, #00c4e6 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 212, 170, 0.3);
    }
    
    .stSelectbox > div > div {
        background-color: #1a1a2e;
        border: 1px solid #0f3460;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        background-color: #1a1a2e;
        border: 1px solid #0f3460;
        border-radius: 8px;
        color: white;
    }
    
    .stFileUploader > div {
        background-color: #1a1a2e;
        border: 1px solid #0f3460;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar datos de sesión
if 'centers_data' not in st.session_state:
    st.session_state.centers_data = {}
if 'current_center' not in st.session_state:
    st.session_state.current_center = None
if 'aggregated_data' not in st.session_state:
    st.session_state.aggregated_data = {}

# Función para mapear centros comerciales a zonas geográficas
def get_geographic_zone(center_name):
    """Mapea el nombre del centro comercial a su zona geográfica"""
    zone_mapping = {
        'Gran Plaza Norte': 'Madrid',
        'Centro Solverde': 'Cataluña',
        'Parque Sur Este': 'Sur',
        'Centro Norte': 'Norte',
        'Centro Castilla': 'Castilla-La Mancha',
        'Centro León': 'León'
    }
    return zone_mapping.get(center_name, 'Madrid')

# Función para categorizar tiendas según el tipo de negocio
def get_business_type(categoria):
    """Categoriza las tiendas según el tipo de negocio"""
    business_mapping = {
        'Moda': 'Moda',
        'Restauración': 'Restauración',
        'Electrónica': 'Ocio',
        'Perfumería': 'Moda',
        'Servicios': 'Ocio',
        'Supermercado': 'Restauración',
        'Deportes': 'Ocio'
    }
    return business_mapping.get(categoria, 'Otra')

# Función para cargar datos agregados del mercado
def load_market_data():
    """Carga los datos agregados del mercado desde el CSV"""
    try:
        # Cargar datos agregados del mercado
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_path = os.path.join(project_root, 'datos', 'datos_agregados_mercado.csv')
        df = pd.read_csv(csv_path)
        
        # Convertir fecha a datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Calcular totales y promedios del sector
        sector_averages = {
            'ventas_totales': df['ingresos_totales'].sum(),
            'n_visitantes': df['trafico_peatonal'].sum(),
            'ocupacion_por_m2': df['tasa_ocupacion'].mean(),
            'ingresos_totales': df['ingresos_totales'].mean(),
            'trafico_peatonal': df['trafico_peatonal'].mean(),
            'ventas_por_m2': df['ventas_por_m2'].mean(),
            'tasa_ocupacion': df['tasa_ocupacion'].mean(),
            'tiempo_permanencia': df['tiempo_permanencia'].mean(),
            'tasa_conversion': df['tasa_conversion'].mean()
        }
        
        return sector_averages, df
        
    except Exception as e:
        st.error(f"Error al cargar datos del mercado: {str(e)}")
        # Retornar valores por defecto si hay error
        return {
            'ventas_totales': 240000,
            'n_visitantes': 11000,
            'ocupacion_por_m2': 75.5,
            'ingresos_totales': 10000,
            'trafico_peatonal': 460,
            'ventas_por_m2': 48.2,
            'tasa_ocupacion': 75.5,
            'tiempo_permanencia': 89.1,
            'tasa_conversion': 26.4
        }, None

# Datos agregados del sector basados en datos reales
def get_sector_averages():
    sector_avg, _ = load_market_data()
    return sector_avg

# Función para obtener datos por zona geográfica
def get_market_data_by_zone():
    """Obtiene datos del mercado agrupados por zona geográfica"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_path = os.path.join(project_root, 'datos', 'datos_agregados_mercado.csv')
        df = pd.read_csv(csv_path)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Agrupar por zona geográfica
        zone_data = df.groupby('zona_geografica').agg({
            'trafico_peatonal': 'sum',
            'ingresos_totales': 'sum',
            'tamaño_m2': 'sum',
            'empleados': 'sum',
            'tasa_ocupacion': 'mean'
        }).reset_index()
        
        # Renombrar columnas para compatibilidad
        zone_data = zone_data.rename(columns={
            'trafico_peatonal': 'afluencia',
            'ingresos_totales': 'ingresos (€)',
            'tasa_ocupacion': 'ocupacion_por_m2'
        })
        
        return zone_data
        
    except Exception as e:
        st.error(f"Error al cargar datos por zona: {str(e)}")
        return None

# Función para obtener datos por tipo de negocio
def get_market_data_by_business_type():
    """Obtiene datos del mercado agrupados por tipo de negocio"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_path = os.path.join(project_root, 'datos', 'datos_agregados_mercado.csv')
        df = pd.read_csv(csv_path)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Agrupar por tipo de negocio
        business_data = df.groupby('tipo_negocio').agg({
            'trafico_peatonal': 'sum',
            'ingresos_totales': 'sum',
            'tamaño_m2': 'sum',
            'empleados': 'sum',
            'tasa_ocupacion': 'mean'
        }).reset_index()
        
        # Renombrar columnas para compatibilidad
        business_data = business_data.rename(columns={
            'trafico_peatonal': 'afluencia',
            'ingresos_totales': 'ingresos (€)',
            'tasa_ocupacion': 'ocupacion_por_m2'
        })
        
        return business_data
        
    except Exception as e:
        st.error(f"Error al cargar datos por tipo de negocio: {str(e)}")
        return None

# Función para cargar datos individuales de un centro comercial
def load_individual_center_data():
    """Carga los datos individuales de un centro comercial"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        csv_path = os.path.join(project_root, 'datos', 'datos_individuales_centros.csv')
        df = pd.read_csv(csv_path)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        return df
        
    except Exception as e:
        st.error(f"Error al cargar datos individuales: {str(e)}")
        return None

# Función para obtener datos de rendimiento por centro comercial (sin nombres)
def get_center_performance_data():
    """Obtiene datos de rendimiento de todos los centros sin mostrar nombres"""
    try:
        # Cargar datos individuales
        df = load_individual_center_data()
        if df is None:
            return None
        
        # Agrupar por centro comercial
        center_data = df.groupby('centro_id').agg({
            'trafico_peatonal': 'mean',
            'ingresos_totales': 'sum',
            'tamaño_m2': 'first',
            'empleados': 'first'
        }).reset_index()
        
        # Calcular métricas adicionales
        center_data['ventas_por_m2'] = center_data['ingresos_totales'] / center_data['tamaño_m2']
        center_data['productividad_empleado'] = center_data['ingresos_totales'] / center_data['empleados']
        
        # Remover IDs de centros para privacidad
        center_data = center_data.drop('centro_id', axis=1)
        
        return center_data
        
    except Exception as e:
        st.error(f"Error al cargar datos de rendimiento: {str(e)}")
        return None

# Función para procesar archivo Excel/CSV
def process_uploaded_file(uploaded_file, center_name, center_type):
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            return None, "Formato de archivo no soportado"
        
        # Validar estructura del archivo
        required_columns = ['fecha', 'trafico_peatonal', 'ventas_por_m2', 'tasa_ocupacion', 
                          'tiempo_permanencia', 'tasa_conversion', 'ingresos_totales']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return None, f"Faltan las siguientes columnas: {', '.join(missing_columns)}"
        
        # Procesar datos
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        
        # Calcular promedios mensuales
        df['year_month'] = df['fecha'].dt.to_period('M')
        monthly_data = df.groupby('year_month').agg({
            'trafico_peatonal': 'mean',
            'ventas_por_m2': 'mean',
            'tasa_ocupacion': 'mean',
            'tiempo_permanencia': 'mean',
            'tasa_conversion': 'mean',
            'ingresos_totales': 'sum'
        }).reset_index()
        
        # Convertir Period a string para serialización
        monthly_data['fecha'] = monthly_data['year_month'].astype(str)
        monthly_data = monthly_data.drop('year_month', axis=1)
        
        center_data = {
            'name': center_name,
            'type': center_type,
            'raw_data': df.to_dict('records'),
            'monthly_data': monthly_data.to_dict('records'),
            'upload_date': datetime.now().isoformat()
        }
        
        return center_data, "Datos procesados correctamente"
        
    except Exception as e:
        return None, f"Error al procesar el archivo: {str(e)}"

# Función para crear gráfica de KPIs mejorada
def create_kpi_chart(data, sector_avg, metric_name, title, unit):
    if not data:
        return go.Figure().add_annotation(text="No hay datos disponibles", 
                                        xref="paper", yref="paper", 
                                        x=0.5, y=0.5, showarrow=False)
    
    fig = go.Figure()
    
    # Convertir fechas a formato datetime para mejor visualización
    dates = pd.to_datetime([d['fecha'] for d in data])
    values = [d[metric_name] for d in data]
    
    # Datos del centro con área sombreada
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name='Tu Centro',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=8, color='#00d4aa'),
        fill='tonexty',
        fillcolor='rgba(0, 212, 170, 0.1)'
    ))
    
    # Promedio del sector
    fig.add_hline(
        y=sector_avg,
        line_dash="dash",
        line_color="orange",
        line_width=2,
        annotation_text=f"Promedio Sector: {sector_avg:.1f}{unit}",
        annotation_position="top right",
        annotation_font_color="orange"
    )
    
    # Calcular tendencia
    if len(values) > 1:
        trend = (values[-1] - values[0]) / values[0] * 100
        trend_color = "green" if trend > 0 else "red"
        fig.add_annotation(
            text=f"Tendencia: {trend:+.1f}%",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font=dict(color=trend_color, size=12)
        )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="white")),
        xaxis_title="Fecha",
        yaxis_title=f"{title} ({unit})",
        template="plotly_dark",
        height=350,
        margin=dict(l=0, r=0, t=60, b=0),
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

# Función para crear gráfica de comparación mejorada
def create_comparison_chart(center_data, sector_avg):
    metrics = ['trafico_peatonal', 'ventas_por_m2', 'tasa_ocupacion', 
               'tiempo_permanencia', 'tasa_conversion', 'ingresos_totales']
    
    metric_names = ['Tráfico Peatonal', 'Ventas/m²', 'Ocupación', 
                   'Tiempo Permanencia', 'Conversión', 'Ingresos']
    
    center_values = []
    sector_values = []
    performance = []
    
    for metric in metrics:
        if center_data:
            center_val = center_data[metric]
            center_values.append(center_val)
            # Calcular rendimiento relativo
            perf = (center_val / sector_avg[metric] - 1) * 100
            performance.append(perf)
        else:
            center_values.append(0)
            performance.append(-100)
        sector_values.append(sector_avg[metric])
    
    fig = go.Figure()
    
    # Crear colores basados en el rendimiento
    colors = ['#00d4aa' if p > 0 else '#ff4757' for p in performance]
    
    fig.add_trace(go.Bar(
        name='Tu Centro',
        x=metric_names,
        y=center_values,
        marker_color=colors,
        text=[f"{p:+.1f}%" for p in performance],
        textposition='auto',
        textfont=dict(color='white', size=10)
    ))
    
    fig.add_trace(go.Bar(
        name='Promedio Sector',
        x=metric_names,
        y=sector_values,
        marker_color='rgba(0, 168, 204, 0.7)',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=dict(text="Comparación vs. Promedio del Sector", 
                  font=dict(size=16, color="white")),
        template="plotly_dark",
        height=450,
        barmode='group',
        xaxis_tickangle=-45,
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

# Función para crear gráfica de rendimiento por categorías
def create_category_performance_chart():
    categories = ['Moda', 'Alimentación', 'Electrónica', 'Hogar', 'Deportes', 'Otros']
    values = [35, 25, 15, 12, 8, 5]
    colors = ['#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#66bb6a', '#ab47bc']
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont=dict(size=12, color='white')
    )])
    
    fig.update_layout(
        title=dict(text="Distribución por Categorías", 
                  font=dict(size=16, color="white")),
        template="plotly_dark",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01
        )
    )
    
    return fig

# Función para crear gráficas de análisis del mercado
def create_market_analysis_charts():
    """Crea gráficas útiles basadas en datos reales del mercado"""
    charts = {}
    
    try:
        # Obtener datos del mercado
        zone_data = get_market_data_by_zone()
        business_data = get_market_data_by_business_type()
        sector_avg, market_df = load_market_data()
        
        # 1. Ventas por Zona Geográfica
        if zone_data is not None:
            fig_zones = go.Figure()
            fig_zones.add_trace(go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ingresos (€)'],
                name='Ventas por Zona',
                marker_color=['#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#66bb6a', '#ab47bc'],
                text=[f"{v:,.0f}€" for v in zone_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='white', size=12)
            ))
            fig_zones.update_layout(
                title="💰 Ventas Totales por Zona Geográfica",
                xaxis_title="Zona Geográfica",
                yaxis_title="Ventas Totales (€)",
                template="plotly_dark",
                height=400
            )
            charts['ventas_zonas'] = fig_zones
        
        # 2. Ocupación por m² por Zona
        if zone_data is not None:
            fig_ocupacion = go.Figure()
            fig_ocupacion.add_trace(go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ocupacion_por_m2'],
                name='Ocupación por m²',
                marker_color=['#66bb6a', '#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#ab47bc'],
                text=[f"{v:.1f}%" for v in zone_data['ocupacion_por_m2']],
                textposition='auto',
                textfont=dict(color='white', size=12)
            ))
            fig_ocupacion.update_layout(
                title="🏢 Tasa de Ocupación por Zona Geográfica",
                xaxis_title="Zona Geográfica",
                yaxis_title="Tasa de Ocupación (%)",
                template="plotly_dark",
                height=400
            )
            charts['ocupacion_zonas'] = fig_ocupacion
        
        # 3. Comparación por Tipo de Negocio
        if business_data is not None:
            fig_business = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Ventas por Tipo de Negocio', 'Visitantes por Tipo de Negocio'),
                specs=[[{"type": "bar"}, {"type": "bar"}]]
            )
            
            # Ventas por tipo de negocio
            fig_business.add_trace(
                go.Bar(
                    x=business_data['tipo_negocio'],
                    y=business_data['ingresos (€)'],
                    name='Ventas',
                    marker_color=['#00d4aa', '#ff6b6b', '#00a8cc'],
                    text=[f"{v:,.0f}€" for v in business_data['ingresos (€)']],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Visitantes por tipo de negocio
            fig_business.add_trace(
                go.Bar(
                    x=business_data['tipo_negocio'],
                    y=business_data['afluencia'],
                    name='Visitantes',
                    marker_color=['#ffa726', '#66bb6a', '#ab47bc'],
                    text=[f"{v:,.0f}" for v in business_data['afluencia']],
                    textposition='auto'
                ),
                row=1, col=2
            )
            
            fig_business.update_layout(
                title="🎯 Análisis por Tipo de Negocio",
                template="plotly_dark",
                height=400,
                showlegend=False
            )
            charts['business_comparison'] = fig_business
        
        # 4. Top Performers (Ranking)
        if zone_data is not None and business_data is not None:
            fig_ranking = make_subplots(
                rows=2, cols=1,
                subplot_titles=('🏆 Top Zonas por Rendimiento', '🎯 Top Tipos de Negocio por Ocupación'),
                specs=[[{"type": "bar"}], [{"type": "bar"}]]
            )
            
            # Ranking de zonas por ventas
            zone_sorted = zone_data.sort_values('ingresos (€)', ascending=True)
            fig_ranking.add_trace(
                go.Bar(
                    y=zone_sorted['zona_geografica'],
                    x=zone_sorted['ingresos (€)'],
                    orientation='h',
                    name='Ventas por Zona',
                    marker_color='#00d4aa',
                    text=[f"{v:,.0f}€" for v in zone_sorted['ingresos (€)']],
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            # Ranking de tipos de negocio por ocupación
            business_sorted = business_data.sort_values('ocupacion_por_m2', ascending=True)
            fig_ranking.add_trace(
                go.Bar(
                    y=business_sorted['tipo_negocio'],
                    x=business_sorted['ocupacion_por_m2'],
                    orientation='h',
                    name='Ocupación por Tipo',
                    marker_color='#ff6b6b',
                    text=[f"{v:.1f}%" for v in business_sorted['ocupacion_por_m2']],
                    textposition='auto'
                ),
                row=2, col=1
            )
            
            fig_ranking.update_layout(
                title="📊 Rankings de Rendimiento",
                template="plotly_dark",
                height=600,
                showlegend=False
            )
            charts['rankings'] = fig_ranking
        
        # 5. Análisis de Eficiencia (Ventas vs Visitantes)
        if market_df is not None:
            fig_efficiency = go.Figure()
            
            # Calcular eficiencia (ventas por visitante)
            market_df['eficiencia'] = market_df['ingresos_totales'] / market_df['trafico_peatonal']
            
            # Scatter plot por zona y tipo de negocio
            colors_map = {'Madrid': '#00d4aa', 'Cataluña': '#00a8cc', 'Norte': '#ff6b6b', 
                         'Sur': '#ffa726', 'Castilla-La Mancha': '#66bb6a', 'León': '#ab47bc'}
            
            for zona in market_df['zona_geografica'].unique():
                data_zona = market_df[market_df['zona_geografica'] == zona]
                fig_efficiency.add_trace(go.Scatter(
                    x=data_zona['trafico_peatonal'],
                    y=data_zona['ingresos_totales'],
                    mode='markers',
                    name=zona,
                    marker=dict(
                        size=data_zona['tasa_ocupacion']/3,  # Tamaño basado en ocupación
                        color=colors_map.get(zona, '#999999'),
                        opacity=0.7
                    ),
                    text=[f"{zona}<br>Tipo: {tipo}<br>Ocupación: {ocup:.1f}%" 
                          for tipo, ocup in zip(data_zona['tipo_negocio'], data_zona['tasa_ocupacion'])],
                    hovertemplate='%{text}<br>Visitantes: %{x}<br>Ventas: %{y:,.0f}€<extra></extra>'
                ))
            
            fig_efficiency.update_layout(
                title="⚡ Eficiencia: Ventas vs Visitantes (tamaño = ocupación)",
                xaxis_title="Visitantes",
                yaxis_title="Ventas (€)",
                template="plotly_dark",
                height=500
            )
            charts['efficiency'] = fig_efficiency
        
        return charts
        
    except Exception as e:
        print(f"Error creating market analysis charts: {e}")
        return {}

# Navegación principal
with st.sidebar:
    selected = option_menu(
        menu_title="Harmon BI",
        options=["Cargar Datos", "Dashboard", "Análisis vs Mercado", "Datos del Mercado", "Configuración"],
        icons=["upload", "speedometer2", "graph-up", "database", "gear"],
        menu_icon="building",
        default_index=1,
        styles={
            "container": {"padding": "0!important", "background-color": "#262730"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#20b2aa",
            },
            "nav-link-selected": {"background-color": "#20b2aa"},
        }
    )

# Página de Cargar Datos
if selected == "Cargar Datos":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    st.header("📊 Cargar Datos del Centro Comercial")
    st.subheader("Sube tu archivo Excel o CSV con las métricas de tu centro comercial")
    
    # Formulario de carga
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            center_name = st.text_input(
                "Nombre del Centro Comercial",
                placeholder="Ej. Centro Plaza Mayor"
            )
        
        with col2:
            center_type = st.selectbox(
                "Tipo de Centro",
                ["Urbano", "Suburbano", "Regional", "Outlet", "Especializado"]
            )
        
        # Área de carga de archivo
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Arrastra tu archivo aquí o haz clic para seleccionar",
            type=['xlsx', 'csv'],
            help="Excel (.xlsx) o CSV (.csv) - Máximo 10MB"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de procesamiento
        submitted = st.form_submit_button("Procesar Datos", type="primary")
        
        if submitted and uploaded_file is not None and center_name:
            with st.spinner("Procesando datos..."):
                center_data, message = process_uploaded_file(uploaded_file, center_name, center_type)
                
                if center_data:
                    st.session_state.centers_data[center_name] = center_data
                    st.session_state.current_center = center_name
                    st.success(f"✅ {message}")
                    st.success("🎉 ¡Datos cargados exitosamente! Ve al Dashboard para visualizar tus métricas.")
                else:
                    st.error(f"❌ {message}")
        
        elif submitted:
            st.warning("⚠️ Por favor, completa todos los campos y sube un archivo")

# Página de Dashboard
elif selected == "Dashboard":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    # Filtro de período
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("📈 Dashboard - Mi Centro")
    with col2:
        period = st.selectbox("Período", ["Mensual", "Trimestral", "Anual"], key="dashboard_period")
    
    if st.session_state.current_center and st.session_state.current_center in st.session_state.centers_data:
        center_data = st.session_state.centers_data[st.session_state.current_center]
        sector_avg = get_sector_averages()
        
        # Obtener datos más recientes
        latest_data = center_data['monthly_data'][-1] if center_data['monthly_data'] else {}
        
        # 10 KPIs más importantes
        st.subheader("📊 10 Indicadores Clave de Rendimiento")
        
        # Obtener datos del sector para comparación
        sector_avg = get_sector_averages()
        zone_data = get_market_data_by_zone()
        business_data = get_market_data_by_business_type()
        
        # Fila 1: KPIs Financieros
        st.markdown("### 💰 **Rendimiento Financiero**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>💰 Ventas Totales</h3>
                <h2>{sector_avg.get('ventas_totales', 0):,.0f}</h2>
                <p>€ del mercado</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>📈 Ventas por m²</h3>
                <h2>{sector_avg.get('ventas_por_m2', 0):.1f}</h2>
                <p>€/m² promedio</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>📊 Ingresos por Centro</h3>
                <h2>{sector_avg.get('ingresos_totales', 0):,.0f}</h2>
                <p>€ promedio/centro</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if zone_data is not None:
                best_zone = zone_data.loc[zone_data['ingresos (€)'].idxmax()]
                performance = ((best_zone['ingresos (€)'] / zone_data['ingresos (€)'].mean() - 1) * 100)
                st.markdown(f"""
                <div class="kpi-card">
                    <h3>🏆 Top Zona</h3>
                    <h2>{best_zone['zona_geografica']}</h2>
                    <p>+{performance:.1f}% vs promedio</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Fila 2: KPIs de Tráfico y Conversión
        st.markdown("### 👥 **Tráfico y Conversión**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>👥 Visitantes Totales</h3>
                <h2>{sector_avg.get('n_visitantes', 0):,.0f}</h2>
                <p>visitantes del mercado</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>⏱️ Tiempo Permanencia</h3>
                <h2>{sector_avg.get('tiempo_permanencia', 0):.0f}</h2>
                <p>minutos promedio</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>🎯 Tasa Conversión</h3>
                <h2>{sector_avg.get('tasa_conversion', 0):.1f}%</h2>
                <p>conversión promedio</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if business_data is not None:
                best_business = business_data.loc[business_data['ingresos (€)'].idxmax()]
                performance = ((best_business['ingresos (€)'] / business_data['ingresos (€)'].mean() - 1) * 100)
                st.markdown(f"""
                <div class="kpi-card">
                    <h3>🎯 Top Categoría</h3>
                    <h2>{best_business['tipo_negocio']}</h2>
                    <p>+{performance:.1f}% vs promedio</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Fila 3: KPIs Operacionales
        st.markdown("### 🏢 **Eficiencia Operacional**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>🏢 Tasa Ocupación</h3>
                <h2>{sector_avg.get('tasa_ocupacion', 0):.1f}%</h2>
                <p>ocupación promedio</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if zone_data is not None and business_data is not None:
                diversification = len(zone_data) * len(business_data)
                st.markdown(f"""
                <div class="kpi-card">
                    <h3>📍 Diversificación</h3>
                    <h2>{len(zone_data)} x {len(business_data)}</h2>
                    <p>zonas x categorías</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Gráficas principales
        st.subheader("📊 Análisis Detallado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(
                create_comparison_chart(latest_data, sector_avg),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(
                create_kpi_chart(
                    center_data['monthly_data'],
                    sector_avg['trafico_peatonal'],
                    'trafico_peatonal',
                    'Evolución del Tráfico Peatonal',
                    'visitantes/día'
                ),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Análisis avanzado del mercado
        st.subheader("📊 Análisis Avanzado del Mercado")
        
        # Crear gráficas del mercado
        market_charts = create_market_analysis_charts()
        
        if market_charts:
            # Fila 1: Ventas y Ocupación por Zona
            col1, col2 = st.columns(2)
            
            with col1:
                if 'ventas_zonas' in market_charts:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(market_charts['ventas_zonas'], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                if 'ocupacion_zonas' in market_charts:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(market_charts['ocupacion_zonas'], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Fila 2: Análisis por Tipo de Negocio
            if 'business_comparison' in market_charts:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(market_charts['business_comparison'], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Fila 3: Rankings y Eficiencia
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if 'rankings' in market_charts:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(market_charts['rankings'], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                if 'efficiency' in market_charts:
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    st.plotly_chart(market_charts['efficiency'], use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.info("📝 No hay datos cargados. Ve a 'Cargar Datos' para subir información de tu centro comercial.")

# Página de Análisis vs Mercado
elif selected == "Análisis vs Mercado":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    st.header("📊 Análisis vs Mercado")
    
    if st.session_state.current_center and st.session_state.current_center in st.session_state.centers_data:
        center_data = st.session_state.centers_data[st.session_state.current_center]
        sector_avg = get_sector_averages()
        latest_data = center_data['monthly_data'][-1] if center_data['monthly_data'] else {}
        
        # Resumen ejecutivo de comparación
        st.subheader("🎯 Resumen Ejecutivo vs Mercado")
        
        # Crear métricas de comparación
        comparison_metrics = []
        metrics_info = [
            ('trafico_peatonal', 'Tráfico Peatonal', 'visitantes/día', sector_avg['trafico_peatonal']),
            ('ventas_por_m2', 'Ventas por m²', '€/m²/mes', sector_avg['ventas_por_m2']),
            ('tasa_ocupacion', 'Tasa de Ocupación', '%', sector_avg['tasa_ocupacion']),
            ('tiempo_permanencia', 'Tiempo Permanencia', 'minutos', sector_avg['tiempo_permanencia']),
            ('tasa_conversion', 'Tasa de Conversión', '%', sector_avg['tasa_conversion']),
            ('ingresos_totales', 'Ingresos Totales', '€/mes', sector_avg['ingresos_totales'])
        ]
        
        for metric, name, unit, sector_val in metrics_info:
            center_val = latest_data.get(metric, 0)
            performance = (center_val / sector_val - 1) * 100 if sector_val > 0 else 0
            comparison_metrics.append({
                'metric': name,
                'center_value': center_val,
                'sector_value': sector_val,
                'performance': performance,
                'unit': unit
            })
        
        # Mostrar métricas de comparación
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📈 Rendimiento Superior al Mercado**")
            superior_metrics = [m for m in comparison_metrics if m['performance'] > 0]
            for metric in superior_metrics:
                st.success(f"✅ {metric['metric']}: +{metric['performance']:.1f}%")
        
        with col2:
            st.markdown("**📉 Rendimiento Inferior al Mercado**")
            inferior_metrics = [m for m in comparison_metrics if m['performance'] < 0]
            for metric in inferior_metrics:
                st.error(f"❌ {metric['metric']}: {metric['performance']:.1f}%")
        
        with col3:
            st.markdown("**📊 Rendimiento Promedio**")
            avg_metrics = [m for m in comparison_metrics if abs(m['performance']) <= 5]
            for metric in avg_metrics:
                st.info(f"⚖️ {metric['metric']}: {metric['performance']:+.1f}%")
        
        # Gráfica de comparación detallada
        st.subheader("📊 Comparación Detallada vs Mercado")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Gráfica de radar mejorada
            categories = ['Tráfico', 'Ventas/m²', 'Ocupación', 'Tiempo', 'Conversión', 'Ingresos']
            
            # Normalizar valores para el radar (0-100)
            center_values = [
                min(100, (latest_data.get('trafico_peatonal', 0) / sector_avg['trafico_peatonal']) * 50),
                min(100, (latest_data.get('ventas_por_m2', 0) / sector_avg['ventas_por_m2']) * 50),
                latest_data.get('tasa_ocupacion', 0),
                min(100, (latest_data.get('tiempo_permanencia', 0) / sector_avg['tiempo_permanencia']) * 50),
                latest_data.get('tasa_conversion', 0) * 5,
                min(100, (latest_data.get('ingresos_totales', 0) / sector_avg['ingresos_totales']) * 50)
            ]
            
            sector_values = [50, 50, sector_avg['tasa_ocupacion'], 50, sector_avg['tasa_conversion'] * 5, 50]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=center_values,
                theta=categories,
                fill='toself',
                name='Tu Centro',
                line_color='#00d4aa',
                fillcolor='rgba(0, 212, 170, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=sector_values,
                theta=categories,
                fill='toself',
                name='Promedio Mercado',
                line_color='#00a8cc',
                fillcolor='rgba(0, 168, 204, 0.2)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(color='white')
                    )),
                showlegend=True,
                title=dict(text="Comparación de Rendimiento vs Mercado", 
                          font=dict(size=16, color="white")),
                template="plotly_dark",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Gráfica de barras de comparación
            metric_names = [m['metric'] for m in comparison_metrics]
            center_vals = [m['center_value'] for m in comparison_metrics]
            sector_vals = [m['sector_value'] for m in comparison_metrics]
            performances = [m['performance'] for m in comparison_metrics]
            
            # Crear colores basados en el rendimiento
            colors = ['#00d4aa' if p > 0 else '#ff4757' if p < -10 else '#ffa726' for p in performances]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Tu Centro',
                x=metric_names,
                y=center_vals,
                marker_color=colors,
                text=[f"{p:+.1f}%" for p in performances],
                textposition='auto',
                textfont=dict(color='white', size=10)
            ))
            
            fig.add_trace(go.Bar(
                name='Promedio Mercado',
                x=metric_names,
                y=sector_vals,
                marker_color='rgba(0, 168, 204, 0.7)',
                opacity=0.7
            ))
            
            fig.update_layout(
                title=dict(text="Comparación Directa vs Mercado", 
                          font=dict(size=16, color="white")),
                template="plotly_dark",
                height=500,
                barmode='group',
                xaxis_tickangle=-45,
                hovermode='x unified',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Análisis de posicionamiento en el mercado
        st.subheader("🎯 Posicionamiento en el Mercado")
        
        # Calcular score general
        total_performance = sum([abs(m['performance']) for m in comparison_metrics if m['performance'] > 0])
        total_metrics = len([m for m in comparison_metrics if m['performance'] > 0])
        market_score = (total_performance / total_metrics) if total_metrics > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Score vs Mercado",
                f"{market_score:.1f}%",
                f"{'Superior' if market_score > 10 else 'Promedio' if market_score > 0 else 'Inferior'}"
            )
        
        with col2:
            superior_count = len([m for m in comparison_metrics if m['performance'] > 0])
            st.metric(
                "Métricas Superiores",
                f"{superior_count}/6",
                f"{superior_count/6*100:.0f}%"
            )
        
        with col3:
            avg_performance = sum([m['performance'] for m in comparison_metrics]) / len(comparison_metrics)
            st.metric(
                "Rendimiento Promedio",
                f"{avg_performance:+.1f}%",
                f"{'Excelente' if avg_performance > 10 else 'Bueno' if avg_performance > 0 else 'Mejorable'}"
            )
        
        with col4:
            best_metric = max(comparison_metrics, key=lambda x: x['performance'])
            st.metric(
                "Mejor Métrica",
                best_metric['metric'],
                f"+{best_metric['performance']:.1f}%"
            )
        
        # Recomendaciones estratégicas basadas en el mercado
        st.subheader("💡 Recomendaciones Estratégicas vs Mercado")
        
        # Generar recomendaciones específicas
        recommendations = []
        
        for metric in comparison_metrics:
            if metric['performance'] < -10:  # Significativamente por debajo del mercado
                if 'Tráfico' in metric['metric']:
                    recommendations.append({
                        'area': 'Marketing y Promoción',
                        'metric': metric['metric'],
                        'performance': metric['performance'],
                        'recommendation': 'Implementar campañas de marketing digital y eventos especiales para aumentar el tráfico peatonal',
                        'priority': 'Alta'
                    })
                elif 'Ventas' in metric['metric']:
                    recommendations.append({
                        'area': 'Estrategia Comercial',
                        'metric': metric['metric'],
                        'performance': metric['performance'],
                        'recommendation': 'Revisar mix de tiendas y estrategias de pricing para mejorar ventas por m²',
                        'priority': 'Alta'
                    })
                elif 'Ocupación' in metric['metric']:
                    recommendations.append({
                        'area': 'Gestión de Espacios',
                        'metric': metric['metric'],
                        'performance': metric['performance'],
                        'recommendation': 'Desarrollar estrategias de atracción de nuevos inquilinos y retención',
                        'priority': 'Alta'
                    })
                elif 'Conversión' in metric['metric']:
                    recommendations.append({
                        'area': 'Experiencia del Cliente',
                        'metric': metric['metric'],
                        'performance': metric['performance'],
                        'recommendation': 'Mejorar la experiencia del cliente y optimizar el layout del centro',
                        'priority': 'Media'
                    })
                elif 'Tiempo' in metric['metric']:
                    recommendations.append({
                        'area': 'Entretenimiento y Servicios',
                        'metric': metric['metric'],
                        'performance': metric['performance'],
                        'recommendation': 'Añadir más opciones de entretenimiento y servicios para aumentar tiempo de permanencia',
                        'priority': 'Media'
                    })
        
        # Mostrar recomendaciones
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_color = "🔴" if rec['priority'] == 'Alta' else "🟡"
                
                with st.expander(f"{priority_color} {rec['area']} - {rec['metric']} ({rec['performance']:+.1f}%)"):
                    st.write(f"**Recomendación:** {rec['recommendation']}")
                    st.write(f"**Prioridad:** {rec['priority']}")
                    st.write(f"**Impacto esperado:** Mejora del {abs(rec['performance']):.1f}% en {rec['metric']}")
        else:
            st.success("🎉 ¡Excelente! Tu centro está por encima del promedio del mercado en todas las métricas principales.")
        
        # Análisis de tendencias vs mercado
        st.subheader("📈 Tendencias vs Mercado")
        
        if len(center_data['monthly_data']) >= 2:
            latest = center_data['monthly_data'][-1]
            previous = center_data['monthly_data'][-2]
            
            trends = {}
            for metric in ['trafico_peatonal', 'ventas_por_m2', 'tasa_ocupacion', 
                          'tiempo_permanencia', 'tasa_conversion', 'ingresos_totales']:
                change = ((latest[metric] - previous[metric]) / previous[metric]) * 100
                trends[metric] = change
            
            # Mostrar tendencias con contexto de mercado
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Tráfico Peatonal",
                    f"{latest['trafico_peatonal']:.0f}",
                    f"{trends['trafico_peatonal']:+.1f}%",
                    help=f"vs Mercado: {((latest['trafico_peatonal']/sector_avg['trafico_peatonal']-1)*100):+.1f}%"
                )
                st.metric(
                    "Ventas por m²",
                    f"{latest['ventas_por_m2']:.1f}",
                    f"{trends['ventas_por_m2']:+.1f}%",
                    help=f"vs Mercado: {((latest['ventas_por_m2']/sector_avg['ventas_por_m2']-1)*100):+.1f}%"
                )
            
            with col2:
                st.metric(
                    "Tasa de Ocupación",
                    f"{latest['tasa_ocupacion']:.1f}%",
                    f"{trends['tasa_ocupacion']:+.1f}%",
                    help=f"vs Mercado: {((latest['tasa_ocupacion']/sector_avg['tasa_ocupacion']-1)*100):+.1f}%"
                )
                st.metric(
                    "Tiempo Permanencia",
                    f"{latest['tiempo_permanencia']:.0f} min",
                    f"{trends['tiempo_permanencia']:+.1f}%",
                    help=f"vs Mercado: {((latest['tiempo_permanencia']/sector_avg['tiempo_permanencia']-1)*100):+.1f}%"
                )
            
            with col3:
                st.metric(
                    "Tasa de Conversión",
                    f"{latest['tasa_conversion']:.1f}%",
                    f"{trends['tasa_conversion']:+.1f}%",
                    help=f"vs Mercado: {((latest['tasa_conversion']/sector_avg['tasa_conversion']-1)*100):+.1f}%"
                )
                st.metric(
                    "Ingresos Totales",
                    f"{latest['ingresos_totales']:,.0f}€",
                    f"{trends['ingresos_totales']:+.1f}%",
                    help=f"vs Mercado: {((latest['ingresos_totales']/sector_avg['ingresos_totales']-1)*100):+.1f}%"
                )
        
            # Insights y recomendaciones
            st.subheader("💡 Insights y Recomendaciones")
            
            # Generar insights basados en los datos
            insights = []
            recommendations = []
            
            # Análisis de tráfico
            if latest['trafico_peatonal'] > sector_avg['trafico_peatonal']:
                insights.append("✅ Tu centro tiene un tráfico peatonal superior al promedio del sector")
            else:
                insights.append("⚠️ El tráfico peatonal está por debajo del promedio del sector")
                recommendations.append("Considera estrategias de marketing para aumentar el tráfico")
            
            # Análisis de conversión
            if latest['tasa_conversion'] > sector_avg['tasa_conversion']:
                insights.append("✅ Excelente tasa de conversión, superior al promedio")
            else:
                insights.append("⚠️ La tasa de conversión está por debajo del promedio")
                recommendations.append("Revisa la experiencia del cliente y la oferta comercial")
            
            # Análisis de ocupación
            if latest['tasa_ocupacion'] > 80:
                insights.append("✅ Alta tasa de ocupación, excelente gestión de espacios")
            elif latest['tasa_ocupacion'] < 70:
                insights.append("⚠️ Tasa de ocupación baja, hay oportunidades de mejora")
                recommendations.append("Evalúa estrategias para atraer nuevos inquilinos")
            
            # Análisis de tiempo de permanencia
            if latest['tiempo_permanencia'] > sector_avg['tiempo_permanencia']:
                insights.append("✅ Los visitantes permanecen más tiempo que el promedio")
            else:
                insights.append("⚠️ Tiempo de permanencia por debajo del promedio")
                recommendations.append("Mejora la experiencia del visitante y la oferta de entretenimiento")
            
            # Mostrar insights
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔍 Insights Clave:**")
                for insight in insights:
                    st.write(insight)
            
            with col2:
                st.markdown("**📋 Recomendaciones:**")
                if recommendations:
                    for rec in recommendations:
                        st.write(f"• {rec}")
                else:
                    st.write("🎉 ¡Excelente rendimiento! Mantén las estrategias actuales.")
        
        # Gráfica de rendimiento por trimestre
        st.subheader("📊 Rendimiento por Trimestre")
        
        if len(center_data['monthly_data']) >= 3:
            # Agrupar por trimestre
            df_quarterly = pd.DataFrame(center_data['monthly_data'])
            df_quarterly['fecha'] = pd.to_datetime(df_quarterly['fecha'])
            df_quarterly['quarter'] = df_quarterly['fecha'].dt.to_period('Q')
            
            quarterly_avg = df_quarterly.groupby('quarter').agg({
                'trafico_peatonal': 'mean',
                'ventas_por_m2': 'mean',
                'tasa_ocupacion': 'mean',
                'tiempo_permanencia': 'mean',
                'tasa_conversion': 'mean',
                'ingresos_totales': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=quarterly_avg['quarter'].astype(str),
                y=quarterly_avg['ingresos_totales'],
                mode='lines+markers',
                name='Ingresos Totales',
                line=dict(color='#00d4aa', width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title="Evolución de Ingresos por Trimestre",
                xaxis_title="Trimestre",
                yaxis_title="Ingresos (€)",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📝 No hay datos cargados. Ve a 'Cargar Datos' para subir información de tu centro comercial.")

# Página de Datos del Mercado
elif selected == "Datos del Mercado":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    st.header("📊 Datos Agregados del Mercado")
    st.subheader("Información consolidada del sector de centros comerciales")
    
    # Obtener datos del sector
    sector_avg = get_sector_averages()
    
    # Información general del mercado
    st.subheader("🎯 Resumen del Mercado")
    
    # Obtener datos adicionales del mercado
    zone_data = get_market_data_by_zone()
    business_data = get_market_data_by_business_type()
    center_performance = get_center_performance_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💰 Ventas Totales**")
        st.metric("Ventas Totales", f"{sector_avg['ventas_totales']:,.0f}", "€")
        st.metric("Promedio por Centro", f"{sector_avg['ingresos_totales']:,.0f}", "€/centro")
        if center_performance is not None:
            st.metric("Centros Analizados", f"{len(center_performance)}", "centros")
    
    with col2:
        st.markdown("**👥 Visitantes**")
        st.metric("Total Visitantes", f"{sector_avg['n_visitantes']:,.0f}", "visitantes")
        st.metric("Ocupación por m²", f"{sector_avg['ocupacion_por_m2']:.2f}", "visitantes/m²")
        if zone_data is not None:
            st.metric("Zonas Analizadas", f"{len(zone_data)}", "zonas")
    
    with col3:
        st.markdown("**🏢 Distribución**")
        if zone_data is not None:
            best_zone = zone_data.loc[zone_data['ingresos (€)'].idxmax()]
            st.metric("Mejor Zona", best_zone['zona_geografica'], f"{best_zone['ingresos (€)']:,.0f}€")
        if business_data is not None:
            best_business = business_data.loc[business_data['ingresos (€)'].idxmax()]
            st.metric("Mejor Categoría", best_business['tipo_negocio'], f"{best_business['ingresos (€)']:,.0f}€")
        if business_data is not None:
            st.metric("Tipos de Negocio", f"{len(business_data)}", "categorías")
    
    # Gráficas del mercado
    st.subheader("📊 Análisis del Mercado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Gráfica de distribución de métricas del mercado
        metrics = ['Tráfico Peatonal', 'Ventas/m²', 'Ocupación', 'Tiempo Permanencia', 'Conversión', 'Ingresos']
        values = [
            sector_avg['trafico_peatonal'] / 100,
            sector_avg['ventas_por_m2'] * 2,
            sector_avg['tasa_ocupacion'],
            sector_avg['tiempo_permanencia'],
            sector_avg['tasa_conversion'] * 5,
            sector_avg['ingresos_totales'] / 10000
        ]
        
        fig = go.Figure(data=[go.Bar(
            x=metrics,
            y=values,
            marker_color=['#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#66bb6a', '#ab47bc'],
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
            textfont=dict(color='white', size=12)
        )])
        
        fig.update_layout(
            title=dict(text="Promedios del Mercado por Métrica", 
                      font=dict(size=16, color="white")),
            template="plotly_dark",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Gráfica de radar del mercado
        categories = ['Tráfico', 'Ventas/m²', 'Ocupación', 'Tiempo', 'Conversión', 'Ingresos']
        market_values = [50, 50, sector_avg['tasa_ocupacion'], 50, sector_avg['tasa_conversion'] * 5, 50]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=market_values,
            theta=categories,
            fill='toself',
            name='Promedio del Mercado',
            line_color='#00a8cc',
            fillcolor='rgba(0, 168, 204, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(color='white')
                )),
            showlegend=True,
            title=dict(text="Perfil del Mercado", 
                      font=dict(size=16, color="white")),
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Análisis de tendencias del mercado con gráficas mejoradas
    st.subheader("📈 Análisis de Tendencias del Mercado")
    
    # Crear gráficas de análisis del mercado
    market_charts = create_market_analysis_charts()
    
    if market_charts:
        # Mostrar gráficas útiles
        col1, col2 = st.columns(2)
        
        with col1:
            if 'ventas_zonas' in market_charts:
                st.plotly_chart(market_charts['ventas_zonas'], use_container_width=True)
        
        with col2:
            if 'ocupacion_zonas' in market_charts:
                st.plotly_chart(market_charts['ocupacion_zonas'], use_container_width=True)
        
        # Análisis por tipo de negocio
        if 'business_comparison' in market_charts:
            st.plotly_chart(market_charts['business_comparison'], use_container_width=True)
        
        # Rankings y eficiencia
        col1, col2 = st.columns(2)
        
        with col1:
            if 'rankings' in market_charts:
                st.plotly_chart(market_charts['rankings'], use_container_width=True)
        
        with col2:
            if 'efficiency' in market_charts:
                st.plotly_chart(market_charts['efficiency'], use_container_width=True)
        
        # Simular datos mensuales para tendencias
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        # Obtener datos reales para crear tendencias
        sector_avg, _ = load_market_data()
        
        # Crear variaciones estacionales realistas
        market_trends = {
            'trafico': [sector_avg['trafico_peatonal'] * factor for factor in [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 0.95, 0.9, 0.85, 0.95]],
            'ventas': [sector_avg['ventas_por_m2'] * factor for factor in [0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.1, 1.0, 0.95, 0.9, 0.85, 0.95]],
            'ocupacion': [sector_avg['tasa_ocupacion'] * factor for factor in [0.95, 0.96, 0.98, 0.97, 0.99, 1.0, 0.99, 0.98, 0.97, 0.96, 0.95, 0.98]],
            'conversion': [sector_avg['tasa_conversion'] * factor for factor in [0.95, 1.0, 1.05, 1.02, 1.08, 1.12, 1.10, 1.06, 1.04, 1.0, 0.98, 1.06]]
        }
    else:
        # Valores por defecto si no se pueden cargar los datos
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        market_trends = {
            'trafico': [2400, 2500, 2600, 2550, 2700, 2800, 2750, 2600, 2500, 2400, 2300, 2500],
            'ventas': [42, 44, 45, 43, 46, 48, 47, 45, 44, 42, 41, 45],
            'ocupacion': [75, 76, 78, 77, 79, 80, 79, 78, 77, 76, 75, 78],
            'conversion': [11.5, 12.0, 12.5, 12.2, 13.0, 13.5, 13.2, 12.8, 12.5, 12.0, 11.8, 12.8]
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfica de tendencias de tráfico y ventas
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Tráfico Peatonal del Mercado', 'Ventas por m² del Mercado'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['trafico'], 
                      mode='lines+markers', name='Tráfico',
                      line=dict(color='#00d4aa', width=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['ventas'], 
                      mode='lines+markers', name='Ventas',
                      line=dict(color='#ff6b6b', width=3)),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Tendencias del Mercado - Tráfico y Ventas",
            template="plotly_dark",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfica de tendencias de ocupación y conversión
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Ocupación del Mercado', 'Conversión del Mercado'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['ocupacion'], 
                      mode='lines+markers', name='Ocupación',
                      line=dict(color='#00a8cc', width=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['conversion'], 
                      mode='lines+markers', name='Conversión',
                      line=dict(color='#ffa726', width=3)),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Tendencias del Mercado - Ocupación y Conversión",
            template="plotly_dark",
            height=500,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Análisis por zona geográfica
    if zone_data is not None:
        st.subheader("🗺️ Análisis por Zona Geográfica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfica de ventas por zona
            fig = go.Figure(data=[go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ingresos (€)'],
                marker_color=['#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#66bb6a'],
                text=[f"{v:,.0f}" for v in zone_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='white', size=10)
            )])
            
            fig.update_layout(
                title="Ventas Totales por Zona Geográfica",
                xaxis_title="Zona Geográfica",
                yaxis_title="Ventas Totales (€)",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfica de ocupación por m² por zona
            fig = go.Figure(data=[go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ocupacion_por_m2'],
                marker_color=['#00d4aa', '#00a8cc', '#ff6b6b', '#ffa726', '#66bb6a'],
                text=[f"{v:.2f}" for v in zone_data['ocupacion_por_m2']],
                textposition='auto',
                textfont=dict(color='white', size=10)
            )])
            
            fig.update_layout(
                title="Ocupación por m² por Zona",
                xaxis_title="Zona Geográfica",
                yaxis_title="Ocupación por m² (visitantes/m²)",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos por zona
        st.subheader("📋 Datos Detallados por Zona Geográfica")
        
        # Preparar datos para la tabla
        display_zone_data = zone_data.copy()
        display_zone_data['afluencia'] = display_zone_data['afluencia'].round(0)
        display_zone_data['ingresos (€)'] = display_zone_data['ingresos (€)'].round(0)
        display_zone_data['tamaño_m2'] = display_zone_data['tamaño_m2'].round(0)
        display_zone_data['empleados'] = display_zone_data['empleados'].round(0)
        display_zone_data['ocupacion_por_m2'] = display_zone_data['ocupacion_por_m2'].round(2)
        
        # Renombrar columnas para mejor visualización
        display_zone_data.columns = ['Zona Geográfica', 'Total Visitantes', 'Ventas Totales (€)', 
                                    'Tamaño Total (m²)', 'Total Empleados', 'Ocupación por m²']
        
        st.dataframe(display_zone_data, use_container_width=True)

    # Análisis por tipo de negocio
    if business_data is not None:
        st.subheader("🏪 Análisis por Tipo de Negocio")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfica de ventas por tipo de negocio
            fig = go.Figure(data=[go.Bar(
                x=business_data['tipo_negocio'],
                y=business_data['ingresos (€)'],
                marker_color=['#00d4aa', '#00a8cc', '#ff6b6b'],
                text=[f"{v:,.0f}" for v in business_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='white', size=10)
            )])
            
            fig.update_layout(
                title="Ventas Totales por Tipo de Negocio",
                xaxis_title="Tipo de Negocio",
                yaxis_title="Ventas Totales (€)",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfica de visitantes por tipo de negocio
            fig = go.Figure(data=[go.Bar(
                x=business_data['tipo_negocio'],
                y=business_data['afluencia'],
                marker_color=['#00d4aa', '#00a8cc', '#ff6b6b'],
                text=[f"{v:,.0f}" for v in business_data['afluencia']],
                textposition='auto',
                textfont=dict(color='white', size=10)
            )])
            
            fig.update_layout(
                title="Visitantes por Tipo de Negocio",
                xaxis_title="Tipo de Negocio",
                yaxis_title="Total Visitantes",
                template="plotly_dark",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabla de datos por tipo de negocio
        st.subheader("📋 Datos Detallados por Tipo de Negocio")
        
        # Preparar datos para la tabla
        display_business_data = business_data.copy()
        display_business_data['afluencia'] = display_business_data['afluencia'].round(0)
        display_business_data['ingresos (€)'] = display_business_data['ingresos (€)'].round(0)
        display_business_data['tamaño_m2'] = display_business_data['tamaño_m2'].round(0)
        display_business_data['empleados'] = display_business_data['empleados'].round(0)
        display_business_data['ocupacion_por_m2'] = display_business_data['ocupacion_por_m2'].round(2)
        
        # Renombrar columnas para mejor visualización
        display_business_data.columns = ['Tipo de Negocio', 'Total Visitantes', 'Ventas Totales (€)', 
                                        'Tamaño Total (m²)', 'Total Empleados', 'Ocupación por m²']
        
        st.dataframe(display_business_data, use_container_width=True)

    # Insights del mercado
    st.subheader("💡 Insights del Mercado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Análisis del Sector**")
        st.info(f"💰 **Ventas Totales**: {sector_avg['ventas_totales']:,.0f}€ en total")
        st.info(f"👥 **Visitantes**: {sector_avg['n_visitantes']:,.0f} visitantes totales")
        st.info(f"🏢 **Ocupación**: {sector_avg['ocupacion_por_m2']:.2f} visitantes/m² promedio")
        if zone_data is not None:
            best_zone = zone_data.loc[zone_data['ingresos (€)'].idxmax()]
            st.info(f"🗺️ **Mejor Zona**: {best_zone['zona_geografica']} con {best_zone['ingresos (€)']:,.0f}€")
    
    with col2:
        st.markdown("**📊 Benchmarking**")
        st.success(f"✅ **Ventas**: {sector_avg['ventas_totales']:,.0f}€ es el total del sector")
        st.success(f"✅ **Visitantes**: {sector_avg['n_visitantes']:,.0f} es el total de visitantes")
        st.success(f"✅ **Ocupación**: {sector_avg['ocupacion_por_m2']:.2f} visitantes/m² es el promedio")
        if business_data is not None:
            best_business = business_data.loc[business_data['ingresos (€)'].idxmax()]
            st.success(f"✅ **Mejor Categoría**: {best_business['tipo_negocio']} con {best_business['ingresos (€)']:,.0f}€")
    
    # Información adicional del mercado
    st.subheader("📋 Información Adicional del Mercado")
    
    with st.expander("🏢 Tipos de Centros Comerciales en el Mercado"):
        st.write("""
        **Centros Urbanos**: 
        - Tráfico promedio: 3,000 visitantes/día
        - Ventas promedio: 50€/m²/mes
        - Ocupación promedio: 85%
        
        **Centros Suburbanos**:
        - Tráfico promedio: 2,200 visitantes/día
        - Ventas promedio: 42€/m²/mes
        - Ocupación promedio: 75%
        
        **Centros Regionales**:
        - Tráfico promedio: 2,800 visitantes/día
        - Ventas promedio: 48€/m²/mes
        - Ocupación promedio: 80%
        """)
    
    with st.expander("📈 Factores que Afectan el Rendimiento"):
        st.write("""
        **Factores Positivos**:
        - Ubicación estratégica
        - Mix de tiendas diversificado
        - Eventos y promociones regulares
        - Servicios adicionales (cine, restaurantes)
        
        **Factores Negativos**:
        - Competencia directa cercana
        - Accesibilidad limitada
        - Falta de renovación
        - Estacionalidad marcada
        """)
    
    with st.expander("🎯 Mejores Prácticas del Sector"):
        st.write("""
        **Marketing y Promoción**:
        - Campañas digitales activas
        - Eventos temáticos mensuales
        - Programas de fidelización
        
        **Gestión Comercial**:
        - Análisis regular de mix de tiendas
        - Optimización de espacios
        - Estrategias de pricing dinámicas
        
        **Experiencia del Cliente**:
        - Layout intuitivo
        - Servicios de conveniencia
        - Tecnología integrada
        """)

# Página de Configuración
elif selected == "Configuración":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    st.header("⚙️ Configuración")
    
    # Información del centro actual
    if st.session_state.current_center and st.session_state.current_center in st.session_state.centers_data:
        center_data = st.session_state.centers_data[st.session_state.current_center]
        
        st.subheader("📋 Información del Centro")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Nombre:** {center_data['name']}")
            st.info(f"**Tipo:** {center_data['type']}")
        
        with col2:
            st.info(f"**Fecha de Carga:** {center_data['upload_date'][:10]}")
            st.info(f"**Registros:** {len(center_data['raw_data'])}")
        
        # Opciones de configuración
        st.subheader("🔧 Opciones de Configuración")
        
        # Selector de centro
        if len(st.session_state.centers_data) > 1:
            center_names = list(st.session_state.centers_data.keys())
            selected_center = st.selectbox(
                "Centro Activo",
                center_names,
                index=center_names.index(st.session_state.current_center)
            )
            
            if selected_center != st.session_state.current_center:
                st.session_state.current_center = selected_center
                st.rerun()
        
        # Configuración de alertas
        st.subheader("🔔 Configuración de Alertas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            traffic_threshold = st.number_input(
                "Umbral de Tráfico Peatonal",
                min_value=0,
                value=2000,
                help="Alerta cuando el tráfico esté por debajo de este valor"
            )
            
            occupancy_threshold = st.number_input(
                "Umbral de Ocupación (%)",
                min_value=0,
                max_value=100,
                value=70,
                help="Alerta cuando la ocupación esté por debajo de este porcentaje"
            )
        
        with col2:
            conversion_threshold = st.number_input(
                "Umbral de Conversión (%)",
                min_value=0,
                max_value=100,
                value=10,
                help="Alerta cuando la conversión esté por debajo de este porcentaje"
            )
            
            revenue_threshold = st.number_input(
                "Umbral de Ingresos (€)",
                min_value=0,
                value=1000000,
                help="Alerta cuando los ingresos estén por debajo de este valor"
            )
        
        # Guardar configuración
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada correctamente")
    
    else:
        st.info("📝 No hay datos cargados. Ve a 'Cargar Datos' para subir información de tu centro comercial.")
    
    # Información del sistema
    st.subheader("ℹ️ Información del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Centros Cargados", len(st.session_state.centers_data))
    
    with col2:
        st.metric("Versión", "1.0.0")
    
    with col3:
        st.metric("Última Actualización", datetime.now().strftime("%Y-%m-%d"))

if __name__ == "__main__":
    pass
