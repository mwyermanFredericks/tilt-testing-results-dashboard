import altair as alt
import pandas as pd
import streamlit as st


def get_temperature_over_time(data):
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

    return chart  # .interactive()


def display_graph(data):
    st.subheader("Temperature over Time")
    st.altair_chart(get_temperature_over_time(data), use_container_width=True)
