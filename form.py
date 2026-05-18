import streamlit as st
from pyairtable import Api
from datetime import date
import urllib.parse

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- 2. ESTILOS VISUALES (LIMPIEZA DE INTERFAZ Y OCULTAR AYUDAS) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    /* TRUCO EFECTIVO: Oculta por completo el texto "Press Enter to submit" de Streamlit */
    [data-testid="stTextInput"] aria-label, 
    [data-testid="stInputInstructions"] {
        display: none !important;
    }
    
    /* Estilo personalizado para el botón de WhatsApp con el logo oficial */
    .whatsapp-button {
        background-color: #25D366;
        color: white !important;
        padding: 14px 20px;
        text-align: center;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        border-radius: 8px;
        font-weight: bold;
        margin-top: 15px;
        border: none;
        font-size: 16px;
    }
    .whatsapp-button:hover {
        background-color: #20ba5a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE ESTADO ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False
if 'datos_resumen' not in st.session_state:
    st.session_state.datos_resumen = {}

# --- 4. CONEXIÓN CON AIRTABLE ---
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = st.secrets["BASE_ID"]
    TABLE_NAME = "RMA ALTAVISTA" 
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)
except Exception:
    st.error("Error crítico: Verifique los Secrets en Streamlit Cloud.")
    st.stop()

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align: center;'>Solicitud de RMA / DEVOLUCION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Recuerde que el producto debe contar su embalaje / blíster o caja. NO SE ACEPTARÁN PRODUCTOS SIN CAJA NI NUMERO DE SERIE.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. CUERPO DEL FORMULARIO / PANTALLA DE ÉXITO ---
with st.container(border=True):
    if st.session_state.enviado:
        # PANTALLA DE ÉXITO
        st.success("¡Solicitud enviada con éxito! En breve le asignaremos su número de RMA.")
        
        st.markdown("### ¿Qué desea hacer ahora?")
        
        # Lógica de WhatsApp
        d = st.session_state.datos_resumen
        texto_ws = (
            f"Hola ALTAVISTA SA, acabo de enviar una solicitud de RMA / DEVOLUCION:\n\n"
            f"👤 *Cliente:* {d.get('cliente')}\n"
            f"📦 *Producto:* {d.get('producto')}\n"
            f"🔢 *Serial:* {d.get('serial')}\n"
            f"⚠️ *Falla:* {d.get('falla')}"
        )
        texto_encoded = urllib.parse.quote(texto_ws)
        link_whatsapp = f"https://wa.me/5493433002458?text={texto_encoded}"
        
        # Mensaje interactivo con botón "Contactanos" y logo en SVG
        st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank" class="whatsapp-button">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.004 2c-5.51 0-9.99 4.49-9.99 10 0 1.91.54 3.7 1.48 5.24l-1.4 5.1 5.23-1.37c1.48.81 3.16 1.27 4.93 1.27 5.51 0 10-4.49 10-10s-4.49-10-10-10zm4.87 14.15c-.21.58-1.22 1.13-1.68 1.19-.46.06-.91.08-2.84-.68-2.47-.97-4.05-3.48-4.17-3.64-.12-.17-1.04-1.38-1.04-2.63 0-1.25.65-1.87.88-2.12.23-.25.5-.31.67-.31.17 0 .33.01.48.01.16.01.37-.06.57.42.21.5.73 1.77.79 1.9.06.12.1.27.02.44-.08.16-.12.27-.25.42-.12.15-.26.33-.37.45-.12.12-.25.26-.11.5.15.24.66 1.09 1.42 1.76.98.86 1.8 1.13 2.06 1.25.25.13.4.1.55-.07.15-.17.65-.75.82-.1.17.15.34.42.92.71.58.29 3.46 1.71 3.54 1.75.08.04.13.19.05.42z"/>
                </svg>
                Contactanos
            </a>
            """, unsafe_allow_html=True)
        
        st.write("") 
        
        if st.button("CARGAR OTRO PRODUCTO", type="secondary", use_container_width=True):
            st.session_state.enviado = False
            st.session_state.datos_resumen = {}
            st.rerun()
            
    else:
        # CAMPOS NORMALES DE ENTRADA DIRECTA
        f1col1, f1col2 = st.columns(2)
        with f1col1:
            cliente = st.text_input("Nombre / Razón Social", placeholder="Ej: Juan Pérez").upper()
        with f1col2:
            serial = st.text_input("Serial (SN - ASA)", placeholder="Ubicado en la etiqueta")

        f2col1, f2col2 = st.columns(2)
        with f2col1:
            producto = st.text_input("Producto", placeholder="Ingrese nombre de producto")
        with f2col2:
            fecha_compra = st.date_input("Fecha de Compra", max_value=date.today(), format="DD/MM/YYYY")

        motivo = st.selectbox("Motivo del trámite", options=["Seleccione una opción", "RMA", "Devolución"])
        descripcion = st.text_area("Descripción detallada", placeholder="Describa el motivo o la falla...")

        st.markdown("---")
        st.markdown("### Método de Contacto")
        opcion_contacto = st.radio("¿Cómo prefiere que nos contactemos?", options=["WhatsApp", "Correo Electrónico"], horizontal=True)

        tel, mail = "", ""
        if opcion_contacto == "WhatsApp":
            tel = st.text_input("Número de WhatsApp", placeholder="Ej: +5493433002458")
        else:
            mail = st.text_input("Dirección de Correo Electrónico", placeholder="Ej: correo@prueba.com")

        st.markdown("---")
        
        if st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True):
            # EVALUACIÓN CONDICIONAL ESTRICTA DE LOS CAMPOS OBLIGATORIOS
            contacto_ok = False
            if opcion_contacto == "WhatsApp" and tel.strip() != "":
                contacto_ok = True
            elif opcion_contacto == "Correo Electrónico" and mail.strip() != "":
                contacto_ok = True
                
            if not cliente or not producto or not serial or motivo == "Seleccione una opción" or not contacto_ok:
                st.error("Por favor, complete todos los campos obligatorios.")
            else:
                try:
                    # Guardar variables en sesión para el mensaje del link
                    st.session_state.datos_resumen = {
                        "cliente": cliente, "producto": producto,
                        "serial": serial, "falla": descripcion
                    }
                    
                    # Escritura limpia en las columnas de Airtable
                    table.create({
                        "Cliente": cliente,
                        "Producto": producto,
                        "Serial": serial,
                        "Compra": str(fecha_compra),
                        "Motivo del trámite": motivo, 
                        "Falla": descripcion,          
                        "diagnostico": "",             
                        "Telefono": tel,      
                        "Email": mail,            
                        "Estado del RMA
