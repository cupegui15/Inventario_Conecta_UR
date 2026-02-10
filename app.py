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
# GOOGLE SHEETS (AJUSTADO)
# =====================================================
SPREADSHEET_ID = "1WW00PoA_SJGfJ6qvHNnFk4AhD6FZfOY_jiX2DM7mQjo"
HOJA_DATOS = "Data"

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
    sh = gc.open_by_key(SPREADSHEET_ID)
    sheet = sh.worksheet(HOJA_DATOS)
    return pd.DataFrame(sheet.get_all_records())


def guardar_dato(fila):
    sh = gc.open_by_key(SPREADSHEET_ID)
    sheet = sh.worksheet(HOJA_DATOS)
    sheet.append_row(fila, value_input_option="USER_ENTERED")
    st.cache_data.clear()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("📦 Inventario Conecta UR")

vista = st.sidebar.radio(
    "Vista",
    ["Formulario", "Dashboard", "🔍 Buscar por placa"]
)

# =====================================================
# FORMULARIO
# =====================================================
if vista == "Formulario":
    st.subheader("📝 Registro de Inventario")

    sede = st.selectbox("SEDE", sorted(SEDES_EDIFICIOS.keys()))
    edificio = st.selectbox("EDIFICIO", SEDES_EDIFICIOS[sede])

    with st.form("form_inventario"):
        ubicacion = st.text_input("UBICACION")
        tipo_equipo = st.text_input("TIPO EQUIPO")
        marca = st.text_input("MARCA")
        modelo = st.text_input("MODELO")
        placa_ur = st.text_input("PLACA UR")
        serial = st.text_input("SERIAL")
        monitor_1 = st.text_input("MONITOR 1")
        monitor_2 = st.text_input("MONITOR 2")
        mac_wifi = st.text_input("MAC WIFI")
        mac_lan = st.text_input("MAC LAN")
        responsable = st.text_input("RESPONSABLE EQUIPO")

        estado_equipo = st.selectbox(
            "ESTADO DEL EQUIPO",
            ["Bueno", "Regular", "Malo"]
        )

        estado_mantenimiento = st.selectbox(
            "ESTADO MANTENIMIENTO",
            ["Al día", "Pendiente", "Vencido"]
        )

        tipo_mantenimiento = st.selectbox(
            "TIPO DE MANTENIMIENTO",
            ["Preventivo", "Correctivo", "No aplica"]
        )

        observaciones = st.text_area("OBSERVACIONES")

        guardar = st.form_submit_button("Guardar registro")

        if guardar:
            guardar_dato([
                sede,
                edificio,
                ubicacion,
                tipo_equipo,
                marca,
                modelo,
                placa_ur,
                serial,
                monitor_1,
                monitor_2,
                mac_wifi,
                mac_lan,
                responsable,
                estado_equipo,
                estado_mantenimiento,
                tipo_mantenimiento,
                observaciones
            ])
            st.success("✅ Registro guardado correctamente")

# =====================================================
# DASHBOARD GENERAL
# =====================================================
if vista == "Dashboard":
    st.subheader("📊 Análisis de Inventario")

    df = cargar_datos()

    if df.empty:
        st.warning("No hay datos registrados.")
        st.stop()

    c1, c2, c3 = st.columns(3)

    with c1:
        sede_f = st.selectbox("SEDE", ["Todas"] + sorted(df["SEDE"].unique()))
    with c2:
        edificio_f = st.selectbox("EDIFICIO", ["Todos"] + sorted(df["EDIFICIO"].unique()))
    with c3:
        estado_f = st.selectbox(
            "ESTADO DEL EQUIPO",
            ["Todos"] + sorted(df["ESTADO DEL EQUIPO"].unique())
        )

    if sede_f != "Todas":
        df = df[df["SEDE"] == sede_f]
    if edificio_f != "Todos":
        df = df[df["EDIFICIO"] == edificio_f]
    if estado_f != "Todos":
        df = df[df["ESTADO DEL EQUIPO"] == estado_f]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total registros", len(df))
    k2.metric("Sedes", df["SEDE"].nunique())
    k3.metric("Edificios", df["EDIFICIO"].nunique())
    k4.metric("Equipos en mal estado", len(df[df["ESTADO DEL EQUIPO"] == "Malo"]))

    st.divider()

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Estado del equipo**")
        st.bar_chart(df["ESTADO DEL EQUIPO"].value_counts())
    with g2:
        st.markdown("**Estado mantenimiento**")
        st.bar_chart(df["ESTADO MANTENIMIENTO"].value_counts())

    st.divider()
    st.dataframe(df, use_container_width=True)

# =====================================================
# 🔍 BÚSQUEDA POR PLACA
# =====================================================
if vista == "🔍 Buscar por placa":
    st.subheader("🔍 Búsqueda por PLACA UR")

    df = cargar_datos()

    if df.empty:
        st.warning("No hay datos registrados.")
        st.stop()

    placa_busqueda = st.text_input(
        "Ingrese la PLACA UR",
        placeholder="Ej: UR-12345"
    )

    if placa_busqueda:
        resultado = df[df["PLACA UR"].astype(str).str.upper() == placa_busqueda.upper()]

        if resultado.empty:
            st.error("❌ No se encontró información para esa placa.")
        else:
            st.success(f"✅ Información encontrada para la placa {placa_busqueda}")
            st.dataframe(resultado, use_container_width=True)
