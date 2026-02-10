import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

# ===============================
# CONFIGURACIÓN GENERAL
# ===============================
st.set_page_config(
    page_title="Inventiro Conecta",
    page_icon="📦",
    layout="wide"
)

# ===============================
# ESTILO (REUTILIZADO DE TU PROYECTO)
# ===============================
st.markdown("""
<style>
:root {
    --rojo-ur: #9B0029;
    --gris-fondo: #f8f8f8;
    --texto: #222;
}
html, body, .stApp {
    background-color: var(--gris-fondo);
    font-family: "Segoe UI", sans-serif;
}
[data-testid="stSidebar"] {
    background-color: var(--rojo-ur);
}
[data-testid="stSidebar"] * {
    color: white;
    font-weight: 600;
}
.card {
    background-color: white;
    padding: 1.2rem;
    border-radius: 10px;
    border: 1px solid #e6e6e6;
    margin-bottom: 1rem;
}
.section-title {
    color: var(--rojo-ur);
    font-weight: 700;
    font-size: 1.3rem;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# CARGA DE EXCEL BASE (SEDES)
# ===============================
@st.cache_data
def cargar_sedes():
    df = pd.read_excel("/mnt/data/Inventario  Sedes.xlsx")
    df.columns = df.columns.str.strip()
    return df

df_sedes = cargar_sedes()

# ===============================
# LISTAS PREDEFINIDAS
# ===============================
sedes = sorted(df_sedes["Sede"].dropna().unique())

estados_equipo = ["Operativo", "En reparación", "Dado de baja"]
estados_mantenimiento = ["Al día", "Pendiente", "Vencido"]
tipos_mantenimiento = ["Preventivo", "Correctivo", "No aplica"]

# ===============================
# SIDEBAR
# ===============================
st.sidebar.title("📦 Inventiro Conecta")
pagina = st.sidebar.radio(
    "Menú",
    ["📝 Registro de Inventario"]
)

# ===============================
# FORMULARIO PRINCIPAL
# ===============================
if pagina == "📝 Registro de Inventario":

    st.markdown('<div class="section-title">🧾 Registro de Activo Tecnológico</div>', unsafe_allow_html=True)

    with st.form("form_inventario"):

        c1, c2 = st.columns(2)

        with c1:
            sede = st.selectbox("Sede *", ["Seleccione"] + sedes)

            edificios = []
            if sede != "Seleccione":
                edificios = (
                    df_sedes[df_sedes["Sede"] == sede]["Edificio"]
                    .dropna()
                    .unique()
                )

            edificio = st.selectbox("Edificio *", ["Seleccione"] + list(edificios))
            ubicacion = st.text_input("Ubicación")

            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")

        with c2:
            placa = st.text_input("Placa UR *")
            serial = st.text_input("Serial *")
            mac_wifi = st.text_input("MAC WiFi")
            mac_lan = st.text_input("MAC LAN")
            responsable = st.text_input("Responsable del equipo")

        st.divider()

        c3, c4, c5 = st.columns(3)

        with c3:
            estado_equipo = st.selectbox("Estado del equipo", estados_equipo)

        with c4:
            estado_mantenimiento = st.selectbox(
                "Estado del mantenimiento",
                estados_mantenimiento
            )

        with c5:
            tipo_mantenimiento = st.selectbox(
                "Tipo de mantenimiento",
                tipos_mantenimiento
            )

        observaciones = st.text_area(
            "Observaciones",
            height=120,
            placeholder="Observaciones generales del equipo..."
        )

        guardar = st.form_submit_button("💾 Guardar registro")

    # ===============================
    # VALIDACIÓN Y GUARDADO
    # ===============================
    if guardar:

        if sede == "Seleccione" or edificio == "Seleccione":
            st.error("⚠️ Debes seleccionar sede y edificio.")
        elif not placa.strip() or not serial.strip():
            st.error("⚠️ Placa UR y Serial son obligatorios.")
        else:
            registro = {
                "Fecha registro": date.today(),
                "Sede": sede,
                "Edificio": edificio,
                "Ubicación": ubicacion,
                "Marca": marca,
                "Modelo": modelo,
                "Placa UR": placa,
                "Serial": serial,
                "MAC WiFi": mac_wifi,
                "MAC LAN": mac_lan,
                "Responsable": responsable,
                "Estado equipo": estado_equipo,
                "Estado mantenimiento": estado_mantenimiento,
                "Tipo mantenimiento": tipo_mantenimiento,
                "Observaciones": observaciones
            }

            st.success("✅ Registro validado correctamente")
            st.json(registro)  # Visualización temporal (luego se guarda en Sheets o DB)

