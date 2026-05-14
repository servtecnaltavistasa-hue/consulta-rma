import streamlit as st
from pyairtable import Api
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- LIMPIEZA VISUAL (CSS) ---
st.markdown("""
    <style>
    div[data-testid="stTextInput"] [data-testid="InputInstructions"] { display: none; }
    div[data-testid="stTextArea"] [data-testid="InputInstructions"] { display: none; }
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'enviado' not in st.session_state:
    st.session_state.enviado = False

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
st.markdown("<h1 style='text-align: center;'>Solicitud de Gestión</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Complete los datos para iniciar su trámite.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- CUERPO DEL FORMULARIO ---
with st.container(border=True):
    # LÓGICA DE PANTALLA DE ÉXITO
    if st.session_state.enviado:
        st.success("¡Solicitud enviada con éxito! El trámite ha sido registrado correctamente.")
        
        # Al presionar este botón, cambiamos el estado y Streamlit recarga solo sin errores
        if st.button("REALIZAR NUEVA SOLICITUD", type="secondary", use_container_width=True):
            st.session_state.enviado = False
            st.rerun()
            
    else:
        # PANTALLA DE FORMULARIO
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Nombre / Razón Social", placeholder="Ej: Juan Pérez o Empresa S.A.").upper()
            producto = st.text_input("Producto", placeholder="Ingrese nombre de producto")
        
        with col2:
            serial = st.text_input("Serial (SN - ASA)", placeholder="Ubicado en la etiqueta")
            fecha_compra = st.date_input("Fecha de Compra", max_value=date.today(), format="DD/MM/YYYY")

        motivo = st.selectbox(
            "Motivo del trámite",
            options=["Seleccione una opción", "RMA", "Devolución"]
        )
        
        descripcion = st.text_area("Descripción detallada", placeholder="Describa el motivo o la falla...")

        st.markdown("---")
        st.markdown("### Método de Contacto")
        
        opcion_contacto = st.radio(
            "¿Cómo prefiere que nos contactemos?",
            options=["WhatsApp", "Correo Electrónico"],
            horizontal=True
        )

        telefono_val = ""
        email_val = ""

        if opcion_contacto == "WhatsApp":
            telefono_val = st.text_input("Número de WhatsApp", placeholder="Ej: 549343...")
        else:
            email_val = st.text_input("Dirección de Correo Electrónico", placeholder="ejemplo@correo.com")

        st.markdown("---")
        
        enviar = st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True)

        if enviar:
            contacto_lleno = telefono_val if opcion_contacto == "WhatsApp" else email_val
            
            if not cliente or not producto or not serial or motivo == "Seleccione una opción" or not contacto_lleno:
                st.error("Por favor, complete todos los campos para poder procesar la solicitud.")
            else:
                with st.spinner("Procesando..."):
                    try:
                        nuevo_registro = {
                            "Cliente": cliente,
                            "Producto": producto,
                            "Serial": serial,
                            "Compra": str(fecha_compra),
                            "Motivo del trámite": motivo, 
                            "diagnostico": descripcion,
                            "Telefono": telefono_val,      
                            "Email": email_val,            
                            "Estado del RMA": "PENDIENTE",
                            "Ingreso": str(date.today())
                        }
                        
                        table.create(nuevo_registro)
                        # Cambiamos el estado y forzamos el refresco para mostrar la pantalla de éxito
                        st.session_state.enviado = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al conectar con Airtable: {e}")