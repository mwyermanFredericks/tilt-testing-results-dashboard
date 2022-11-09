import streamlit as st
import altair as alt

from results_dashboard.data import SensorData
from results_dashboard.data.mongo import tests_db
from results_dashboard.ui import samples, test_select

# Sidebar/Multipage

st.set_page_config(
    page_title="Data Over Time",
    page_icon=":line_chart:",
        )
st.sidebar.title("Data Over Time")
selected_ids = test_select.get_test_selection_sidebar()
data = samples.show_samples_sidebar(selected_ids)

# Main content

st.header("Data over Time")
st.write(
    "These graphs show various metrics over time during a test."
    " This gives a basic overview of the test process and can"
    " highlight any major performance issues."
)

# Angle over Time

st.subheader("Set Angle vs Time")

if data.empty:
    st.warning("No data to show")
else:
    df = data.downsampled[["sample_time", "set_angle", "stage_angle"]]
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("sample_time", title="Time"),
            alt.Y("set_angle", title="Angle (° tilt)"),
            tooltip=[
                alt.Tooltip("sample_time", title="Time"),
                alt.Tooltip("set_angle", title="Angle"),
                alt.Tooltip("stage_angle", title="Reported Stage Angle"),
            ],
        )
        .properties(title="Set Angle vs Time")
        .interactive()
    )
    st.altair_chart(chart, use_container_width=True)

# Temperature over Time

st.subheader("Temperature over Time")


if data.empty:
    st.warning("No data to show")

else:
    cols = {
        "oven_set_temperature": "Setpoint",
        "oven_integrated_temperature": "PID Reading",
        "thermocouple_temperature": "Thermocouple Reading",
        "ambient_temperature": "Ambient",
    }
    df = data.downsampled[list(cols.keys())]
    df = df.rename(columns=cols)
    df = df.rename_axis("Time").reset_index()

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("Time"),
            alt.Y(alt.repeat("layer"), aggregate="mean", title="Temperature (°C)"),
            color=alt.ColorDatum(alt.repeat("layer")),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("Setpoint", title="Setpoint"),
                alt.Tooltip("PID Reading", title="PID Reading"),
                alt.Tooltip("Thermocouple Reading", title="Thermocouple Reading"),
                alt.Tooltip("Ambient", title="Ambient"),
            ],
        )
        .properties(title="Temperature vs Time")
        .repeat(layer=list(cols.values()))
        .configure_legend(
            direction="horizontal", orient="none", legendY=485, legendX=15
        )
    )
    st.altair_chart(chart, use_container_width=True)

