# --- REEMPLAZO PARA LA PÁGINA DE CONSULTA PÚBLICA (VISTA CLIENTE) ---

# Recorremos cada caso asignado al cliente en tu bucle iterador
for _, caso_row in df_cliente.iterrows():
    cliente_val = caso_row.get('Cliente', '')
    rma_num = caso_row.get('RMA', caso_row.get('id_interno', ''))
    es_finalizado = caso_row.get('Finalizado', False)
    
    # FORMATO DEL TAG: Determina el texto y color dinámico
    texto_estado = "CASO FINALIZADO" if es_finalizado else "EN PROCESO"
    color_badge = "#28a745" if es_finalizado else "#17a2b8" # Verde / Celeste
    
    # HACK FLEXBOX: Esto empuja el estado al extremo derecho exacto del expander
    label_header = f"""
        <div style="display: flex; justify-content: space-between; width: 100%; font-weight: 500; align-items: center;">
            <span>Cliente: {cliente_val} - RMA: {rma_num}</span>
            <span style="color: {color_badge}; margin-right: 25px; font-weight: bold; font-size: 13px;">
                [{texto_estado}]
            </span>
        </div>
    """
    
    with st.expander(label_header, expanded=False):
        # Renderizado interno de la ficha técnica en dos columnas limpias
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.write(f"**Producto:** {caso_row.get('Producto', '')}")
            st.write(f"**Serial:** {caso_row.get('Serial', 'N/A')}")
            st.write(f"**Compra:** {formatear_para_leer(caso_row.get('Compra', ''))}")
            st.write(f"**Ingreso:** {formatear_para_leer(caso_row.get('Ingreso', ''))}")
            
        with col_der:
            st.write(f"**Aceptado:** {'✅' if caso_row.get('Aceptado', False) else '❌'}")
            st.write(f"**Estado del RMA:** {caso_row.get('Estado del RMA', 'PENDIENTE')}")
            
            resol_text = caso_row.get('Resolucion', '')
            if resol_text:
                st.write(f"**Resolución:** {formatear_para_leer(resol_text)}")
            else:
                st.write("**Resolución:** Pendiente de revisión")
                
            # REQUISITO EXACTO: Campo 'comentario' justo abajo de la resolución
            com_val = caso_row.get('comentario', '')
            com_limpio = "" if str(com_val).strip() in ["None", "none", "nan", "NaN", ""] else str(com_val)
            
            if com_limpio:
                st.markdown(f"""
                    <div style="margin-top: 10px; padding: 8px 12px; background-color: #fcfcfc; 
                                border-left: 4px solid #007bff; border-bottom: 1px solid #eee; border-radius: 4px;">
                        <span style="font-weight: bold; text-decoration: underline; color: #111;">
                            💬 Comentario adicional:
                        </span>
                        <span style="color: #444; font-style: italic; margin-left: 5px;">
                            {com_limpio}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        st.write("**Diagnóstico:**")
        diag_val = caso_row.get('diagnostico', '')
        st.info(diag_val if diag_val else "Sin diagnóstico registrado.")