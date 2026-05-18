# --- RENDERIZADO DE LA FICHA DEL CASO (VISTA CLIENTE) ---
# (Asumiendo que 'caso' es la fila o diccionario con los datos del RMA encontrado)

# 1. ENCABEZADO: Título a la izquierda, Estado a la derecha
col_titulo, col_estado = st.columns([3, 1])

with col_titulo:
    st.subheader(f"📋 Caso: {caso.get('Producto', 'Producto no especificado')}")

with col_estado:
    # Lógica para determinar el color de la etiqueta según el estado
    estado_raw = str(caso.get('Estado del RMA', "")).upper()
    color_bg = "#6c757d" # Gris por defecto
    color_txt = "white"
    
    if estado_raw in ["CAMBIO", "CREDITO"]: color_bg = "#28a745"
    elif estado_raw in ["GARANTIA", "GARANTIA OFICIAL"]: color_bg = "#fd7e14"; color_txt = "black"
    elif estado_raw == "NO FALLO - DEVOLVER A CLIENTE": color_bg = "#17a2b8"
    elif estado_raw == "FUERA DE GARANTIA": color_bg = "#dc3545"
    
    # Renderizado alineado a la derecha usando HTML nativo
    st.markdown(f"""
        <div style="text-align: right; margin-top: 10px;">
            <span style="background-color: {color_bg}; color: {color_txt}; 
                         padding: 6px 12px; border-radius: 4px; 
                         font-weight: bold; font-size: 14px; display: inline-block;">
                {estado_raw if estado_raw else "EN PROCESO"}
            </span>
        </div>
    """, unsafe_allow_html=True)

st.write(f"**Cliente:** {caso.get('Cliente', '')}")
st.write(f"**Fecha de Ingreso:** {formatear_para_leer(caso.get('Ingreso', ''))}")
st.write(f"**Falla Reportada:** {caso.get('Falla', '')}")
st.write(f"**Diagnóstico Técnico:** {caso.get('diagnostico', '')}")

# Formateamos la resolución para mostrarla limpia
resolucion_texto = caso.get('Resolucion', '')
if resolucion_texto:
    st.write(f"**Resolución:** {formatear_para_leer(resolucion_texto)}")
else:
    st.write("**Resolución:** Pendiente de evaluación")

# 2. COMENTARIO EXTRA: Abajo de la resolución y remarcado/subrayado
# Limpiamos el comentario para evitar que muestre "None" en la web de consulta
comentario_raw = caso.get('comentario', '')
comentario_limpio = "" if str(comentario_raw).strip() in ["None", "none", "nan", "NaN", ""] else str(comentario_raw)

if comentario_limpio:
    st.markdown(f"""
        <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; 
                    border-left: 4px solid #007bff; border-bottom: 1px solid #dee2e6;">
            <span style="font-weight: bold; text-decoration: underline; color: #333;">
                💬 Comentario adicional:
            </span> 
            <span style="color: #555; font-style: italic;">
                {comentario_limpio}
            </span>
        </div>
    """, unsafe_allow_html=True)