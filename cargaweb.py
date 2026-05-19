import streamlit as st
from pyairtable import Api
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RMA ALTAVISTA SA", layout="centered")

# --- CSS PARA ELIMINAR EL CARTEL "PRESS ENTER TO APPLY" ---
st.markdown("""
    <style>
        /* Oculta la leyenda de 'Press Enter to apply' en los inputs de texto */
        div[data-testid="stTextInput"] aria-instructions, 
        div[data-testid="stTextInput"] div[data-testid="InputInstructions"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

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

# --- FUNCIONES DE APOYO ---
def formatear_fecha_cliente(fecha_raw):
    """Convierte fechas YYYY-MM-DD de Airtable a formato legible DD/MM/YYYY"""
    if not fecha_raw or str(fecha_raw).strip() in ["None", "none", "nan", "NaN", ""]: 
        return "N/A"
    
    fecha_str = str(fecha_raw).replace('-', '/').strip()
    for formato in ['%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            dt = datetime.strptime(fecha_str, formato)
            return dt.strftime('%d/%m/%Y')
        except ValueError:
            continue
    return str(fecha_raw)

def obtener_fecha_ordenamiento(record):
    """Extrae la fecha de resolución para usarla como clave de ordenamiento"""
    f = record.get('fields', {})
    fecha_raw = f.get('Resolucion', '')
    if not fecha_raw or str(fecha_raw).strip() in ["None", "none", "nan", "NaN", ""]:
        return datetime.min # Si no tiene fecha, lo manda al final de los finalizados
    
    fecha_str = str(fecha_raw).replace('-', '/').strip()
    for formato in ['%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y']:
        try:
            return datetime.strptime(fecha_str, formato)
        except ValueError:
            continue
    return datetime.min

# --- CABECERA ---
st.markdown("<h1 style='text-align: center;'>RMA ALTAVISTA SA</h1>", unsafe_allow_html=True)

# --- BARRA DE BÚSQUEDA ---
entrada_usuario = st.text_input("Ingrese Código de Cliente o Número de RMA:", value="").strip()
busqueda = entrada_usuario.upper() 

if busqueda:
    try:
        condicion_cliente = f"{{Cliente}} = '{busqueda}'"
        if busqueda.isdigit():
            condicion_rma = f"{{Numero RMA}} = {busqueda}"
            formula = f"OR({condicion_cliente}, {condicion_rma})"
        else:
            formula = condicion_cliente
        
        results = table.all(formula=formula)
        
        if results:
            # --- LÓGICA DE CLASIFICACIÓN Y ORDENAMIENTO DE CASOS ---
            en_proceso = []
            finalizados = []
            
            for record in results:
                f = record.get('fields', {})
                es_aceptado = f.get('Aceptado') in [True, 1, "True", "true"]
                es_finalizado = f.get('Finalizado') in [True, 1, "True", "true"]
                
                if es_aceptado and not es_finalizado:
                    en_proceso.append(record)
                elif es_aceptado and es_finalizado:
                    finalizados.append(record)
                else:
                    # Por las dudas si hay casos no aceptados aún, los agrupamos con "en proceso"
                    en_proceso.append(record)
            
            # Ordenar los finalizados por fecha de 'Resolucion' (Más nuevos primero -> reverse=True)
            finalizados.sort(key=obtener_fecha_ordenamiento, reverse=True)
            
            # Combinamos: Primero En Proceso, abajo los Finalizados ordenados cronológicamente
            resultados_ordenados = en_proceso + finalizados
            
            # --- INTERFAZ GRÁFICA DE CONTACTO ---
            numero_tel = "5493433002458"
            mensaje_wa = urllib.parse.quote(f"Hola Altavista SA, tengo una consulta sobre el RMA/Cliente: {busqueda}")
            link_wa = f"https://wa.me/{numero_tel}?text={mensaje_wa}"
            
            col_msg, col_ws = st.columns([2, 1])
            with col_msg:
                st.success(f"Se encontraron {len(resultados_ordenados)} coincidencia(s):")
            with col_ws:
                st.markdown(f"""
                <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="18">
                        Contactarnos
                    </div>
                </a>
                """, unsafe_allow_html=True)

            # --- RENDERS DE LAS FICHAS ---
            for index, record in enumerate(resultados_ordenados):
                f = record['fields']
                estado_valor = str(f.get('Estado del RMA', '')).strip().upper()
