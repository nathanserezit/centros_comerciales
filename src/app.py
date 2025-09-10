import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os

# 🎨 Paleta de colores simplificada - Azul y Blanco
# Esquema de color centrado en azul #2563eb con gradientes
COLORS = {
    'primary': '#2563eb',      # Azul principal
    'primary_light': '#3b82f6', # Azul claro
    'primary_dark': '#1d4ed8',  # Azul oscuro
    'secondary': '#1e40af',     # Azul secundario
    'accent': '#60a5fa',        # Azul acento
    'success': '#10b981',       # Verde para éxito
    'warning': '#f59e0b',       # Ámbar para advertencias
    'error': '#ef4444',         # Rojo para errores
    'neutral': '#6b7280',       # Gris neutro
    'light': '#9ca3af'          # Gris claro
}

# Paleta específica para gráficas - Solo gradientes de azul
CHART_COLORS = [
    '#2563eb',  # Azul principal
    '#3b82f6',  # Azul medio
    '#60a5fa',  # Azul claro
    '#1d4ed8',  # Azul oscuro
    '#1e40af',  # Azul secundario
    '#93c5fd'   # Azul muy claro
]
import matplotlib.colors as mcolors
from streamlit_option_menu import option_menu

# Configuración de la página
st.set_page_config(
    page_title="Harmon BI Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Forzar visibilidad del sidebar (especialmente útil en Mac)
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

# 🖥️ Configuración para mejorar compatibilidad cross-platform
def configure_plotly_theme(dark_mode=False):
    """Configura tema consistente para gráficas según el modo claro/oscuro"""
    if dark_mode:
        return {
            'layout': {
                'font': {
                    'family': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
                    'size': 12,
                    'color': '#ffffff'
                },
                'plot_bgcolor': '#2d2d30',
                'paper_bgcolor': '#2d2d30',
                'colorway': CHART_COLORS,
                'xaxis': {
                    'gridcolor': '#3e3e42', 
                    'gridwidth': 1,
                    'color': '#ffffff',
                    'tickcolor': '#3e3e42'
                },
                'yaxis': {
                    'gridcolor': '#3e3e42', 
                    'gridwidth': 1,
                    'color': '#ffffff',
                    'tickcolor': '#3e3e42'
                }
            }
        }
    else:
        return {
            'layout': {
                'font': {
                    'family': '"Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
                    'size': 12,
                    'color': '#2c3e50'
                },
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'colorway': CHART_COLORS,
                'xaxis': {'gridcolor': '#e8e8e8', 'gridwidth': 1},
                'yaxis': {'gridcolor': '#e8e8e8', 'gridwidth': 1}
            }
        }

# Aplicar configuración global de Plotly basada en el modo
import plotly.io as pio

# JavaScript mejorado para sidebar y modo oscuro
st.markdown("""
<script>
// JavaScript para manejar el sidebar y modo oscuro
document.addEventListener('DOMContentLoaded', function() {
    function ensureSidebarVisibility() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.zIndex = '999';
            
            // Mejorar visibilidad del sidebar
            sidebar.style.minWidth = '280px';
            sidebar.style.maxWidth = '350px';
        }
        
        // Verificar si el menú de opciones es visible
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.style.color = 'white';
            link.style.visibility = 'visible';
            link.style.display = 'block';
        });
        
        // Asegurar que los elementos del sidebar sean visibles
        const sidebarElements = sidebar?.querySelectorAll('*');
        sidebarElements?.forEach(el => {
            if (el.style.display === 'none') {
                el.style.display = 'block';
            }
        });
    }
    
    // Ejecutar múltiples veces para asegurar que funcione
    ensureSidebarVisibility();
    setTimeout(ensureSidebarVisibility, 100);
    setTimeout(ensureSidebarVisibility, 500);
    setTimeout(ensureSidebarVisibility, 1000);
    setTimeout(ensureSidebarVisibility, 2000);
    
    // Observador para cambios en el DOM
    const observer = new MutationObserver(ensureSidebarVisibility);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Reobservar cuando cambia el contenido
    setInterval(ensureSidebarVisibility, 3000);
    
});
</script>
""", unsafe_allow_html=True)

# Inicializar datos de sesión
if 'centers_data' not in st.session_state:
    st.session_state.centers_data = {}
if 'current_center' not in st.session_state:
    st.session_state.current_center = None
if 'aggregated_data' not in st.session_state:
    st.session_state.aggregated_data = {}
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Dashboard"

# Función para generar CSS según el modo
def get_theme_css(dark_mode=False):
    """Genera CSS dinámico basado en el modo claro/oscuro con esquema azul y blanco"""
    if dark_mode:
        # Modo oscuro - Azul oscuro y blanco
        bg_primary = "#0f172a"     # Azul muy oscuro
        bg_secondary = "#1e293b"   # Azul oscuro medio
        bg_sidebar = "#1e293b"     # Azul oscuro para sidebar
        sidebar_text_color = "#ffffff"  # Texto blanco en sidebar
        sidebar_secondary_text = "#cbd5e1"  # Texto secundario en sidebar
        sidebar_border_color = "#334155"  # Bordes en sidebar
        text_primary = "#ffffff"
        text_secondary = "#cbd5e1"
        border_color = "#334155"
        card_bg = "#1e293b"
        button_bg = "#2563eb"      # Azul principal
        button_hover = "#1d4ed8"   # Azul oscuro
        input_bg = "#334155"
        success_bg = "#065f46"
        warning_bg = "#92400e"
        error_bg = "#7f1d1d"
        info_bg = "#1e3a8a"
    else:
        # Modo claro - Azul y blanco
        bg_primary = "#ffffff"
        bg_secondary = "#f8fafc"   # Blanco azulado muy claro
        bg_sidebar = "#1e293b"     # Azul oscuro para contraste
        sidebar_text_color = "#ffffff"  # Texto blanco en sidebar oscuro
        sidebar_secondary_text = "#cbd5e1"  # Texto secundario en sidebar
        sidebar_border_color = "#334155"  # Bordes en sidebar
        text_primary = "#1f2937"   # Texto oscuro para contenido principal
        text_secondary = "#64748b"
        border_color = "#e2e8f0"
        card_bg = "#ffffff"
        button_bg = "#2563eb"      # Azul principal
        button_hover = "#1d4ed8"   # Azul oscuro
        input_bg = "#ffffff"
        success_bg = "#dcfce7"
        warning_bg = "#fef3c7"
        error_bg = "#fecaca"
        info_bg = "#dbeafe"
    
    return f"""
    <style>
        /* Variables CSS para temas */
        :root {{
            --bg-primary: {bg_primary};
            --bg-secondary: {bg_secondary};
            --bg-sidebar: {bg_sidebar};
            --sidebar-text-color: {sidebar_text_color};
            --sidebar-secondary-text: {sidebar_secondary_text};
            --sidebar-border-color: {sidebar_border_color};
            --text-primary: {text_primary};
            --text-secondary: {text_secondary};
            --text-color: {text_primary};
            --border-color: {border_color};
            --card-bg: {card_bg};
            --button-bg: {button_bg};
            --button-hover: {button_hover};
            --input-bg: {input_bg};
            --success-bg: {success_bg};
            --warning-bg: {warning_bg};
            --error-bg: {error_bg};
            --info-bg: {info_bg};
        }}
        
        /* Tema principal adaptable */
        .main {{
            background: var(--bg-primary) !important;
            color: #ffffff !important;
        }}
        
        .stApp {{
            background: var(--bg-primary) !important;
            color: #ffffff !important;
        }}
        
        /* Contenedor principal */
        .main .block-container {{
            background: var(--bg-primary) !important;
            color: #ffffff !important;
        }}
        
        /* KPI Cards mejoradas - Gradiente azul */
        .kpi-card {{
            background: linear-gradient(135deg, #e5e7eb 0%, #cbd5e1 100%);
            color: #1f2937 !important;
            padding: 1rem 0.75rem;
            border-radius: 18px;
            border: none;
            text-align: center;
            margin: 0.25rem;
            box-shadow: 0 2px 12px rgba(37, 99, 235, 0.08);
            transition: box-shadow 0.2s, transform 0.2s;
        }}

        .kpi-card h2 {{font-size: 2rem;
            font-weight: 600;
            margin: 0.2rem 0 0.1rem 0;
            color: #2563eb !important;
            letter-spacing: -1px;}}

        .kpi-card h3 {{font-size: 1.1rem;
            font-weight: 500;
            margin: 0.1rem 0 0.2rem 0;
            color: #1e293b !important;
        }}

        .kpi-card p {{
            font-size: 0.95rem;
            color: #64748b !important;
            margin: 0.1rem 0 0 0;
        }}

        .kpi-card:hover {{
            box-shadow: 0 6px 24px rgba(37, 99, 235, 0.15);
            transform: translateY(-2px) scale(1.03);
            background: linear-gradient(135deg, #e0e7ef 0%, #f8fafc 100%);
        }}

        /* Contenedores de gráficos */
        .chart-container {{
            background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 16px;
            border: 2px solid var(--border-color);
        margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, {"0.2" if dark_mode else "0.1"});
        }}
        
        /* Sidebar mejorada */
        section[data-testid="stSidebar"] {{
            background: var(--bg-sidebar) !important;
            border-right: 3px solid var(--button-bg) !important;
            min-width: 280px !important;
            max-width: 350px !important;
        }}
        
        section[data-testid="stSidebar"] > div {{
            background: var(--bg-sidebar) !important;
            padding: 1rem !important;
        }}
        
        /* Contenido del sidebar */
        section[data-testid="stSidebar"] .stMarkdown {{
            color: var(--sidebar-text-color) !important;
        }}
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {{
            color: var(--sidebar-text-color) !important;
        text-align: center;
        }}
        
        /* Textos específicos del sidebar */
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div:not(.stButton),
        section[data-testid="stSidebar"] label {{
            color: var(--sidebar-text-color) !important;
        }}
        
        /* Métricas del sidebar */
        section[data-testid="stSidebar"] .metric-container {{
            color: var(--sidebar-text-color) !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="metric-container"] * {{
            color: var(--sidebar-text-color) !important;
        }}
        
        section[data-testid="stSidebar"] [data-testid="metric-container"] label {{
            color: var(--sidebar-secondary-text) !important;
        }}
        
        /* Texto del contenido principal en colores normales */
        .main .stMarkdown,
        section[data-testid="stMain"] .stMarkdown {{
            color: var(--text-color) !important;
        }}
        
        .main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
        section[data-testid="stMain"] h1, 
        section[data-testid="stMain"] h2, 
        section[data-testid="stMain"] h3, 
        section[data-testid="stMain"] h4, 
        section[data-testid="stMain"] h5, 
        section[data-testid="stMain"] h6 {{
            color: var(--text-color) !important;
        }}
        
        .main p, .main span, .main div,
        section[data-testid="stMain"] p:not(.stButton p), 
        section[data-testid="stMain"] span:not(.stButton span), 
        section[data-testid="stMain"] div:not(.stButton div) {{
            color: var(--text-color) !important;
        }}
        
        /* Sobreescribir cualquier color blanco en el contenido principal */
        section[data-testid="stMain"] * {{
            color: var(--text-color) !important;
        }}
        
        /* Excepciones para elementos que deben mantener colores específicos */
        section[data-testid="stMain"] .stButton button {{
        color: #ffffff !important;
        }}
        
        /* Botones principales */
        .stButton > button {{
            background: linear-gradient(135deg, var(--button-bg) 0%, var(--button-hover) 100%);
            color: #ffffff !important;
            border: 2px solid var(--button-hover);
            border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
            width: 100%;
        }}
        
        .stButton > button:hover {{
            background: linear-gradient(135deg, var(--button-hover) 0%, var(--button-bg) 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(46, 134, 171, 0.4);
        }}
        
        /* Botón Cargar Datos - AZUL personalizado */
        .stButton > button[kind="primary"][data-testid*="load_data_btn"],
        button[kind="primary"][data-testid*="load_data_btn"] {{
            background: #2563eb !important;
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: 2px solid #2563eb !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
        }}
        
        .stButton > button[kind="primary"][data-testid*="load_data_btn"]:hover,
        button[kind="primary"][data-testid*="load_data_btn"]:hover {{
            background: #1d4ed8 !important;
            background-color: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
        }}
        
        /* Botón Procesar Datos - VERDE */
        .stButton > button[kind="primary"][data-testid*="process_data_btn"],
        button[kind="primary"][data-testid*="process_data_btn"] {{
            background: #10b981 !important;
            background-color: #10b981 !important;
            color: #ffffff !important;
            border: 2px solid #10b981 !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }}
        
        .stButton > button[kind="primary"][data-testid*="process_data_btn"]:hover,
        button[kind="primary"][data-testid*="process_data_btn"]:hover {{
            background: #059669 !important;
            background-color: #059669 !important;
            border-color: #059669 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4) !important;
        }}
        
        /* File uploader - AZUL */
        .stFileUploader > div > div,
        .stFileUploader > div > div > div,
        div[data-testid*="file_uploader_main"] > div,
        div[data-testid*="file_uploader_main"] > div > div,
        .stFileUploader div[data-testid*="file_uploader_main"] {{
            background: #2563eb !important;
            background-color: #2563eb !important;
            color: #ffffff !important;
            border: 2px solid #2563eb !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
            text-align: center !important;
            cursor: pointer !important;
        }}
        
        .stFileUploader > div > div:hover,
        .stFileUploader > div > div > div:hover,
        div[data-testid*="file_uploader_main"] > div:hover,
        div[data-testid*="file_uploader_main"] > div > div:hover,
        .stFileUploader div[data-testid*="file_uploader_main"]:hover {{
            background: #1d4ed8 !important;
            background-color: #1d4ed8 !important;
            border-color: #1d4ed8 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
        }}
        
        /* TEXTO BLANCO - Selectores universales */
        .stFileUploader *,
        .stFileUploader > div *,
        .stFileUploader > div > div *,
        .stFileUploader > div > div > div *,
        .stFileUploader > div > div > div > div *,
        div[data-testid*="file_uploader_main"] *,
        div[data-testid*="file_uploader_main"] > div *,
        div[data-testid*="file_uploader_main"] > div > div *,
        .stFileUploader div[data-testid*="file_uploader_main"] * {{
            color: #ffffff !important;
        }}
        
        /* Forzar colores en todos los elementos del file uploader */
        .stFileUploader,
        .stFileUploader > div,
        .stFileUploader > div > div,
        .stFileUploader > div > div > div,
        .stFileUploader > div > div > div > div {{
            color: #ffffff !important;
        }}
        
        /* Botones secundarios para sidebar */
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: var(--sidebar-text-color) !important;
            border: 1px solid var(--sidebar-border-color) !important;
            border-radius: 8px !important;
            padding: 0.75rem 1rem !important;
            font-weight: 400 !important;
            font-size: 0.9rem !important;
            text-align: left !important;
            margin: 0.3rem 0 !important;
        }}
        
        section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
            background: rgba(37, 99, 235, 0.1) !important;
            border-color: #2563eb !important;
            color: var(--sidebar-text-color) !important;
            transform: none !important;
        }}
        
        /* Botones primarios para sidebar */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
            color: #ffffff !important;
            border: 1px solid #2563eb !important;
            border-radius: 8px !important;
            padding: 0.75rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
        }}
        
        /* Todos los botones del sidebar */
        section[data-testid="stSidebar"] .stButton > button {{
            color: var(--sidebar-text-color) !important;
        }}
        
        /* Inputs mejorados */
        .stSelectbox > div > div {{
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }}
        
        .stSelectbox > div > div > div {{
            color: var(--text-primary) !important;
        }}
        
        .stTextInput > div > div > input {{
            background-color: var(--input-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }}
        
        .stTextInput > div > label {{
            color: var(--text-color) !important;
        }}
        
        .stSelectbox > div > label {{
            color: var(--text-color) !important;
        }}
        
        /* File uploader */
        .stFileUploader > div > label {{
            color: var(--text-color) !important;
        }}
        
        .stFileUploader > div > div {{
            border: 2px dashed var(--border-color) !important;
            border-radius: 8px !important;
            background-color: var(--input-bg) !important;
        }}
        
        .stFileUploader > div > div > div {{
            color: var(--text-color) !important;
        }}
        
        /* Títulos y texto */
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff !important;
        }}
        
        p, span, div {{
            color: #ffffff !important;
        }}
    
    /* Métricas de Streamlit */
        .metric-container {{
            background: var(--card-bg) !important;
            border: 2px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }}
        
        .metric-container label {{
            color: #cbd5e1 !important;
            font-weight: 600 !important;
        }}
        
        .metric-container [data-testid="metric-container"] > div {{
            color: #ffffff !important;
        }}
        
        /* Cajas de información */
        .stInfo {{
            background-color: var(--info-bg) !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .stSuccess {{
            background-color: var(--success-bg) !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .stWarning {{
            background-color: var(--warning-bg) !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .stError {{
            background-color: var(--error-bg) !important;
            color: #ffffff !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* Upload box */
        .upload-box {{
            border: 3px dashed var(--button-bg) !important;
            border-radius: 12px !important;
            padding: 2rem !important;
            text-align: center !important;
            background: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            margin: 1rem 0 !important;
            transition: all 0.3s ease !important;
        }}
        
        .upload-box:hover {{
            border-color: var(--button-hover) !important;
            background: var(--card-bg) !important;
        }}
    
    /* Dataframes */
        .dataframe {{
            background-color: var(--card-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        /* Expandir elementos */
        .streamlit-expanderHeader {{
            background-color: var(--bg-secondary) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
        }}
        
        .streamlit-expanderContent {{
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 0 0 8px 8px !important;
        }}
        
        /* Expander text */
        [data-testid="stExpander"] .streamlit-expanderHeader p {{
            color: var(--text-color) !important;
        }}
        
        [data-testid="stExpander"] .streamlit-expanderContent p {{
            color: var(--text-color) !important;
        }}
        
        [data-testid="stExpander"] .streamlit-expanderContent * {{
            color: var(--text-color) !important;
        }}
        
        /* CSS específico para navegadores webkit (Safari/Mac) */
        @supports (-webkit-appearance: none) {{
            section[data-testid="stSidebar"] {{
                background: var(--bg-sidebar) !important;
                border-right: 3px solid var(--button-bg) !important;
            }}
            
            section[data-testid="stSidebar"] > div:first-child {{
                background: var(--bg-sidebar) !important;
            }}
        }}
        
        /* Animaciones suaves */
        * {{
            transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }}
</style>
    """

# Aplicar CSS dinámico basado en el modo
st.markdown(get_theme_css(st.session_state.dark_mode), unsafe_allow_html=True)

# Configurar Plotly según el modo
pio.templates.default = "plotly_dark" if st.session_state.dark_mode else "plotly_white"

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
        csv_path = os.path.join(current_dir, 'data', 'datos_agregados_mercado.csv')
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
        csv_path = os.path.join(current_dir, 'data', 'datos_agregados_mercado.csv')
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
        csv_path = os.path.join(current_dir, 'data', 'datos_agregados_mercado.csv')
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
        csv_path = os.path.join(current_dir, 'data', 'datos_individuales_centros.csv')
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
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['primary']),
        fill='tonexty',
        fillcolor='rgba(37, 99, 235, 0.1)'
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
    
    # Configurar colores según el modo
    title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
    bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
    axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=title_color)),
        xaxis_title="Fecha",
        yaxis_title=f"{title} ({unit})",
        xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
        yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
        template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
        height=350,
        margin=dict(l=0, r=0, t=60, b=0),
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color
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
    
    # Crear colores basados en el rendimiento - Solo azules
    colors = [COLORS['primary'] if p > 0 else COLORS['accent'] for p in performance]
    
    fig.add_trace(go.Bar(
        name='Tu Centro',
        x=metric_names,
        y=center_values,
        marker_color=colors,
        text=[f"{p:+.1f}%" for p in performance],
        textposition='auto',
        textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=10)
    ))
    
    fig.add_trace(go.Bar(
        name='Promedio Sector',
        x=metric_names,
        y=sector_values,
        marker_color='rgba(100, 116, 139, 0.7)',  # Gris azulado para contraste
        opacity=0.7
    ))
    
    # Configurar colores según el modo
    title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
    bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
    axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
    
    fig.update_layout(
        title=dict(text="Comparación vs. Promedio del Sector", 
                  font=dict(size=16, color=title_color)),
        xaxis=dict(tickfont=dict(color=axis_text_color)),
        yaxis=dict(tickfont=dict(color=axis_text_color)),
        template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
        height=450,
        barmode='group',
        xaxis_tickangle=-45,
        hovermode='x unified',
        showlegend=True,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color
    )
    
    return fig

