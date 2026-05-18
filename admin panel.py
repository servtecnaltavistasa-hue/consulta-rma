# --- CONFIGURACIÓN DE ESTILOS DE XLSXWRITER (CORREGIDO DE RAÍZ) ---
                    output = io.BytesIO()
                    # Agregamos style_converter=None para que Pandas no meta formatos por defecto
                    with pd.ExcelWriter(output, engine='xlsxwriter', style_converter=None) as writer:
                        df_exc.to_excel(writer, index=False, sheet_name='Reporte', startrow=2)
                        
                        workbook  = writer.book
                        worksheet = writer.sheets['Reporte']
                        
                        formato_titulo = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Segoe UI'})
                        
                        formato_encabezado = workbook.add_format({
                            'bold': True,
                            'font_color': '#FFFFFF',
                            'bg_color': '#000000',
                            'border': 1,
                            'border_color': '#000000',
                            'align': 'center',
                            'valign': 'vcenter',
                            'font_name': 'Segoe UI',
                            'font_size': 11
                        })
                        
                        formato_celda = workbook.add_format({
                            'border': 1,
                            'border_color': '#000000',
                            'valign': 'vcenter',
                            'font_name': 'Segoe UI',
                            'font_size': 10
                        })
                        
                        # Escribimos el título principal
                        worksheet.write(0, 0, f"REPORTE DE RMA - CLIENTE: {cliente_buscado.upper()}", formato_titulo)
                        
                        # Forzamos el formato negro en los encabezados
                        for col_num, header_title in enumerate(df_exc.columns):
                            worksheet.write(1, col_num, header_title, formato_encabezado)
                        
                        # --- AUTOAJUSTE DE ANCHO Y RE-ESCRITURA CON FORMATO DE CELDAS ---
                        for i, col in enumerate(df_exc.columns):
                            max_len = df_exc[col].astype(str).str.len().max()
                            
                            if pd.isna(max_len) or max_len < 0:
                                max_len = 12
                                
                            max_len = max(int(max_len), len(col)) + 4  
                            worksheet.set_column(i, i, max_len)
                            
                            # Iteramos exactamente sobre cada fila para estampar nuestro propio formato_celda
                            for row_idx in range(len(df_exc)):
                                val_raw = df_exc.iloc[row_idx, i]
                                
                                if pd.isna(val_raw) or str(val_raw).strip() in ["NaT", "None", "nan", "NaN"]:
                                    val_celda = ""
                                else:
                                    val_celda = str(val_raw)
                                    
                                # Esto sobreescribe la celda asegurando los bordes y la fuente Segoe UI en TODAS las filas
                                worksheet.write(row_idx + 2, i, val_celda, formato_celda)
                                
                        worksheet.set_row(1, 24)
