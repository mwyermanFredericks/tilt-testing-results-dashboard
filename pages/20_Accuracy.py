import streamlit as st
import altair as alt
import pandas as pd

from results_dashboard.data import SensorData
from results_dashboard.data.mongo import tests_db
from results_dashboard.sidebar import show_sidebar

# Sidebar/Multipage

st.set_page_config(
    page_title="Accuracy",
    page_icon=":line_chart:",
        )

data = show_sidebar()

st.sidebar.write("### Accuracy Options")
expected_accuracy = st.sidebar.number_input("Expected Accuracy")

# Main content

st.header("Accuracy")
st.write(
    "Sensor accuracy is a test of how well the linearization algorithm "
    "performs. It is calculated by taking the difference between the "
    "sensor output and the set angle. The difference is then averaged "
    "over all samples at each angle."
)
st.write(
    "For bare sensors and unlinearized boards, this will be a measure "
    "of how well the test performed the linearization. For linearized "
    "boards, this will be a measure of how well the linearization "
    "algorithm of the sensor itself performed. For this reason, this"
    "test is normally only useful for linearized boards."
)

# Expected Accuracy


# By Sensor
st.subheader("Accuracy by Sensor")

if data.empty:
    st.warning("No data to display")

else:
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

    st.altair_chart(chart.interactive(), use_container_width=True)