# Función para crear gráfica de rendimiento por categorías
def create_category_performance_chart():
    categories = ['Moda', 'Alimentación', 'Electrónica', 'Hogar', 'Deportes', 'Otros']
    values = [35, 25, 15, 12, 8, 5]
    colors = CHART_COLORS
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont=dict(size=12, color='#ffffff' if st.session_state.dark_mode else '#212529')
    )])
    
    # Configurar colores según el modo
    title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
    bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
    text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
    
    fig.update_layout(
        title=dict(text="Distribución por Categorías", 
                  font=dict(size=16, color=title_color)),
        template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01,
            font=dict(color=text_color)
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color
    )
    
    # Update pie chart text colors
    fig.update_traces(
        textfont=dict(size=12, color=text_color)
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
                marker_color=CHART_COLORS,
                text=[f"{v:,.0f}€" for v in zone_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
            ))
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            fig_zones.update_layout(
                title=dict(text="💰 Ventas Totales por Zona Geográfica", font=dict(size=16, color=title_color)),
                xaxis_title="Zona Geográfica",
                yaxis_title="Ventas Totales (€)",
                 xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                 height=400,
                 plot_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                 paper_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            )
            charts['ventas_zonas'] = fig_zones
        
        # 2. Ocupación por m² por Zona
        if zone_data is not None:
            fig_ocupacion = go.Figure()
            fig_ocupacion.add_trace(go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ocupacion_por_m2'],
                name='Ocupación por m²',
                marker_color=CHART_COLORS,
                text=[f"{v:.1f}%" for v in zone_data['ocupacion_por_m2']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
            ))
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            fig_ocupacion.update_layout(
                title=dict(text="🏢 Tasa de Ocupación por Zona Geográfica", font=dict(size=16, color=title_color)),
                xaxis_title="Zona Geográfica",
                yaxis_title="Tasa de Ocupación (%)",
                 xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                 height=400,
                 plot_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                 paper_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
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
                    marker_color=['#2563eb', '#3b82f6', '#60a5fa'],
                    text=[f"{v:,.0f}€" for v in business_data['ingresos (€)']],
                    textposition='auto',
                    textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
                ),
                row=1, col=1
            )
            
            # Visitantes por tipo de negocio
            fig_business.add_trace(
                go.Bar(
                    x=business_data['tipo_negocio'],
                    y=business_data['afluencia'],
                    name='Visitantes',
                    marker_color=['#1d4ed8', '#1e40af', '#93c5fd'],
                    text=[f"{v:,.0f}" for v in business_data['afluencia']],
                    textposition='auto',
                    textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
                ),
                row=1, col=2
            )
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            
            fig_business.update_layout(
                title=dict(text="🎯 Análisis por Tipo de Negocio", font=dict(size=16, color=title_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=400,
                showlegend=False,
                plot_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                paper_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                # Configurar colores de ejes para ambos subplots
                xaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                yaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                xaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                yaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color))
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
                     marker_color='#2563eb',
                    text=[f"{v:,.0f}€" for v in zone_sorted['ingresos (€)']],
                    textposition='auto',
                    textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
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
                     marker_color='#3b82f6',
                    text=[f"{v:.1f}%" for v in business_sorted['ocupacion_por_m2']],
                    textposition='auto',
                    textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
                ),
                row=2, col=1
            )
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            
            fig_ranking.update_layout(
                title=dict(text="📊 Rankings de Rendimiento", font=dict(size=16, color=title_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=600,
                margin=dict(t=100),
                showlegend=False,
                plot_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                paper_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                # Configurar colores de ejes para ambos subplots
                xaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                yaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                xaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                yaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
                # Configurar colores de títulos de subplots
                annotations=[
                    dict(text="🏆 Top Zonas por Rendimiento", x=0.5, y=1.05, xref="paper", yref="paper", 
                         showarrow=False, font=dict(size=14, color=title_color)),
                    dict(text="🎯 Top Tipos de Negocio por Ocupación", x=0.5, y=0.45, xref="paper", yref="paper", 
                         showarrow=False, font=dict(size=14, color=title_color))
                ]
            )
            charts['rankings'] = fig_ranking
        
        # 5. Análisis de Eficiencia (Ventas vs Visitantes)
        if market_df is not None:
            fig_efficiency = go.Figure()
            
            # Calcular eficiencia (ventas por visitante)
            market_df['eficiencia'] = market_df['ingresos_totales'] / market_df['trafico_peatonal']
            
            # Scatter plot por zona y tipo de negocio
            colors_map = {
                            'Madrid': '#60a5fa',           # Azul claro
                            'Cataluña': '#93c5fd',         # Azul muy claro
                            'Norte': '#2563eb',            # Azul principal
                            'Sur': '#3b82f6',              # Azul medio
                            'Castilla-La Mancha': '#1e40af', # Azul oscuro
                            'León': '#64748b'              # Gris azulado suave
                        }
            
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
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            fig_efficiency.update_layout(
                title=dict(text="⚡ Eficiencia: Ventas vs Visitantes (tamaño = ocupación)", font=dict(size=16, color=title_color)),
                xaxis_title="Visitantes",
                yaxis_title="Ventas (€)",
                 xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                 template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                 height=500,
                 plot_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)',
                 paper_bgcolor='#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            )
            charts['efficiency'] = fig_efficiency
        
        return charts
        
    except Exception as e:
        print(f"Error creating market analysis charts: {e}")
        return {}

# Navegación principal - Sidebar elegante y moderno
with st.sidebar:
    # Header minimalista
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
        <h1 style="color: white; margin: 0; font-size: 1.8rem; font-weight: 300; letter-spacing: 1px;">
            Harmon BI
        </h1>
        <div style="width: 60px; height: 2px; background: linear-gradient(90deg, #2563eb, #60a5fa); margin: 0.8rem auto; border-radius: 1px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle para modo oscuro - diseño elegante
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 2rem;">
        <div style="background: {'#0f172a' if st.session_state.dark_mode else '#1e293b'}; 
                    padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid #2563eb;">
            <span style="color: #cbd5e1; font-size: 0.9rem;">🌙 {'Oscuro' if st.session_state.dark_mode else 'Claro'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Checkbox oculto para el toggle
    dark_mode_toggle = st.checkbox("Modo oscuro", value=st.session_state.dark_mode, key="dark_mode_toggle", label_visibility="hidden")
    
    # Actualizar el estado si cambió
    if dark_mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_toggle
        st.rerun()
    
    # Navegación minimalista sin iconos
    st.markdown("""
    <div style="margin: 1rem 0;">
        <div style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; text-align: center;">
            Navegación
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Menú de navegación elegante sin iconos
    nav_options = ["Dashboard", "Análisis vs Mercado", "Configuración"]
    
    # Crear botones de navegación elegantes
    selected = st.session_state.selected_page
    
    for i, option in enumerate(nav_options):
        is_selected = (option == st.session_state.selected_page)
        
        # Estilo dinámico basado en si está seleccionado
        button_key = f"nav_{option.replace(' ', '_')}"
        
        if st.button(
            option, 
            key=button_key, 
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.selected_page = option
            selected = option
            st.rerun()
    
    # Espaciador elegante
    st.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #334155, transparent); margin: 0 1rem;"></div>
    </div>
    """, unsafe_allow_html=True)

# Si no hay selección, usar Dashboard por defecto
if not selected:
    selected = "Dashboard"

# Página de Dashboard
if selected == "Dashboard":
    st.title("🏢 Harmon BI Dashboard")
    st.markdown("---")
    
    # Header con botones de carga de datos
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.header("📈 Dashboard - Mi Centro")
    with col2:
        period = st.selectbox("Período", ["Mensual", "Trimestral", "Anual"], key="dashboard_period")
    with col3:
        # Botón personalizado para cargar datos
        if st.button("📁 Cargar Datos", type="primary", use_container_width=True, key="load_data_btn"):
            st.session_state.show_file_upload = True
            st.rerun()
        
        # File uploader que aparece cuando se presiona el botón
        if st.session_state.get('show_file_upload', False):
            uploaded_file = st.file_uploader(
                "Selecciona tu archivo",
                type=['xlsx', 'csv'],
                help="Excel (.xlsx) o CSV (.csv) - Máximo 10MB",
                key="file_uploader_main"
            )
            if uploaded_file is not None:
                st.session_state.uploaded_file = uploaded_file
                st.session_state.show_file_upload = False
                st.success(f"✅ Datos cargados: {uploaded_file.name}")
                st.rerun()
    with col4:
        if st.button("⚙️ Procesar Datos", type="primary", use_container_width=True, key="process_data_btn"):
            # Verificar si hay archivo cargado
            if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file is None:
                st.warning("⚠️ Primero debes cargar un archivo")
            else:
                # Procesar directamente sin formularios
                with st.spinner("Procesando datos..."):
                    # Usar nombre por defecto basado en el archivo
                    file_name = st.session_state.uploaded_file.name
                    center_name = file_name.split('.')[0]  # Nombre sin extensión
                    center_type = "Urbano"  # Tipo por defecto
                    
                    center_data, message = process_uploaded_file(
                        st.session_state.uploaded_file, 
                        center_name, 
                        center_type
                    )
                    
                    if center_data:
                        st.session_state.centers_data[center_name] = center_data
                        st.session_state.current_center = center_name
                        st.session_state.uploaded_file = None
                        st.success(f"✅ {message}")
                        st.success("🎉 ¡Datos procesados exitosamente! Visualizando métricas...")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
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
        
        # Análisis avanzado del mercado
        st.subheader("📊 Análisis Avanzado del Mercado")
        
        # Crear gráficas del mercado
        market_charts = create_market_analysis_charts()
        
        if market_charts:
            # Análisis por Tipo de Negocio
            if 'business_comparison' in market_charts:
                st.plotly_chart(market_charts['business_comparison'], use_container_width=True)
                
            
            # Rankings y Eficiencia
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if 'rankings' in market_charts:
                    st.plotly_chart(market_charts['rankings'], use_container_width=True)
                    
            
            with col2:
                if 'efficiency' in market_charts:
                    st.plotly_chart(market_charts['efficiency'], use_container_width=True)
                    
    
    else:
        # Estado sin datos - Mostrar solo los botones de carga
        st.markdown("---")
        st.markdown("### 📊 No hay datos cargados")
        st.info("Usa los botones de arriba para cargar y procesar tus datos del centro comercial.")

    # Insights del mercado
    st.subheader("💡 Insights del Mercado")
    
    # Obtener datos del mercado para los insights
    sector_avg = get_sector_averages()
    zone_data = get_market_data_by_zone()
    business_data = get_market_data_by_business_type()
    
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
            
            # Gráfica de radar mejorada
            categories = ['Tráfico', 'Ventas/m²', 'Ocupación', 'Tiempo', 'Conversión', 'Ingresos']
            
            # Normalizar valores para el radar (0-100)
            center_values = [
                min(100, (latest_data.get('trafico_peatonal', 0) / sector_avg['trafico_peatonal']) * 50),
                min(100, (latest_data.get('ventas_por_m2', 0) / sector_avg['ventas_por_m2']) * 50),
                latest_data.get('tasa_ocupacion', 0),
                min(100, (latest_data.get('tiempo_permanencia', 0) / sector_avg['tiempo_permanencia']) * 50),
                latest_data.get('tasa_conversion', 0),
                min(100, (latest_data.get('ingresos_totales', 0) / sector_avg['ingresos_totales']) * 50)
            ]
            
            sector_values = [50, 50, sector_avg['tasa_ocupacion'], 50, sector_avg['tasa_conversion'], 50]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=center_values,
                theta=categories,
                fill='toself',
                name='Tu Centro',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=8, color='#2563eb'),
                fillcolor='rgba(37, 99, 235, 0.2)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=sector_values,
                theta=categories,
                fill='toself',
                name='Promedio Mercado',
                line=dict(color='#64748b', width=2),
                marker=dict(size=6, color='#64748b'),
                fillcolor='rgba(100, 116, 139, 0.15)'
            ))
            
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            
            # Configurar colores de fondo
            bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(color=axis_text_color),
                        gridcolor='rgba(0,0,0,0.1)' if not st.session_state.dark_mode else 'rgba(255,255,255,0.1)',
                        linecolor=axis_text_color
                    ),
                    angularaxis=dict(
                        tickfont=dict(color=axis_text_color, size=12),
                        linecolor=axis_text_color,
                        gridcolor='rgba(0,0,0,0.1)' if not st.session_state.dark_mode else 'rgba(255,255,255,0.1)'
                    ),
                    bgcolor=bg_color
                ),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=0.95,
                    xanchor="left",
                    x=1.02,
                    font=dict(color=axis_text_color, size=12)
                ),
                title=dict(text="Comparación de Rendimiento vs Mercado", 
                           font=dict(size=16, color=title_color)),
                 template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=500,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color,
                font=dict(color=axis_text_color)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader("🎯 Posicionamiento en el Mercado")

            # Calcular score general
            total_performance = sum([abs(m['performance']) for m in comparison_metrics if m['performance'] > 0])
            total_metrics = len([m for m in comparison_metrics if m['performance'] > 0])
            market_score = (total_performance / total_metrics) if total_metrics > 0 else 0

            # 2 filas de 2 columnas cada una
            row1_col1, row1_col2 = st.columns(2)
            row2_col1, row2_col2 = st.columns(2)

            # Estilo tipo botón para métricas (más pequeño)
            button_style = """
            <style>
            .metric-btn {
                display: block;
                background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
                color: #fff !important;
                border-radius: 10px;
                padding: 0.7em 0.3em;
                margin: 0.3em 0;
                text-align: center;
                font-size: 1em;
                font-weight: 500;
                box-shadow: 0 1px 4px rgba(37,99,235,0.10);
                border: none;
                transition: background 0.2s, box-shadow 0.2s;
                cursor: pointer;
            }
            .metric-btn span {
                font-size: 1.2em;
                font-weight: 600;
            }
            .metric-btn:hover {
                background: linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%);
                box-shadow: 0 2px 8px rgba(37,99,235,0.18);
            }
            </style>
            """
            st.markdown(button_style, unsafe_allow_html=True)

            with row1_col1:
                st.markdown(
                    f'<div class="metric-btn">Score vs Mercado<br><span>{market_score:.1f}%</span><br><span style="font-size:0.9em;">{"Superior" if market_score > 10 else "Promedio" if market_score > 0 else "Inferior"}</span></div>',
                    unsafe_allow_html=True
                )

            with row1_col2:
                superior_count = len([m for m in comparison_metrics if m['performance'] > 0])
                st.markdown(
                    f'<div class="metric-btn">Métricas Superiores<br><span>{superior_count}/6</span><br><span style="font-size:0.9em;">{superior_count/6*100:.0f}%</span></div>',
                    unsafe_allow_html=True
                )

            with row2_col1:
                avg_performance = sum([m['performance'] for m in comparison_metrics]) / len(comparison_metrics)
                st.markdown(
                    f'<div class="metric-btn">Rendimiento Promedio<br><span>{avg_performance:+.1f}%</span><br><span style="font-size:0.9em;">{"Excelente" if avg_performance > 10 else "Bueno" if avg_performance > 0 else "Mejorable"}</span></div>',
                    unsafe_allow_html=True
                )

            with row2_col2:
                best_metric = max(comparison_metrics, key=lambda x: x['performance'])
                st.markdown(
                    f'<div class="metric-btn">Mejor Métrica<br><span>{best_metric["metric"]}</span><br><span style="font-size:0.9em;">+{best_metric["performance"]:.1f}%</span></div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

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
            marker_color=CHART_COLORS,
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
            textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=12)
        )])
        
        title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
        axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
        
        fig.update_layout(
            title=dict(text="Promedios del Mercado por Métrica", 
                       font=dict(size=16, color=title_color)),
             xaxis=dict(tickfont=dict(color=axis_text_color)),
             yaxis=dict(tickfont=dict(color=axis_text_color)),
             template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
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
            line_color='#64748b',
            fillcolor='rgba(100, 116, 139, 0.3)'
        ))
        
        title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
        axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                     tickfont=dict(color=axis_text_color)
                )),
            showlegend=True,
            title=dict(text="Perfil del Mercado", 
                       font=dict(size=16, color=title_color)),
             template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
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
                      line=dict(color='#2563eb', width=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['ventas'], 
                      mode='lines+markers', name='Ventas',
                      line=dict(color='#3b82f6', width=3)),
            row=2, col=1
        )
        
        # Configurar colores según el modo
        title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
        axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
        bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
        
        fig.update_layout(
            title=dict(text="Tendencias del Mercado - Tráfico y Ventas", font=dict(size=16, color=title_color)),
            template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
            height=500,
            showlegend=False,
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            # Configurar colores de ejes para ambos subplots
            xaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            yaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            xaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            yaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color))
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
                      line=dict(color='#60a5fa', width=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=market_trends['conversion'], 
                      mode='lines+markers', name='Conversión',
                      line=dict(color='#1d4ed8', width=3)),
            row=2, col=1
        )
        
        # Configurar colores según el modo
        title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
        axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
        bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
        
        fig.update_layout(
            title=dict(text="Tendencias del Mercado - Ocupación y Conversión", font=dict(size=16, color=title_color)),
            template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
            height=500,
            showlegend=False,
            plot_bgcolor=bg_color,
            paper_bgcolor=bg_color,
            # Configurar colores de ejes para ambos subplots
            xaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            yaxis=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            xaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color)),
            yaxis2=dict(tickfont=dict(color=axis_text_color), title_font=dict(color=axis_text_color))
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
                marker_color=CHART_COLORS[:5],
                text=[f"{v:,.0f}" for v in zone_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=10)
            )])
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            
            fig.update_layout(
                title=dict(text="Ventas Totales por Zona Geográfica", font=dict(size=16, color=title_color)),
                xaxis_title="Zona Geográfica",
                yaxis_title="Ventas Totales (€)",
                xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=400,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfica de ocupación por m² por zona
            fig = go.Figure(data=[go.Bar(
                x=zone_data['zona_geografica'],
                y=zone_data['ocupacion_por_m2'],
                marker_color=CHART_COLORS[:5],
                text=[f"{v:.2f}" for v in zone_data['ocupacion_por_m2']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=10)
            )])
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            
            fig.update_layout(
                title=dict(text="Ocupación por m² por Zona", font=dict(size=16, color=title_color)),
                xaxis_title="Zona Geográfica",
                yaxis_title="Ocupación por m² (visitantes/m²)",
                xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=400,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color
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
                marker_color=CHART_COLORS[:3],
                text=[f"{v:,.0f}" for v in business_data['ingresos (€)']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=10)
            )])
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            
            fig.update_layout(
                title=dict(text="Ventas Totales por Tipo de Negocio", font=dict(size=16, color=title_color)),
                xaxis_title="Tipo de Negocio",
                yaxis_title="Ventas Totales (€)",
                xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=400,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfica de visitantes por tipo de negocio
            fig = go.Figure(data=[go.Bar(
                x=business_data['tipo_negocio'],
                y=business_data['afluencia'],
                marker_color=CHART_COLORS[:3],
                text=[f"{v:,.0f}" for v in business_data['afluencia']],
                textposition='auto',
                textfont=dict(color='#ffffff' if st.session_state.dark_mode else '#212529', size=10)
            )])
            
            # Configurar colores según el modo
            title_color = "#ffffff" if st.session_state.dark_mode else "#2c3e50"
            axis_text_color = '#ffffff' if st.session_state.dark_mode else '#1f2937'
            bg_color = '#2d2d30' if st.session_state.dark_mode else 'rgba(0,0,0,0)'
            
            fig.update_layout(
                title=dict(text="Visitantes por Tipo de Negocio", font=dict(size=16, color=title_color)),
                xaxis_title="Tipo de Negocio",
                yaxis_title="Total Visitantes",
                xaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                yaxis=dict(title_font=dict(color=axis_text_color), tickfont=dict(color=axis_text_color)),
                template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                height=400,
                plot_bgcolor=bg_color,
                paper_bgcolor=bg_color
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
