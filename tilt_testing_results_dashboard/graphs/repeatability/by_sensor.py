import altair as alt
import pandas as pd
import streamlit as st

from ...data import SensorData


def generate_graph(
    data: SensorData, expected_repeatability: float | None, zeroed: bool
) -> alt.Chart:
    if expected_repeatability is not None and expected_repeatability > 0:
        spec_chart = (
            alt.Chart(pd.DataFrame({"Spec": [expected_repeatability]}))
            .mark_rule()
            .encode(y="Spec")
        )
    else:
        spec_chart = None

    if zeroed:
        df = data.repeatability_zeroed
    else:
        df = data.repeatability

    selection = alt.selection_multi(fields=["sensor_name"], bind="legend")
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("angle", title="Zeroed Angle (° tilt)"),
            alt.Y(
                "repeatability",
                title="Repeatability (±° tilt)",
                scale=alt.Scale(type="log"),
            ),
            color=alt.Color(
                "sensor_name",
                legend=alt.Legend(
                    title="Sensor",
                    orient="none",
                    direction="horizontal",
                    legendX=15,
                    legendY=450,
                    columns=8,
                ),
            ),
            tooltip=[
                alt.Tooltip("sensor_name", title="Sensor"),
                alt.Tooltip("angle", title="Angle"),
                alt.Tooltip("repeatability", title="Repeatability"),
            ],
            opacity=alt.condition(selection, alt.value(1), alt.value(0.15)),
        )
        .add_selection(selection)
    )

    if spec_chart is not None:
        chart += spec_chart

    return chart.interactive()


def display_graph(
    df: pd.DataFrame, expected_repeatability: float | None, zeroed: bool
) -> None:
    chart = generate_graph(df, expected_repeatability, zeroed)
    st.subheader("Repeatability by Sensor")
    st.altair_chart(chart, use_container_width=True)
