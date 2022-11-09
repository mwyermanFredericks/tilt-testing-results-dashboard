import altair as alt
import pandas as pd
import streamlit as st

from ...data import SensorData


def generate_graph(data: SensorData, expected_accuracy: float | None) -> alt.Chart:
    if expected_accuracy is not None and expected_accuracy > 0:
        spec_chart = (
            alt.Chart(pd.DataFrame({"Spec": [expected_accuracy]}))
            .mark_rule()
            .encode(y="Spec")
        )
    else:
        spec_chart = None

    df = data.accuracy

    selection = alt.selection_multi(fields=["sensor_name"], bind="legend")
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("angle", title="Set Angle (° tilt)"),
            alt.Y(
                "error",
                title="Error (±° tilt)",
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
                alt.Tooltip("angle", title="Set Angle"),
                alt.Tooltip("error", title="Mean Error"),
                alt.Tooltip("error.max", title="Maximum Error"),
                alt.Tooltip("error.min", title="Minimum Error"),
            ],
            opacity=alt.condition(selection, alt.value(1), alt.value(0.15)),
        )
        .add_selection(selection)
    )

    if spec_chart is not None:
        chart += spec_chart

    return chart.interactive()


def display_graph(df: pd.DataFrame, expected_accuracy: float | None) -> None:
    chart = generate_graph(df, expected_accuracy)
    st.subheader("Accuracy by Sensor")
    st.altair_chart(chart, use_container_width=True)
