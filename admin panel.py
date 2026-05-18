# --- AUTOAJUSTE DE ANCHO Y ESCALADO SEGURO DE CELDAS (CORREGIDO) ---
                        for i, col in enumerate(df_exc.columns):
                            max_len = df_exc[col].astype(str).str.len().max()
                            
                            if pd.isna(max_len) or max_len < 0:
                                max_len = 12
                                
                            max_len = max(int(max_len), len(col)) + 4  
                            worksheet.set_column(i, i, max_len)
                            
                            # Recorremos de manera exacta todas las filas del DataFrame
                            for row_idx in range(len(df_exc)):
                                val_raw = df_exc.iloc[row_idx, i]
                                
                                # Sanitización de valores vacíos o nulos
                                if pd.isna(val_raw) or str(val_raw).strip() in ["NaT", "None", "nan", "NaN"]:
                                    val_celda = ""
                                else:
                                    val_celda = str(val_raw)
                                    
                                # Escribimos aplicando estrictamente el formato_celda (borde negro y Segoe UI)
                                worksheet.write(row_idx + 2, i, val_celda, formato_celda)
