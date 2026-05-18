import streamlit as st
from pyairtable import Api

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RMA ALTAVISTA SA", layout="centered")

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
            for r in results:
                f = r.get('fields', {})
                
                # EVITAR MUESTRAS VACÍAS
                if not f.get('Producto'):
                    continue
                
                es_finalizado = f.get('Finalizado', False)
                estado_valor = str(f.get('Estado del RMA', '')).upper()
                es_fuera_garantia = "FUERA DE GARANTIA" in estado_valor
                diagnostico_texto = f.get('diagnostico', 'Sin diagnóstico aún')
                
                texto_estado = "[CASO FINALIZADO]" if es_finalizado else "[EN PROCESO]"
                
                label_header = f"Cliente: {f.get('Cliente', 'N/A')} - Producto: {f.get('Producto', 'N/A')} {texto_estado}"
                
                with st.expander(label_header, expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Producto:** {f.get('Producto', 'N/A')}")
                        st.markdown(f"**Serial:** {f.get('Serial', 'N/A')}")
                        
                        fecha_compra = f.get('Compra', 'N/A')
                        if fecha_compra != 'N/A' and "EXCEDIDO" in str(f.get('Compra', '')):
                            st.markdown(f"**Compra:** :red[{fecha_compra}]")
                        else:
                            st.markdown(f"**Compra:** {fecha_compra}")
                        st.markdown(f"**Ingreso:** {f.get('ingreso', 'N/A')}")
                    
                    with col2:
                        aceptado_icon = "✅" if f.get('Aceptado') else "❌"
                        st.markdown(f"**Aceptado:** {aceptado_icon}")
                        st.markdown(f"**Estado del RMA:** {f.get('Estado del RMA', 'N/A')}")
                        
                        # FECHA DE RESOLUCIÓN
                        if es_finalizado:
                            st.markdown(f"**Resolución:** :red[{f.get('Resolucion', 'N/A')}]")
                        else:
                            st.markdown(f"**Resolución:** {f.get('Resolucion', 'N/A')}")
                        
                        # =====================================================================
                        # SOLUCIÓN EXPLICITA PARA TEXTO LARGO (LONG TEXT) DE AIRTABLE
                        # =====================================================================
                        # Forzamos la obtención del string, si no existe devuelve cadena vacía
                        comentario_raw = f.get('comentario', '')
                        
                        # Limpieza estricta de formatos nulos que genera Airtable en textos largos vacíos
                        comentario_limpio = "" if str(comentario_raw).strip() in ["None", "none", "nan", "NaN", ""] else str(comentario_raw).strip()
                        
                        if comentario_limpio:
                            # Lo renderizamos como HTML destacado para que no se pierda visualmente
                            st.markdown(f"""
                                <div style="margin-top: 8px; padding: 6px 10px; background-color: #f9f9f9; 
                                            border-left: 3px solid #17a2b8; border-radius: 4px;">
                                    <strong>Comentario:</strong> <span style="font-style: italic; color: #555;">{comentario_limpio}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        # =====================================================================
                    
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
    st.info("Sistema de consulta de RMA. Ingrese sus datos para comenzar...")