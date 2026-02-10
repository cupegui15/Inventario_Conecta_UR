import streamlit as st
import pandas as pd
import gspread
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Inventario Conecta UR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CONSTANTES
# =====================================================
SPREADSHEET_ID = "177Cel8v0RcLhNeJ_K6zjwItN7Td2nM1M"
HOJA_DATOS = "Hoja 1"
FILE_ID_SEDES = "PEGA_AQUI_EL_ID_DEL_EXCEL_DE_SEDES"

# =====================================================
# CREDENCIALES
# =====================================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)

# =====================================================
# FUNCIONES
# =====================================================
@st.cache_data
def cargar_sedes():
    request = drive_service.files().get_media(fileId=FILE_ID_SEDES)
    file_bytes = request.execute()
    df = pd.read_excel(io.BytesIO(file_bytes))
    return df.dropna(subset=["Sede", "Edificio"])


@st.cache_data
def cargar_datos():
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(HOJA_DATOS)
    return pd.DataFrame(sheet.get_all_records())


def guardar_dato(fila):
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(HOJA_DATOS)
    sheet.append_row(fila, value_input_option="USER_ENTERED")
    st.cache_data.clear()

# =====================================================
# SIDEBAR (ESTILO MONITOREOS)
# =====================================================
st.sidebar.title("📦 Inventario Conecta UR")

vista = st.sidebar.radio(
    "Vista",
    ["Formulario", "Dashboard"]
)

# =====================================================
# FORMULARIO
# =====================================================
if vista == "Formulario":
    st.subheader("📝 Registro de Inventario")

    df_sedes = cargar_sedes()

    sede = st.selectbox(
        "Sede",
        sorted(df_sedes["Sede"].unique())
    )

    edificio = st.selectbox(
        "Edificio",
        sorted(df_sedes[df_sedes["Sede"] == sede]["Edificio"].unique())
    )

    with st.form("form_inventario"):
        fecha = st.date_input("Fecha")
        area = st.text_input("Área")
        equipo = st.text_input("Equipo")
        estado = st.selectbox("Estado del equipo", ["Bueno", "Regular", "Malo"])
        observaciones = st.text_area("Observaciones")

        guardar = st.form_submit_button("Guardar")

        if guardar:
            guardar_dato([
                str(fecha),
                sede,
                edificio,
                area,
                equipo,
                estado,
                observaciones
            ])
            st.success("✅ Registro guardado correctamente")

# =====================================================
# DASHBOARD (MISMO PATRÓN DE MONITOREOS)
# =====================================================
if vista == "Dashboard":
    st.subheader("📊 Análisis de Inventario")

    df = cargar_datos()

    if df.empty:
        st.warning("No hay datos registrados.")
        st.stop()

    # ---------------------------
    # FILTROS (EN DASHBOARD)
    # ---------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        sede_f = st.selectbox(
            "Sede",
            ["Todas"] + sorted(df["Sede"].unique())
        )

    with c2:
        edificio_f = st.selectbox(
            "Edificio",
            ["Todos"] + sorted(df["Edificio"].unique())
        )

    with c3:
        estado_f = st.selectbox(
            "Estado",
            ["Todos"] + sorted(df["Estado del equipo"].unique())
        )

    if sede_f != "Todas":
        df = df[df["Sede"] == sede_f]

    if edificio_f != "Todos":
        df = df[df["Edificio"] == edificio_f]

    if estado_f != "Todos":
        df = df[df["Estado del equipo"] == estado_f]

    # ---------------------------
    # KPIs (IGUAL MONITOREOS)
    # ---------------------------
    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total registros", len(df))
    k2.metric("Sedes", df["Sede"].nunique())
    k3.metric("Edificios", df["Edificio"].nunique())
    k4.metric("En mal estado", len(df[df["Estado del equipo"] == "Malo"]))

    st.divider()

    # ---------------------------
    # GRÁFICOS
    # ---------------------------
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Estado de equipos**")
        st.bar_chart(df["Estado del equipo"].value_counts())

    with c2:
        st.markdown("**Equipos por sede**")
        st.bar_chart(df["Sede"].value_counts())

    st.divider()

    # ---------------------------
    # TABLA
    # ---------------------------
    st.markdown("### Detalle de registros")
    st.dataframe(df, use_container_width=True)
