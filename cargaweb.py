# --- COLOCAR EN LA PÁGINA DE CONSULTA DE CLIENTES ---
# (Justo debajo de la línea donde se renderiza la 'Resolucion')

resol_text = caso_row.get('Resolucion', '')
if resol_text:
    st.write(f"**Resolución:** {formatear_para_leer(resol_text)}")
else:
    st.write("**Resolución:** Pendiente de revisión técnica")

# =====================================================================
# AGREGAR CAMPO COMENTARIO (DEBAJO DE LA RESOLUCIÓN)
# =====================================================================
# Traemos el valor usando 'comentario' tal cual está en la base de datos
com_val = caso_row.get('comentario', '')

# Limpiamos el texto para asegurar que si está vacío en Airtable no muestre "None" o "NaN"
com_limpio = "" if str(com_val).strip() in ["None", "none", "nan", "NaN", ""] else str(com_val)

if com_limpio:
    st.markdown(f"""
        <div style="margin-top: 12px; padding: 8px 12px; background-color: #fcfcfc; 
                    border-left: 4px solid #007bff; border-bottom: 1px solid #eee; border-radius: 4px;">
            <span style="font-weight: bold; text-decoration: underline; color: #111;">
                💬 Comentario adicional:
            </span>
            <span style="color: #444; font-style: italic; margin-left: 5px;">
                {com_limpio}
            </span>
        </div>
    """, unsafe_allow_html=True)
# =====================================================================