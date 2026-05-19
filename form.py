import streamlit as st
from pyairtable import Api
from datetime import date
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- LIMPIEZA VISUAL EXTENSIVA (CSS) ---
st.markdown("""
    <style>
    /* Oculta los carteles flotantes "Press Enter to submit" e instrucciones de entrada de Streamlit */
    div[data-testid="stTextInput"] [data-testid="InputInstructions"],
    div[data-testid="stTextArea"] [data-testid="InputInstructions"],
    div[data-testid="stInputInstructions"],
    .stInputInstructions,
    small {
        display: none !important;
    }
    
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 2rem;
    }

    /* Estilo personalizado y pulido para el botón nativo de WhatsApp con el logo */
    .whatsapp-btn {
        background-color: #25D366;
        color: white !important;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        border-radius: 8px;
        font-weight: 500;
        border: none;
        font-size: 14px;
        line-height: 1.6;
        width: 100%;
        height: 38px; /* Sincronizado exactamente con la altura de los botones de Streamlit */
    }
    .whatsapp-btn:hover {
        background-color: #20ba5a;
        text-decoration: none;
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
        
        # Obtener los datos resguardados en el estado de la sesión
        d = st.session_state.resumen_rma
        
        # Armado estructurado del mensaje para WhatsApp
        texto_ws = (
            f"Hola ALTAVISTA SA, acabo de enviar una solicitud de RMA / DEVOLUCION:\n\n"
            f"👤 *Cliente:* {d.get('cliente', '')}\n"
            f"📦 *Producto:* {d.get('producto', '')}\n"
            f"🔢 *Serial:* {d.get('serial', '')}\n"
            f"⚠️ *Falla:* {d.get('falla', '')}"
        )
        texto_encoded = urllib.parse.quote(texto_ws)
        link_whatsapp = f"https://wa.me/5493433002458?text={texto_encoded}"
        
        # Distribución en dos columnas simétricas para los botones de acción final
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("CARGAR OTRO PRODUCTO", type="secondary", use_container_width=True):
                st.session_state.enviado = False
                st.session_state.resumen_rma = {}
                st.rerun()
                
        with col_btn2:
            # Inyección limpia del enlace con el vector SVG oficial de WhatsApp
            st.markdown(f"""
                <a href="{link_whatsapp}" target="_blank" class="whatsapp-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12.004 2c-5.51 0-9.99 4.49-9.99 10 0 1.91.54 3.7 1.48 5.24l-1.4 5.1 5.23-1.37c1.48.81 3.16 1.27 4.93 1.27 5.51 0 10-4.49 10-10s-4.49-10-10-10zm4.87 14.15c-.21.58-1.22 1.13-1.68 1.19-.46.06-.91.08-2.84-.68-2.47-.97-4.05-3.48-4.17-3.64-.12-.17-1.04-1.38-1.04-2.63 0-1.25.65-1.87.88-2.12.23-.25.5-.31.67-.31.17 0 .33.01.48.01.16.01.37-.06.57.42.21.5.73 1.77.79 1.9.06.12.1.27.02.44-.08.16-.12.27-.25.42-.12.15-.26.33-.37.45-.12.12-.25.26-.11.5.15.24.66 1.09 1.42 1.76.98.86 1.8 1.13 2.06 1.25.25.13.4.1.55-.07.15-.17.65-.75.82-.1.17.15.34.42.92.71.58.29 3.46 1.71 3.54 1.75.08.04.13.19.05.42z"/>
                    </svg>
                    Contactanos
                </a>
                """, unsafe_allow_html=True)
            
    else:
        # FILA 1: Cliente y Serial
        fila1_col1, fila1_col2 = st.columns(2)
        with fila1_col1:
            cliente = st.text_input("Nombre / Razón Social", placeholder="Ej: Juan Pérez o Empresa S.A.").upper()
        with fila1_col2:
            serial = st.text_input("Serial (SN - ASA)", placeholder="U
