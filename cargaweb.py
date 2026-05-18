import streamlit as st
from pyairtable import Api
import pandas as pd
from datetime import datetime, date
import io

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel RMA", layout="wide")

# CSS: Bordes de 4px, FUENTE UNIFICADA y trucos para celdas editables coloridas
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

        /* Fuerza a los inputs editables a transparentar su fondo para ver el Styler */
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
    if not fecha_raw or str(fecha_raw).strip() == "": return ""
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

# FILA 1 DE BOTONES
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.link_button("🔵 Airtable", "https://airtable.com/appjlLix1HpBwnhpS/tblNnoXdIsLFN92Mr/viwLRiCozAc4oVKZY", use_container_width=True)
with c2: st.link_button("💻 Github", "https://github.com/FedeASA/consulta-rma", use_container_width=True)
with c3: st.link_button("📝 Texto Clientes", "https://docs.google.com/document/d/1URgFPuVsIoR6LX2diAwFR5rWRKYvmmEwvQ7VXuxSnYg", use_container_width=True)
with c4: st.selectbox("🚀 Páginas", ["Navegar...", "Formulario", "Consulta"], label_visibility="collapsed")
with c5: st.link_button("📊 Excel Viejo", "https://docs.google.com/spreadsheets/d/17zp1kEZhVBw1Ul3HkoDZhyQ2IYthjNGS", use_container_width=True)

# FILA 2: REPORTE
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
                for f in ['Compra', 'Ingreso', 'Resolucion']:
                    df_exc[f] = df_exc[f].apply(formatear_para_leer)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_exc.to_excel(writer, index=False, sheet_name='Reporte', startrow=1)
                    writer.sheets['Reporte'].write(0, 0, f"Cliente: {cliente_buscado}")
                
                st.download_button(f"📥 Descargar Reporte {cliente_buscado}", output.getvalue(), f"Reporte_{cliente_buscado}.xlsx", "application/vnd.ms-excel")
            else:
                st.warning("No hay datos para ese cliente.")

st.divider()

# --- 4. TABLAS (RENDERING) ---
if df_all.empty:
    st.warning("No hay datos para mostrar.")
    st.stop()

# Asegurar columnas globales y unificar minúscula de 'diagnostico' acorde a base de datos
for col in ['Aceptado', 'Finalizado', 'Ingreso', 'Resolucion', 'diagnostico', 'Estado del RMA', 'Compra', 'Producto', 'comentario', 'Falla']:
    if col not in df_all.columns: 
        df_all[col] = False if col in ['Aceptado', 'Finalizado'] else ""
    if col in ['Aceptado', 'Finalizado']:
        df_all[col] = df_all[col].apply(lambda x: True if x in [True, 1, "True", "true"] else False)

# Forzar limpieza de valores vacíos o nulos en campos de texto editables
for col_texto in ['comentario', 'Falla', 'diagnostico', 'Ingreso', 'Resolucion', 'Compra']:
    if col_texto in df_all.columns:
        df_all[col_texto] = df_all[col_texto].fillna("").apply(lambda x: "" if str(x).strip() in ["None", "none", "nan", "NaN", ""] else str(x))

# TABLA 1: POR ACEPTAR
df1 = df_all[(df_all['Aceptado'] == False) & (df_all['Producto'].fillna("").str.strip() != "")].copy()
with st.expander("📥 1. TICKETS POR ACEPTAR (Entrada)", expanded=True):
    if not df1.empty:
        df1['Compra'] = df1['Compra'].apply(formatear_para_leer)
        with st.form("f1"):
            c1_cols = ['Cliente', 'Producto', 'Serial', 'Falla', 'Compra', 'Aceptado']
            ed1 = st.data_editor(df1[['id_interno'] + c1_cols].reset_index(drop=True), column_config={"id_interno":None}, disabled=['Serial','Falla'], hide_index=True, use_container_width=True)
            if st.form_submit_button("GUARDAR ENTRADAS"):
                for _, r in ed1.iterrows():
                    orig = df1[df1['id_interno']==r['id_interno']].iloc[0]
                    up = {k: r[k] for k in ['Aceptado','Cliente','Producto'] if str(r[k])!=str(orig.get(k,""))}
                    f, e = formatear_y_validar_fecha(r['Compra'])
                    if e=="OK" and f: up['Compra'] = f
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()
    else: st.info("No hay pendientes.")

