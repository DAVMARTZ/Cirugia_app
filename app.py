from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os

import os
import json
import uuid
import numpy as np
import pandas as pd
import streamlit as st

from datetime import date, datetime, timedelta
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# CSS Loader
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader, simpleSplit

from auth import login
from cirugia import render_cirugia
from historia_clinica_paciente import render_historia_clinica
# =========================
# CONFIG
# =========================
RUTA_CIRUGIAS = "data/cirugias.csv"
RUTA_FIRMAS = "data/firmas"
RUTA_PDFS = "data/pdfs"
RUTA_LOGO = "assets/logo.png"

os.makedirs("data", exist_ok=True)
os.makedirs(RUTA_FIRMAS, exist_ok=True)
os.makedirs(RUTA_PDFS, exist_ok=True)



# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(
    page_title="Gestión de Cirugías",
    page_icon="🏥",
    layout="wide"
)

# Load Styles
try:
    local_css("assets/style.css")
except:
    pass

# =========================
# SESIÓN
# =========================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    login()
    st.stop()

# =========================
# FUNCIONES
# =========================
def cargar_csv(ruta, columnas):
    try:
        return pd.read_csv(ruta)
    except:
        return pd.DataFrame(columns=columnas)

# =========================
# DATOS
# =========================
pacientes = cargar_csv(
    "data/pacientes.csv",
    ["id", "nombre", "documento", "edad", "sexo"]
)

cirugias = cargar_csv(
    "data/cirugias.csv",
    ["id", "paciente", "procedimiento", "fecha", "cirujano"]
)

checklist = cargar_csv(
    "data/checklist.csv",
    ["paciente", "fecha", "fase", "item", "estado"]
)

# SIDEBAR DESIGN
with st.sidebar:
    st.markdown('<div style="margin-top: -50px;"></div>', unsafe_allow_html=True)
    if os.path.exists(RUTA_LOGO):
        st.image(RUTA_LOGO, width=150)
    else:
        st.title("🏥 CirugíaApp")
    
    st.markdown(f"""
        <div style="background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <p style="margin:0; font-size: 0.8em; opacity: 0.8;">USUARIO ACTIVO</p>
            <p style="margin:0; font-weight: bold; font-size: 1.1em;">{st.session_state['usuario']}</p>
            <p style="margin:0; font-size: 0.9em; opacity: 0.9;">{st.session_state['rol']}</p>
        </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navegación Principal",
        [
            "Inicio",
            "Historial de Pacientes",
            "Cirugía",
            "Historia Clínica del Paciente"
        ]
    )
    
    # Espaciador para empujar el botón hacia abajo
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# =========================
# PANTALLAS
# =========================
if menu == "Inicio":
    st.markdown("""
        <div style="background-color: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); margin-bottom: 30px;">
            <h1 style="margin:0;">🏥 Bienvenido al Sistema de Gestión de Cirugías</h1>
            <p style="color: #64748b; font-size: 1.2em; margin-top: 10px;">
                Plataforma de control clínico y seguimiento de protocolos OMS.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-container">
                <p class="metric-label">Pacientes Registrados</p>
                <p class="metric-value">""" + str(len(pacientes)) + """</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="metric-container" style="border-bottom-color: #10b981;">
                <p class="metric-label">Cirugías Realizadas</p>
                <p class="metric-value">""" + str(len(cirugias)) + """</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="metric-container" style="border-bottom-color: #f59e0b;">
                <p class="metric-label">Checklists Completados</p>
                <p class="metric-value">""" + str(len(checklist)) + """</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Consejo del día:** Recuerde siempre verificar la identidad del paciente antes de iniciar cualquier procedimiento quirúrgico.")

# =========================
elif menu == "Cirugía":
   render_cirugia()


# =========================
elif menu == "Historial de Pacientes":
    st.markdown("""
        <div style="background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px;">
            <h1 style="margin:0;">📋 Historial de Pacientes</h1>
            <p style="color: #64748b;">Consulte y filtre la base de datos de pacientes registrados.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Buscador
    busqueda = st.text_input("🔍 Buscar por nombre o documento", placeholder="Ej: Juan Pérez o 1010...")
    
    if busqueda:
        df_filtrado = pacientes[
            pacientes["nombre_paciente"].str.contains(busqueda, case=False, na=False) |
            pacientes["numero_documento"].astype(str).str.contains(busqueda, na=False)
        ]
    else:
        df_filtrado = pacientes

    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    
    st.info(f"Mostrando {len(df_filtrado)} pacientes de un total de {len(pacientes)}.")


#==================================
elif menu == "Historia Clínica del Paciente":
   render_historia_clinica()