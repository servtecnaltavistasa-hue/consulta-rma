import streamlit as st
from pyairtable import Api
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- CREDENCIALES SEGURAS (SECRETS) ---
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = st.secrets["BASE_ID"]
    TABLE_NAME = f"{st.secrets['TABLE_NAME']}"
except Exception:
    st.error("Error: No se encontraron las credenciales en los Secrets de Streamlit.")
    st.stop()

api = Api(AIRTABLE_TOKEN)
table = api.table(BASE_ID, TABLE_NAME)

# --- INTERFAZ DE USUARIO ---
st.markdown("<h1 style='text-align: center;'>Formulario de Ingreso de RMA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Complete los siguientes datos para registrar el reingreso de mercadería.</p>", unsafe_allow_html=True)
st.markdown("---")

with st.form("formulario_rma", clear_on_submit=True):
    # Campos del formulario
    cliente = st.text_input("Código de Cliente:").strip()
    producto = st.text_input("Producto (Modelo / Descripción):").strip()
    serial = st.text_input("Número de Serie (Serial):").strip()
    
    # Campo de Falla (Guardado correctamente bajo la clave "Falla")
    falla = st.text_area("Falla / Motivo del trámite:").strip()
    
    # Campo de Fecha de Compra
    fecha_compra = st.date_input("Fecha de Compra:", value=date.today())
    
    # Texto de ayuda renderizado como un comentario gris de código debajo del cuadro
    st.markdown("<div style='color: #888888; font-size: 14px; margin-top: -10px; margin-bottom: 15px;'># Dejar fecha actual si no recuerda</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    bot_enviar = st.form_submit_button("Registrar RMA", use_container_width=True)

    if bot_enviar:
        # Validación de campos obligatorios
        if not cliente or not producto or not serial or not falla:
            st.error("Por favor, complete todos los campos obligatorios del formulario.")
        else:
            try:
                # Mapeo de datos correcto hacia las columnas de Airtable
                datos_registro = {
                    "Cliente": cliente.upper(),
                    "Producto": producto,
                    "Serial": serial.upper(),
                    "Falla": falla,              # <-- Guardado en la columna correcta de la base de datos
                    "Compra": fecha_compra.strftime("%Y-%m-%d"),
                    "Aceptado": False,           # Entra como pendiente en la Tabla 1 del admin panel
                    "Finalizado": False
                }
                
                table.create(datos_registro)
                st.success("¡Trámite de RMA registrado con éxito! Será evaluado por el equipo técnico.")
                
            except Exception as e:
                st.error(f"Ocurrió un error al guardar los datos: {e}")
