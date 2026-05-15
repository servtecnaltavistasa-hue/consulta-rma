import streamlit as st
from pyairtable import Api
from datetime import date
import urllib.parse  # Para procesar el texto de WhatsApp

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Formulario RMA - ALTAVISTA SA", layout="centered")

# --- 2. LIMPIEZA VISUAL ---
st.markdown("""
    <style>
    /* Ocultar elementos de la interfaz de Streamlit */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    stDecoration {display: none !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stAppViewBlockContainer"] + div {display: none !important;}
    
    /* Ocultar instrucciones de teclado */
    div[data-testid="stTextInput"] [data-testid="InputInstructions"] { display: none !important; }
    div[data-testid="stTextArea"] [data-testid="InputInstructions"] { display: none !important; }

    /* Contenedor del formulario */
    .block-container { padding-top: 2rem; }
    [data-testid="stVerticalBlockBorderControl"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        padding: 2rem;
    }

    /* Botón de WhatsApp Personalizado */
    .whatsapp-button {
        background-color: #25D366;
        color: white !important;
        padding: 14px 20px;
        text-align: center;
        text-decoration: none;
        display: block;
        border-radius: 8px;
        font-weight: bold;
        margin-top: 15px;
        border: none;
        transition: 0.3s;
    }
    .whatsapp-button:hover {
        background-color: #128C7E;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
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
if st.session_state.enviado:
        st.success("¡Solicitud enviada con éxito! En breve le asignaremos su número de RMA.")
        
        st.markdown("### ¿Qué desea hacer ahora?")
        
        # --- FILA DE BOTONES (COLUMNAS) ---
        col_izq, col_der = st.columns([3, 1]) # La columna izquierda es más ancha que la derecha

        with col_izq:
            if st.button("CARGAR OTRO PRODUCTO", type="secondary", use_container_width=True):
                st.session_state.enviado = False
                st.session_state.datos_resumen = {}
                st.rerun()

        with col_der:
            # Generar link de WhatsApp
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
            
            # Botón de WhatsApp más pequeño y alineado
            st.markdown(f"""
                <a href="{link_whatsapp}" target="_blank" class="whatsapp-button" 
                   style="margin-top: 0px; padding: 8px; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="20" height="20">
                    Contactarnos
                </a>
                """, unsafe_allow_html=True)
    else:
        # --- CAMPOS DEL FORMULARIO ---
        f1col1, f1col2 = st.columns(2)
        with f1col1:
            cliente = st.text_input("Nombre / Razón Social", placeholder="Ej: Juan Pérez").upper()
        with f1col2:
            serial = st.text_input("Serial (SN - ASA)", placeholder="Ubicado en la etiqueta")

        f2col1, f2col2 = st.columns(2)
        with f2col1:
            producto = st.text_input("Producto", placeholder="Ingrese nombre de producto")
        with f2col2:
            fecha_compra = st.date_input(
                "Fecha de Compra", 
                max_value=date.today(), 
                format="DD/MM/YYYY",
                help="Dejar el valor predeterminado si no recuerda la fecha exacta"
            )
            st.caption("Dejar valor predeterminado si no recuerda")

        motivo = st.selectbox("Motivo del trámite", options=["Seleccione una opción", "RMA", "Devolución"])
        descripcion = st.text_area("Descripción detallada", placeholder="Describa el motivo o la falla...")

        st.markdown("---")
        st.markdown("### Método de Contacto")
        opcion_contacto = st.radio("¿Cómo prefiere que nos contactemos?", options=["WhatsApp", "Correo Electrónico"], horizontal=True)

        tel, mail = "", ""
        if opcion_contacto == "WhatsApp":
            tel = st.text_input("Número de WhatsApp", placeholder="Ej: 549343...")
        else:
            mail = st.text_input("Dirección de Correo Electrónico", placeholder="ejemplo@correo.com")

        st.markdown("---")
        
        if st.button("ENVIAR SOLICITUD", type="primary", use_container_width=True):
            contacto_val = tel if opcion_contacto == "WhatsApp" else mail
            if not cliente or not producto or not serial or motivo == "Seleccione una opción" or not contacto_val:
                st.error("Por favor, complete todos los campos obligatorios antes de enviar.")
            else:
                with st.spinner("Registrando en base de datos..."):
                    try:
                        # 1. Guardar resumen para el mensaje de WhatsApp
                        st.session_state.datos_resumen = {
                            "cliente": cliente,
                            "producto": producto,
                            "serial": serial,
                            "falla": descripcion
                        }
                        
                        # 2. Enviar a Airtable (Ojo: Asegúrate que la columna en Airtable se llame 'Ingreso' con I mayúscula)
                        nuevo_registro = {
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
                        }
                        table.create(nuevo_registro)
                        
                        st.session_state.enviado = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al conectar con Airtable: {e}")