# TABLA 2: EN PROCESO
df2 = df_all[(df_all['Aceptado'] == True) & (df_all['Finalizado'] == False)].copy().reset_index(drop=True)
with st.expander("⚙️ 2. TICKETS EN PROCESO (Aceptados)", expanded=True):
    if not df2.empty:
        for c in ['Compra','Ingreso','Resolucion']: 
            df2[c] = df2[c].apply(formatear_para_leer)
        
        with st.form("f2"):
            c2_cols = ['comentario', 'Cliente', 'Producto', 'Compra', 'Falla', 'Ingreso', 'diagnostico', 'Estado del RMA', 'Resolucion', 'Finalizado']
            st_df2 = df2[['id_interno'] + c2_cols]
            
            ed2 = st.data_editor(
                st_df2.style.apply(estilo_filas, axis=1), 
                column_config={
                    "id_interno": None, 
                    "comentario": st.column_config.TextColumn("💬 Comentario", width="medium"),
                    "diagnostico": st.column_config.TextColumn("🔧 Diagnóstico", width="medium"),
                    "Finalizado": st.column_config.CheckboxColumn("Finalizar"), 
                    "Estado del RMA": st.column_config.SelectboxColumn(options=["CAMBIO", "CREDITO", "GARANTIA OFICIAL", "GARANTIA", "FUERA DE GARANTIA", "NO FALLO - DEVOLVER A CLIENTE", "REPARADO"])
                }, 
                disabled=['Cliente', 'Producto', 'Compra', 'Falla'], 
                hide_index=True, 
                use_container_width=True
            )
            
            if st.form_submit_button("ACTUALIZAR PROCESOS"):
                for _, r in ed2.iterrows():
                    orig = df2[df2['id_interno'] == r['id_interno']].iloc[0]
                    up = {k: r[k] for k in ['comentario', 'diagnostico', 'Estado del RMA', 'Finalizado'] if str(r[k]) != str(orig.get(k, ""))}
                    for f in ['Ingreso', 'Resolucion']:
                        val, stt = formatear_y_validar_fecha(r[f])
                        if stt == "OK": up[f] = val
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()

# TABLA 3: HISTÓRICO
df3 = df_all[(df_all['Aceptado'] == True) & (df_all['Finalizado'] == True)].copy().reset_index(drop=True)
with st.expander("✅ 3. CASOS RESUELTOS (Histórico)"):
    if not df3.empty:
        df3['Resolucion'] = df3['Resolucion'].apply(formatear_para_leer)
        
        with st.form("f3"):
            c3_cols = ['comentario', 'Cliente', 'Producto', 'diagnostico', 'Estado del RMA', 'Resolucion']
            st_df3 = df3[['id_interno'] + c3_cols]
            
            ed3 = st.data_editor(
                st_df3.style.apply(estilo_filas, axis=1),
                column_config={
                    "id_interno": None,
                    "comentario": st.column_config.TextColumn("💬 Comentario", width="medium"),
                    "diagnostico": st.column_config.TextColumn("🔧 Diagnóstico", width="medium")
                },
                disabled=['Cliente', 'Producto', 'diagnostico', 'Estado del RMA', 'Resolucion'],
                hide_index=True,
                use_container_width=True
            )
            
            if st.form_submit_button("ACTUALIZAR COMENTARIOS HISTÓRICO"):
                for _, r in ed3.iterrows():
                    orig = df3[df3['id_interno'] == r['id_interno']].iloc[0]
                    up = {k: r[k] for k in ['comentario'] if str(r[k]) != str(orig.get(k, ""))}
                    if up: table.update(r['id_interno'], up)
                st.cache_data.clear(); st.rerun()