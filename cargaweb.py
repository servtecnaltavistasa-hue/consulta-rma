import streamlit as st
from pyairtable import Api
import urllib.parse

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RMA ALTAVISTA SA", layout="centered")

# --- CREDENCIALES SEGURAS (SECRETS) ---
try:
    AIRTABLE_TOKEN = st.secrets["patADPYfeYSK86zP9.b6b1da2053f3e17dc5eb4730ddf5015e2d59ca43576e956999b0dded741938c7" ]
    BASE_ID = st.secrets["appjlLix1HpBwnhpS"]
    TABLE_NAME = st.secrets["RMA ALTAVISTA"]
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
            numero_tel = "5493433002458"
            mensaje_wa = urllib.parse.quote(f"Hola Altavista SA, tengo una consulta sobre el RMA/Cliente: {busqueda}")
            link_wa = f"https://wa.me/{numero_tel}?text={mensaje_wa}"
            
            col_msg, col_ws = st.columns([2, 1])
            with col_msg:
                st.success(f"Se encontraron {len(results)} coincidencia(s):")
            with col_ws:
                st.markdown(f"""
                <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; display: flex; align-items: center; justify-content: center; gap: 8px;">
                        <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="18">
                        Contactarnos
                    </div>
                </a>
                """, unsafe_allow_html=True)

            for index, record in enumerate(results):
                f = record['fields']
                estado_valor = str(f.get('Estado del RMA', '')).strip().upper()
                diagnostico_texto = f.get('diagnostico', 'Sin diagnóstico registrado.')
                fecha_compra = f.get('Compra', 'N/A')
                es_fuera_garantia = "FUERA DE GARANTIA" in estado_valor
                
                # Comprobar si está marcado como Finalizado en Airtable
                es_finalizado = f.get('Finalizado') in [True, 1, "True", "true"]
                
                # Título en texto plano para el expander (Previene que falle el renderizado)
                titulo_expander = f"Cliente: {f.get('Cliente', 'S/D')} - RMA: {f.get('Numero RMA', 'S/D')}"
                
                debe_expandir = True
                if len(results) > 2 and index > 0:
                    debe_expandir = False
                
                with st.expander(titulo_expander, expanded=debe_expandir):
                    # SOLUCIÓN DE ENCABEZADO: Insertamos la alerta roja/naranja de estado al principio de la tarjeta
                    if es_finalizado:
                        st.markdown(
                            """
                            <div style="background-color: #dc3545; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px; text-align: center; margin-bottom: 12px; font-size: 14px; letter-spacing: 0.5px;">
                                🔴 ESTADO DEL CASO: FINALIZADO
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="background-color: #fd7e14; color: black; font-weight: bold; padding: 6px 12px; border-radius: 4px; text-align: center; margin-bottom: 12px; font-size: 14px;">
                                ⏳ ESTADO DEL CASO: EN PROCESO ({f.get('Estado del RMA', 'N/A')})
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Producto:** {f.get('Producto', 'N/A')}")
                        st.markdown(f"**Serial:** {f.get('serial', 'N/A')}")
                        if es_fuera_garantia:
                            st.markdown(f"**Compra:** :red[{fecha_compra}]")
                        else:
                            st.markdown(f"**Compra:** {fecha_compra}")
                        st.markdown(f"**Ingreso:** {f.get('ingreso', 'N/A')}")
                    
                    with col2:
                        aceptado_icon = "✅" if f.get('Aceptado') else "❌"
                        st.markdown(f"**Aceptado:** {aceptado_icon}")
                        st.markdown(f"**Estado del RMA:** {f.get('Estado del RMA', 'N/A')}")
                        
                        # MODIFICACIÓN SOLICITADA: Fecha de resolución remarcada en rojo
                        if es_finalizado:
                            st.markdown(
                                f"""
                                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; border-left: 5px solid #dc3545; padding: 6px 12px; border-radius: 4px; margin-top: 5px; display: inline-block;">
                                    <strong style="color: #721c24;">Resolución:</strong> 
                                    <span style="color: #dc3545; font-weight: bold;">{f.get('Resolucion', 'N/A')}</span>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(f"**Resolución:** {f.get('Resolucion', 'N/A')}")
                    
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