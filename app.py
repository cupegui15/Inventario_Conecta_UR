import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =====================================
# CONFIGURACIÓN GENERAL
# =====================================
st.set_page_config(
    page_title="Inventario Conecta UR",
    layout="wide"
)

# =====================================
# CONSTANTES
# =====================================
SPREADSHEET_ID = "177Cel8v0RcLhNeJ_K6zjwItN7Td2nM1M"
HOJA_DATOS = "Data"  # Cambia si tu hoja tiene otro nombre

# =====================================
# CREDENCIALES GOOGLE
# =====================================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(creds)

# =====================================
# FUNCIONES
# =====================================
@st.cache_data
def cargar_datos():
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(HOJA_DATOS)
    data = sheet.get_all_records()
    return pd.DataFrame(data)


def guardar_datos(fila):
    sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(HOJA_DATOS)
    sheet.append_row(fila, value_input_option="USER_ENTERED")
    st.cache_data.clear()

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("📦 Inventario Conecta UR")
vista = st.sidebar.radio(
    "Menú",
    ["Formulario", "Dashboard"]
)

# =====================================
# FORMULARIO
# =====================================
if vista == "Formulario":
    st.title("📝 Registro de Inventario")

    with st.form("form_inventario"):
        fecha = st.date_input("Fecha")
        sede = st.text_input("Sede")
        area = st.text_input("Área")
        equipo = st.text_input("Equipo")
        estado = st.selectbox("Estado del equipo", ["Bueno", "Regular", "Malo"])
        observaciones = st.text_area("Observaciones")

        enviar = st.form_submit_button("Guardar registro")

        if enviar:
            guardar_datos([
                str(fecha),
                sede,
                area,
                equipo,
                estado,
                observaciones
            ])
            st.success("✅ Registro guardado correctamente")

# =====================================
# DASHBOARD
# =====================================
if vista == "Dashboard":
    st.title("📊 Análisis de Inventario")

    df = cargar_datos()

    if df.empty:
        st.warning("⚠️ No hay datos registrados aún.")
        st.stop()

    # -------------------------
    # FILTROS
    # -------------------------
    c1, c2, c3 = st.columns(3)

    with c1:
        sede_filtro = st.selectbox(
            "Filtrar por sede",
            ["Todas"] + sorted(df["Sede"].unique())
        )

    with c2:
        estado_filtro = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + sorted(df["Estado del equipo"].unique())
        )

    with c3:
        area_filtro = st.selectbox(
            "Filtrar por área",
            ["Todas"] + sorted(df["Área"].unique())
        )

    if sede_filtro != "Todas":
        df = df[df["Sede"] == sede_filtro]

    if estado_filtro != "Todos":
        df = df[df["Estado del equipo"] == estado_filtro]

    if area_filtro != "Todas":
        df = df[df["Área"] == area_filtro]

    # -------------------------
    # KPIs
    # -------------------------
    k1, k2, k3 = st.columns(3)
    k1.metric("Total registros", len(df))
    k2.metric("Equipos en mal estado", len(df[df["Estado del equipo"] == "Malo"]))
    k3.metric("Sedes únicas", df["Sede"].nunique())

    # -------------------------
    # GRÁFICOS NATIVOS
    # -------------------------
    st.subheader("📊 Estado de los equipos")
    st.bar_chart(df["Estado del equipo"].value_counts())

    st.subheader("📊 Registros por sede")
    st.bar_chart(df["Sede"].value_counts())

    # -------------------------
    # TABLA
    # -------------------------
    st.subheader("📋 Detalle de registros")
    st.dataframe(df, use_container_width=True)
