import streamlit as st
import altair as alt

from results_dashboard.data import SensorData
from results_dashboard.data.mongo import tests_db
from results_dashboard.sidebar import show_sidebar

# Sidebar/Multipage

st.set_page_config(
    page_title="Data Over Time",
    page_icon="https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png",
        )

data = show_sidebar()

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
    # df = data.downsampled[["sample_time", "set_angle", "stage_angle"]]
    df = data.angle_data
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
    df = data.temperature_data

    chart = (
        alt.Chart(data.temperature_data)
        .mark_line()
        .encode(
            x=alt.X("sample_time", title="Time"),
            y=alt.Y("mean", title="Temperature (°C)"),
            color=alt.Color("source", title="Temperature Source"),
            tooltip=[
                alt.Tooltip("source", title="Temperature Source"),
                alt.Tooltip("mean", title="Temperature (°C)"),
                alt.Tooltip("max", title="Max Temperature (°C)"),
                alt.Tooltip("min", title="Min Temperature (°C)"),
                alt.Tooltip("dev", title="Temperature Std Deviation (°C)"),
            ],
        )
    )

    chart = chart.properties(title="Temperature over Time").interactive()

    st.altair_chart(chart, use_container_width=True)
