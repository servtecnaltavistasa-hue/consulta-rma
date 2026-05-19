import streamlit as st
from pyairtable import Api
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RMA ALTAVISTA SA", layout="centered")

# --- CSS PARA ELIMINAR EL CARTEL "PRESS ENTER TO APPLY" --
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
    try:
        dt = datetime.strptime(str(fecha_raw).strip(), "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return str(fecha_raw)

# --- INTERFAZ DE USUARIO ---
st.markdown("<h1 style='text-align: center;'>Consulta de Estado de RMA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ingrese el número de serie de su producto para verificar el estado de su trámite.</p>", unsafe_allow_html=True)
st.markdown("---")

busqueda = st.text_input("Número de Serie o Cliente:", placeholder="Ej: SN-ASA12345...").strip()

if busqueda:
    try:
        # Consulta en Airtable buscando coincidencia en Serial o Cliente
        formula = f"OR(FIND('{busqueda}', {{Serial}}), FIND('{busqueda}', {{Cliente}}))"
        resultados = table.all(formula=formula)
        
        if resultados:
            st.success(f"Se encontraron {len(resultados)} registro(s) asociado(s).")
            st.markdown("---")
            
            for r in resultados:
                f = r.get('fields', {})
                
                # Controladores de estados y visualización
                estado_valor = str(f.get('Estado del RMA', 'PENDIENTE')).upper()
                es_finalizado = f.get('Finalizado', False)
                
                # Estilos condicionales según el diagnóstico
                diagnostico_texto = f.get('diagnostico', 'Sin diagnóstico asentado aún.')
                es_fuera_garantia = "FUERA DE GARANTIA" in estado_valor
                
                # Procesar fechas legibles
                fecha_compra = formatear_fecha_cliente(f.get('Compra'))
                fecha_resolucion = formatear_fecha_cliente(f.get('Resolucion'))
                fecha_ingreso = formatear_fecha_cliente(f.get('Ingreso'))
                
                # Renderizado de Tarjeta de Información
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Cliente:** {f.get('Cliente', 'N/A')}")
                        st.markdown(f"**Producto:** {f.get('Producto', 'N/A')}")
                        st.markdown(f"**Serial:** {f.get('Serial', 'N/A')}")
                        st.markdown(f"**Fecha de Ingreso:** {fecha_ingreso}")
                        st.markdown(f"**Fecha de Compra:** {fecha_compra}")
                        st.markdown(f"**Motivo:** {f.get('Motivo del trámite', 'N/A')}")
                    
                    with col2:
                        aceptado_icon = "✅" if f.get('Aceptado') else "❌"
                        st.markdown(f"**Aceptado:** {aceptado_icon}")
                        st.markdown(f"**Estado del RMA:** {f.get('Estado del RMA', 'N/A')}")
                        
                        if es_finalizado:
                            st.markdown(f"**Resolución:** :red[{fecha_resolucion}]")
                        else:
                            st.markdown(f"**Resolución:** {fecha_resolucion}")
                        
                        comentario_texto = f.get('comentario', '')
                        if comentario_texto and str(comentario_texto).strip() not in ["None", "none", "nan", "NaN", ""]:
                            st.markdown(f"**Comentario:** {comentario_texto}")
                    
                    st.markdown("---")
                    st.markdown(f"**Diagnóstico:**")
                    if es_fuera_garantia:
                        st.error(diagnostico_texto)
                    elif "NO FALLO" in estado_valor:
                        st.warning(diagnostico_texto)
                    else:
                        st.info(diagnostico_texto)
        else:
            st.warning(f"No se encontraron resultados para '{busqueda}'.")
            
    except Exception as e:
        st.error(f"Error en la consulta: {e}")
else:
    st.info("Sistema de consulta de RMA. Ingrese sus datos para comenzar.")
