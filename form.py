import streamlit as st
from pyairtable import Api
from datetime import date
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- LIMPIEZA VISUAL EXTENSIVA Y ESTILOS PARA EL BOTÓN DE WHATSAPP ---
st.markdown("""
    <style>
    /* Oculta de raíz los carteles flotantes "Press Enter to submit" de Streamlit */
    div[data-testid="stTextInput"] [data-testid="InputInstructions"],
    div[data-testid="stTextArea"] [data-testid="InputInstructions"],
    div[data-testid="stInputInstructions"],
    .stInputInstructions {
        display: none !important;
    }
    
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 2rem;
    }

    /* Estilo personalizado para el botón de WhatsApp (Simula perfectamente el diseño nativo primary de Streamlit) */
    .btn-whatsapp-custom {
        background-color: #25D366;
        color: white !important;
        border: 1px solid #25D366;
        padding: 0px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        border-radius: 8px;
        font-weight: 400;
        font-size: 14px;
        font-family: inherit;
        width: 100%;
        height: 38px; /* Altura exacta del st.button estándar de Streamlit */
        box-sizing: border-box;
        cursor: pointer;
        transition: background-color 0.16s ease 0s, border-color 0.16s ease 0s;
    }
    .btn-whatsapp-custom:hover {
        background-color: #20ba5a;
        border-color: #20ba5a;
        text-decoration: none;
    }
    .btn-whatsapp-custom svg {
        flex-shrink: 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False
if 'resumen_rma' not in st.session_state:
    st.session_state.resumen_rma = {}

# --- CREDENCIALES ---
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = st.secrets["BASE_ID"]
    TABLE_NAME = "RMA ALTAVISTA" 
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)
except Exception:
    st.error("Error: No se pudieron cargar las credenciales.")
    st.stop()

# --- CABECERA ---
st.markdown("<h1 style='text-align: center;'>Solicitud de RMA / DEVOLUCION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Recuerde que el producto debe contar su embalaje / blíster o caja. NO SE ACEPTARÁN PRODUCTOS SIN CAJA NI NUMERO DE SERIE.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- CUERPO DEL FORMULARIO ---
with st.container(border=True):
    if st.session_state.enviado:
        st.success("¡Solicitud enviada con éxito! En breve le asignaremos su número de RMA.")
        
        # Recuperamos la información guardada temporalmente en la sesión
        d = st.session_state.resumen_rma
        
        # Mensaje limpio con " - " para WhatsApp
        texto_ws = (
            f"Hola ALTAVISTA SA, acabo de enviar una solicitud de RMA / DEVOLUCION:\n\n"
            f"- *Cliente:* {d.get('cliente', '')}\n"
            f"- *Producto:* {d.get('producto', '')}\n"
            f"- *Serial:* {d.get('serial', '')}\n"
            f"- *Falla:* {d.get('falla', '')}"
        )
        texto_encoded = urllib.parse.quote(texto_ws)
        link_whatsapp = f"
