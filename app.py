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
