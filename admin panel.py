import streamlit as st
from pyairtable import Api
import pandas as pd
from datetime import datetime, date
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel RMA", layout="wide")

# CSS original para diseño de tablas y celdas coloridas
st.markdown("""
    <style>
        .block-container { padding-top: 4rem; }
        div[data-testid="stExpander"] { border: 1px solid #444; margin-bottom: 1rem; }
        
        [data-testid="stDataEditor"] div, .stDataTable td {
            border-bottom: 4px solid #000 !important;
        }
        
        .stDataTable td, .stDataTable th, [data-testid="stDataEditor"] * {
            font-family: sans-serif !important;
            font-size: 14px !important;
            font-weight: 400 !important;
        }

        .stDataTable td, .stDataTable th {
            border-right: 1px solid #444 !important;
        }

        div[data-testid="stGridVirtualizingContainer"] div {
            --background-color: transparent !important;
        }
        [data-testid="stDataEditor"] td div input, 
        [data-testid="stDataEditor"] td div div,
        [data-testid="stDataEditor"] [role="gridcell"] * {
            background-color: inherit !important;
            color: inherit !important;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 1B. SISTEMA DE AUTENTICACIÓN SEGURO (SECRETS) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""

def login():
    st.markdown("<h2 style='text-align: center;'>Control de Acceso - Panel RMA</h2>", unsafe_allow_html=True)
    with st.form("formulario_login"):
        usuario = st.text_input("Usuario:").strip()
        clave = st.text_input("Contraseña:", type="password").strip()
        bot_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        if bot_login:
            try:
                usuarios_secretos = st.secrets["USUARIOS"]
                
                if usuario in usuarios_secretos and usuarios_secretos[usuario] == clave:
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.session_state.rol = "admin" if usuario == "admin" else "user"
                    st.success("¡Acceso concedido!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
            except Exception:
                st.error("Error de configuración: No se encontró la sección [USUARIOS] en los Secrets.")

if not st.session_state.autenticado:
    login()
    st.stop()

# --- BARRA LATERAL ---
st.sidebar.write(f"Conectado como: **{st.session_state.usuario}** ({st.session_state.rol.upper()})")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.rol = ""
    st.rerun()

# --- CONEXIÓN A AIRTABLE ---
try:
    AIRTABLE_TOKEN = st.secrets["AIRTABLE_TOKEN"]
    BASE_ID = st.secrets["BASE_ID"]
    TABLE_NAME = st.secrets["TABLE_NAME"]
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, TABLE_NAME)
except Exception as e:
    st.error(f"Error en credenciales: {e}")
    st.stop()

# --- 2. FUNCIONES DE APOYO ---
def estilo_filas(row):
    estado = str(row.get('Estado del RMA', "")).upper()
    verde, naranja, celeste, rojo, gris = 'background-color: #28a745; color: white;', 'background-color: #fd7e14; color: black;', 'background-color: #17a2b8; color: white;', 'background-color: #dc3545; color: white;', 'background-color: #6c757d; color: white;'
    style = ''
    if estado in ["CAMBIO", "CREDITO"]: style = verde
    elif estado in ["GARANTIA", "GARANTIA OFICIAL"]: style = naranja
    elif estado == "NO FALLO - DEVOLVER A CLIENTE": style = celeste
    elif estado == "FUERA DE GARANTIA": style = rojo
    elif estado == "REPARADO": style = gris
    return [style if col != 'Finalizado' else '' for col in row.index]

def formatear_para_leer(fecha_raw):
    if not fecha_raw or str(fecha_raw).strip() in ["None", "none", "nan", "NaN", ""]: return ""
    fecha_str = str(fecha_raw).replace('-', '/').strip()
    for formato in ['%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']:
        try:
            dt = datetime.strptime(fecha_str, formato)
            return dt.strftime('%d/%m/%Y')
        except ValueError: continue
    return str(fecha_raw)

def formatear_y_validar_fecha(fecha_texto):
    if not fecha_texto or str(fecha_texto).strip() == "": return None, "OK"
    texto = str(fecha_texto).replace('-', '/').strip()
    for formato in ['%d/%m/%y', '%d/%m/%Y']:
        try:
            dt_objeto = datetime.strptime(texto, formato)
            if dt_objeto.date() > date.today(): return None, "FUTURA"
            return dt_objeto.strftime('%Y-%m-%d'), "OK"
        except ValueError: continue
    return None, "FORMATO_INVALIDO"

@st.cache_data(ttl=5)
def cargar_todos_los_datos():
    all_records = table.all()
    if not all_records: return pd.DataFrame()
    rows = []
    for r in all_records:
        fields = r['fields']
        fields['id_interno'] = r['id']
        rows.append(fields)
    return pd.DataFrame(rows)

# --- 3. CARGA Y MENÚ ---
df_all = cargar_todos_los_datos()

if st.session_state.rol == "admin":
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.link_button("🔵 Airtable", "https://airtable.com/appjlLix1HpBwnhpS/tblNnoXdIsLFN92Mr/viwLRiCozAc4oVKZY", use_container_width=True)
    with c2: st.link_button("💻 Github", "https://github.com/FedeASA/consulta-rma", use_container_width=True)
    with c3: st.link_button("📝 Texto Clientes", "https://docs.google.com/document/d/1URgFPuVsIoR6LX2diAwFR5rWRKYvmmEwvQ7VXuxSnYg", use_container_width=True)
    
    # NUEVA OPCIÓN AGREGADA AL MENÚ DESPLEGABLE ("Streamlit Base")
    with c4: 
        opcion_seleccionada = st.selectbox(
            "🚀 Páginas", 
            ["Navegar...", "Formulario", "Consulta", "Streamlit Base"], 
            label_visibility="collapsed"
        )
        # Redirección si se selecciona la nueva opción externa
        if opcion_seleccionada == "Streamlit Base":
            st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://share.streamlit.io/\'">', unsafe_allow_html=True)
            st.link_button("Abrir Streamlit Base manualmente", "https://share.streamlit.io/", use_container_width=True)

    with c5: st.link_button("📊 Excel Viejo", "https://docs.google.com/spreadsheets/d/17zp1kEZhVBw1Ul3HkoDZhyQ2IYthjNGS", use_container_width=True)

    col_rep1, col_rep2 = st.columns([1, 4])
    with col_rep1:
        btn_reporte = st.button("📊 Reporte", use_container_width=True)

    if btn_reporte:
        st.session_state.mostrar_input_reporte = not st.session_state.get('mostrar_input_reporte', False)

    if st.session_state.get('mostrar_input_reporte', False):
        with st.container(border=True):
            cliente_buscado = st.text_input("Ingrese nombre del Cliente para generar Excel:")
            if cliente_buscado:
                df_rep = df_all[df_all['Cliente'].astype(str).str.contains(cliente_buscado, case=False, na=False)].copy() if 'Cliente' in df_all.columns else pd.DataFrame()
                if not df_rep.empty:
                    cols_sel = ['Producto', 'Compra', 'Falla', 'Serial', 'Ingreso', 'Estado del RMA', 'Resolucion']
                    for c in cols_sel:
                        if c not in df_rep.columns: df_rep[c] = ""
                    
                    df_exc = df_rep[cols_sel].copy()
                    
                    # --- REPORTE: ORDENAR POR FECHA DE RESOLUCIÓN (MÁS NUEVOS ARRIBA) ---
                    df_exc['Resolucion_clean'] = df_exc['Resolucion'].astype(str).str.strip().replace(["None", "none", "nan", "NaN"], "")
                    df_exc['Resolucion_dt'] = pd.to_datetime(df_exc['Resolucion_clean'], errors='coerce')
                    df_exc = df_exc.sort_values(by='Resolucion_dt', ascending=False).drop(columns=['Resolucion_dt', 'Resolucion_clean'])

                    # Formateamos todas las fechas para el Excel final visible
                    for f in ['Compra', 'Ingreso', 'Resolucion']:
                        df_exc[f] = df_exc[f].apply(formatear_para_leer)

                    # --- CONFIGURACIÓN DE ESTILOS DE XLSXWRITER ---
                    output = io.BytesIO()
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
                        
                        worksheet.write(0, 0, f"REPORTE DE RMA - CLIENTE: {cliente_buscado.upper()}", formato_titulo)
                        
                        for col_num, header_title in enumerate(df_exc.columns):
                            worksheet.write(1, col_num, header_title, formato_encabezado)
                        
                        # --- AUTOAJUSTE DE ANCHO Y ESCALADO SEGURO DE CELDAS ---
                        for i, col in enumerate(df_exc.columns):
                            max_len = df_exc[col].astype(str).str.len().max()
                            
                            if pd.isna(max_len) or max_len < 0:
                                max_len = 12
                                
                            max_len = max(int(max_len), len(col)) + 4  
                            worksheet.set_column(i, i, max_len)
                            
                            for row_idx in range(len(df_exc)):
                                val_raw = df_exc.iloc[row_idx, i]
                                
                                if pd.isna(val_raw) or str(val_raw).strip() in ["NaT", "None", "nan", "NaN"]:
                                    val_celda = ""
                                else:
                                    val_celda = str(val_raw)
                                    
                                worksheet.write(row_idx + 2, i, val_celda, formato_celda)
                                
                        worksheet.set_row(1, 24)
                    
                    st.download_button(
                        label=f"📥 Descargar Reporte {cliente_buscado}", 
                        data=output.getvalue(), 
                        file_name=f"Reporte_{cliente_buscado}_{datetime.now().strftime('%d_%m_%Y')}.xlsx", 
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No hay datos para ese cliente.")
    st.divider()

if df_all.empty:
    st.warning("No hay datos para mostrar.")
    st.stop()

# --- SANEAMIENTO SEGURO DE COLUMNAS ---
columnas_requeridas = ['Aceptado', 'Finalizado', 'Ingreso', 'Resolucion', 'diagnostico', 'Estado del RMA', 'Compra', 'Producto', 'comentario', 'Falla']
for col in columnas_requeridas:
    if col not in df_all.columns: 
        df_all[col] = False if col in ['Aceptado', 'Finalizado'] else ""
    else:
        if col in ['Aceptado', 'Finalizado']:
            df_all[col] = df_all[col].apply(lambda x: True if x in [True, 1, "True", "true"] else False)

for col_txt in ['comentario', 'Falla', 'diagnostico', 'Ingreso', 'Resolucion', 'Compra', 'Cliente', 'Producto', 'Serial']:
    if col_txt in df_all.columns:
        df_all[col_txt] = df_all[col_txt].fillna("").apply(lambda x: "" if str(x).strip() in ["None", "none", "nan", "NaN", ""] else str(x))

# --- TABLA 1: POR ACEPTAR ---
df1 = df_all[
    (df_all['Aceptado'] == False) & 
    (df_all['Producto'].str.strip() != "") & 
    (df_all['Cliente'].str.strip() != "")
].copy()

with st.expander("📥 1. TICKETS POR ACEPTAR (Entrada)", expanded=True):
    if not df1.empty:
        if 'Compra' in df1.columns:
            df1 = df1.sort_values(by='Compra', ascending=False)
            
        df1['Compra'] = df1['Compra'].apply(formatear_para_leer)
        with st.form("f1"):
            c1_cols = ['Cliente', 'Producto', 'Serial', 'Falla', 'Compra', 'Aceptado']
            esta_deshabilitado_t1 = ['Cliente', 'Producto', 'Serial', 'Falla', 'Compra', 'Aceptado'] if st.session_state.rol != "admin" else ['Serial','Falla']
            
            ed1 = st.data_editor(df1[['id_interno'] + c1_cols].reset_index(drop=True), column_config={"id_interno":None}, disabled=esta_deshabilitado_t1, hide_index=True, use_container_width=True)
            
            if st.form_submit_button("GUARDAR ENTRADAS", disabled=(st.session_state.rol != "admin")):
                for _, r in ed1.iterrows():
                    orig = df1[df1['id_interno'] == r['id_interno']].iloc[0]
                    up = {k: r[k] for k in ['Aceptado','Cliente','Producto'] if str(r[k]) != str(orig.get(k,""))}
                    f, e = formatear_y_validar_fecha(r['Compra'])
                    if e == "OK" and f: up['Compra'] = f
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()
    else:
        st.info("No hay pendientes.")

# --- TABLA 2: EN PROCESO ---
df2 = df_all[(df_all['Aceptado'] == True) & (df_all['Finalizado'] == False)].copy().reset_index(drop=True)
with st.expander("⚙️ 2. TICKETS EN PROCESO (Aceptados)", expanded=True):
    if not df2.empty:
        for c in ['Compra','Ingreso','Resolucion']: 
            df2[c] = df2[c].apply(formatear_para_leer)
        
        with st.form("f2"):
            c2_cols = ['comentario', 'Cliente', 'Producto', 'Compra', 'Falla', 'Ingreso', 'diagnostico', 'Estado del RMA', 'Resolucion', 'Finalizado']
            st_df2 = df2[['id_interno'] + c2_cols]
            
            if st.session_state.rol == "admin":
                deshabilitados_t2 = ['Cliente', 'Producto', 'Compra', 'Falla']
            else:
                deshabilitados_t2 = ['Cliente', 'Producto', 'Compra', 'Falla', 'Ingreso', 'diagnostico', 'Estado del RMA', 'Resolucion', 'Finalizado']
            
            ed2 = st.data_editor(
                st_df2.style.apply(estilo_filas, axis=1), 
                column_config={
                    "id_interno": None, 
                    "comentario": st.column_config.TextColumn("💬 Comentario", width="medium"),
                    "diagnostico": st.column_config.TextColumn("🔧 Diagnóstico", width="medium"),
                    "Finalizado": st.column_config.CheckboxColumn("Finalizar"), 
                    "Estado del RMA": st.column_config.SelectboxColumn(options=["CAMBIO", "CREDITO", "GARANTIA OFICIAL", "GARANTIA", "FUERA DE GARANTIA", "NO FALLO - DEVOLVER A CLIENTE", "REPARADO"])
                }, 
                disabled=deshabilitados_t2, 
                hide_index=True, 
                use_container_width=True
            )
            
            if st.form_submit_button("ACTUALIZAR PROCESOS"):
                for _, r in ed2.iterrows():
                    orig = df2[df2['id_interno'] == r['id_interno']].iloc[0]
                    campos_a_revisar = ['comentario', 'diagnostico', 'Estado del RMA', 'Finalizado'] if st.session_state.rol == "admin" else ['comentario']
                    up = {k: r[k] for k in campos_a_revisar if str(r[k]) != str(orig.get(k, ""))}
                    
                    if st.session_state.rol == "admin":
                        for f in ['Ingreso', 'Resolucion']:
                            val, stt = formatear_y_validar_fecha(r[f])
                            if stt == "OK": up[f] = val
                    
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()

# --- TABLA 3: HISTÓRICO ---
df3 = df_all[(df_all['Aceptado'] == True) & (df_all['Finalizado'] == True)].copy().reset_index(drop=True)
with st.expander("✅ 3. CASOS RESUELTOS (Histórico)"):
    if not df3.empty:
        df3['Resolucion'] = df3['Resolucion'].apply(formatear_para_leer)
        
        with st.form("f3"):
            c3_cols = ['comentario', 'Cliente', 'Producto', 'diagnostico', 'Estado del RMA', 'Resolucion']
            st_df3 = df3[['id_interno'] + c3_cols]
            
            deshabilitados_t3 = ['Cliente', 'Producto', 'diagnostico', 'Estado del RMA', 'Resolucion']
            
            ed3 = st.data_editor(
                st_df3.style.apply(estilo_filas, axis=1),
                column_config={
                    "id_interno": None,
                    "comentario": st.column_config.TextColumn("💬 Comentario", width="medium"),
                    "diagnostico": st.column_config.TextColumn("🔧 Diagnóstico", width="medium")
                },
                disabled=deshabilitados_t3,
                hide_index=True,
                use_container_width=True
            )
            
            if st.form_submit_button("ACTUALIZAR COMENTARIOS HISTÓRICO"):
                for _, r in ed3.iterrows():
                    orig = df3[df3['id_interno'] == r['id_interno']].iloc[0]
                    up = {k: r[k] for k in ['comentario'] if str(r[k]) != str(orig.get(k, ""))}
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()
