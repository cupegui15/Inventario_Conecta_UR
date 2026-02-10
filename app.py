import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Inventario Conecta UR",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# SEDES Y EDIFICIOS (DEFINIDOS EN CÓDIGO)
# =====================================================
SEDES_EDIFICIOS = {
    "CENTRO": [
        "CECILIA HERNANDEZ 12C",
        "CLAUSTRO - CRAI",
        "CLAUSTRO - CASUR",
        "CLAUSTRO - TORRE 1",
        "CLAUSTRO - TORRE 2",
        "CLAUSTRO TORRE 2",
        "DAVILA",
        "EL TIEMPO",
        "PEDRO FERMIN",
        "SURAMERICANA"
    ],
    "GSB": ["GSB"],
    "MEDERI": ["GSB"],
    "NORTE": [
        "FCI",
        "MODULO 1",
        "MODULO 2",
        "MODULO 3",
        "MODULO 4",
        "MODULO 5",
        "MODULO 6",
        "MODULO 7",
        "MODULO 8",
        "MODULO D"
    ],
    "QUINTA MUTIS": [
        "AULARIOS NUEVOS",
        "CRAI",
        "MODULO ANTIGUO",
        "QUINTA MUTIS",
        "Salón de Danzas"
    ]
}

# =====================================================
# GOOGLE SHEETS
# =====================================================
SPREADSHEET_ID = "177Cel8v0RcLhNeJ_K6zjwItN7Td2nM1M"
HOJA_DATOS = "Datos"

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

# =====================================================
# FUNCIONES
# =====================================================
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

    sede = st.selectbox(
        "Sede",
        sorted(SEDES_EDIFICIOS.keys())
    )

    edificio = st.selectbox(
        "Edificio",
        SEDES_EDIFICIOS[sede]
    )

    with st.form("form_inventario"):
        fecha = st.date_input("Fecha")
        area = st.text_input("Área")
        equipo = st.text_input("Equipo")
        estado = st.selectbox(
            "Estado del equipo",
            ["Bueno", "Regular", "Malo"]
        )
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
# DASHBOARD (MISMO DISEÑO DE MONITOREOS)
# =====================================================
if vista == "Dashboard":
    st.subheader("📊 Análisis de Inventario")

    df = cargar_datos()

    if df.empty:
        st.warning("No hay datos registrados.")
        st.stop()

    # ---------------------------
    # FILTROS
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
    # KPIs
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
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("**Estado de equipos**")
        st.bar_chart(df["Estado del equipo"].value_counts())

    with g2:
        st.markdown("**Equipos por sede**")
        st.bar_chart(df["Sede"].value_counts())

    st.divider()

    # ---------------------------
    # TABLA
    # ---------------------------
    st.markdown("### Detalle de registros")
    st.dataframe(df, use_container_width=True)
