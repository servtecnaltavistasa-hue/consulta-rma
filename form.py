import streamlit as st
from pyairtable import Api
from datetime import date

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- 2. ESTILOS VISUALES (LIMPIEZA DE INTERFAZ) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    [data-testid="stStatusWidget"] {display: none;}
    
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE ESTADO ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

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
        st.success("¡Solicitud enviada con éxito! En breve le asignaremos su número de RMA.")
        
        if st.button("REALIZAR NUEVA SOLICITUD", type="primary", use_container_width=True):
            st.session_state.enviado = False
            st.rerun()
            
    else:
        # CAMPOS DEL FORMULARIO
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
            # Cambio solicitado: Placeholder para WhatsApp
            tel = st.text_input("Número de WhatsApp", placeholder="+5493...")
        else:
            # Cambio solicitado: Placeholder para Correo
            mail = st.text_input("Dirección de Correo Electrónico", placeholder="correo@email.com")

        st.markdown("---")
        
        if st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True):
            contacto_val = tel if opcion_contacto == "WhatsApp" else mail
            if not cliente or not producto or not serial or motivo == "Seleccione una opción" or not contacto_val:
                st.error("Por favor, complete todos los campos obligatorios.")
            else:
                try:
                    table.create({
                        "Cliente": cliente,
                        "Producto": producto,
                        "Serial": serial,
                        "Compra": str(fecha_compra),
                        "Motivo del trámite": motivo, 
                        "diagnostico": descripcion,
                        "Telefono": tel,      
                        "Email": mail,            
                        "Estado del RMA": "PENDIENTE",
                        "Ingreso": str(date.today())
                    })
                    st.session_state.enviado = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al enviar: {e}")
