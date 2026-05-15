import streamlit as st
from pyairtable import Api
from datetime import date
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    
    /* Botón de WhatsApp estilizado */
    .whatsapp-button {
        background-color: #25D366;
        color: white !important;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 38px; /* Altura similar al botón de Streamlit */
        transition: 0.3s;
    }
    .whatsapp-button:hover {
        background-color: #128C7E;
        text-decoration: none;
    }
    
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ESTADO DE SESIÓN ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False
if 'datos_resumen' not in st.session_state:
    st.session_state.datos_resumen = {}

# --- 4. CREDENCIALES ---
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = st.secrets["BASE_ID"]
    TABLE_NAME = "RMA ALTAVISTA" 
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)
except Exception:
    st.error("Error en credenciales.")
    st.stop()

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align: center;'>Solicitud de RMA / DEVOLUCION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Recuerde que el producto debe contar su embalaje / blíster o caja.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. LÓGICA DE PANTALLAS ---
with st.container(border=True):
    if st.session_state.enviado:
        st.success("¡Solicitud enviada con éxito!")
        st.markdown("### ¿Qué desea hacer ahora?")
        
        # FILA DE BOTONES: Cargar otro (Izquierda) | WhatsApp (Derecha)
        col_izq, col_der = st.columns([2, 1])
        
        with col_izq:
            if st.button("CARGAR OTRO PRODUCTO", use_container_width=True):
                st.session_state.enviado = False
                st.session_state.datos_resumen = {}
                st.rerun()
        
        with col_der:
            d = st.session_state.datos_resumen
            msg = (f"Hola ALTAVISTA SA, envié un formulario:\n\n"
                   f"👤 Cliente: {d.get('cliente')}\n"
                   f"📦 Producto: {d.get('producto')}\n"
                   f"🔢 Serial: {d.get('serial')}\n"
                   f"⚠️ Falla: {d.get('falla')}")
            link = f"https://wa.me/5493433002458?text={urllib.parse.quote(msg)}"
            
            st.markdown(f"""
                <a href="{link}" target="_blank" class="whatsapp-button">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="18">
                    Contactarnos
                </a>
                """, unsafe_allow_html=True)
    else:
        # FORMULARIO
        f1c1, f1c2 = st.columns(2)
        with f1c1:
            cliente = st.text_input("Nombre / Razón Social").upper()
        with f1c2:
            serial = st.text_input("Serial (SN - ASA)")
            
        f2c1, f2c2 = st.columns(2)
        with f2c1:
            producto = st.text_input("Producto")
        with f2c2:
            fecha_compra = st.date_input("Fecha de Compra", max_value=date.today(), format="DD/MM/YYYY")

        motivo = st.selectbox("Motivo", ["Seleccione una opción", "RMA", "Devolución"])
        descripcion = st.text_area("Descripción de la falla")

        st.markdown("---")
        opcion_contacto = st.radio("Método de contacto", ["WhatsApp", "Correo"], horizontal=True)
        contacto = st.text_input("Dato de contacto (Nro o Mail)")

        if st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True):
            if not cliente or not serial or motivo == "Seleccione una opción" or not contacto:
                st.error("Complete los campos obligatorios.")
            else:
                try:
                    st.session_state.datos_resumen = {
                        "cliente": cliente, "producto": producto,
                        "serial": serial, "falla": descripcion
                    }
                    table.create({
                        "Cliente": cliente, "Producto": producto, "Serial": serial,
                        "Compra": str(fecha_compra), "Motivo del trámite": motivo, 
                        "diagnostico": descripcion, "Estado del RMA": "PENDIENTE",
                        "Ingreso": str(date.today())
                    })
                    st.session_state.enviado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
