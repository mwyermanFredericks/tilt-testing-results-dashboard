import streamlit as st
import altair as alt
import pandas as pd

from results_dashboard.sidebar import samples, test_select
from results_dashboard.sidebar import show_sidebar

# st.write("Work in progress")

st.set_page_config(
    page_title="Repeatability",
    page_icon=":repeat:",
)

data = show_sidebar()

st.sidebar.write("### Repeatability Options")
repeatability_zeroed = st.sidebar.checkbox("Use zeroed values", value=True, key="repeatability_zeroed")
repeatability_expected = st.sidebar.number_input("Expected Repeatability", value=0.0, key="repeatability_expected", step=0.0001, format="%f")

# Main content

st.header("Repeatability")
st.write(
    """
    Repeatability is a measure of how consistent a sensor is after moving and
    returning to the same angle. It is measured by finding the range
    (max - min) of the sensor output at each angle in the test. The range is
    divided by 2 to give the +/- repeatability.
    """
)

# Options

# By Sensor

st.write("### Repeatability by Sensor")

st.write("""
    This chart shows the repeatability of each sensor in the test. The
    dropdown menu can be used to select which sensors to show.

    If a single sensor is selected, the average repeatability is shown in
    the title and is drawn as a horizontal red line on the graph.
        """)


if data.empty:
    st.warning("No data to display")
else:
    sensors = st.selectbox("Select a sensor", ["All"] + data.sensor_names, key="repeatability_sensor")

    df = data.repeatability_zeroed if repeatability_zeroed else data.repeatability
    if sensors != "All":
        df = df[df.sensor_name == sensors]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("angle", title="Angle (deg)"),
            y=alt.Y("repeatability", title="Repeatability (deg)"),
            color="sensor_name",
            tooltip=["sensor_name", "angle", "repeatability"],
        )
        .interactive()
    )

    if repeatability_expected > 0:
        chart += alt.Chart(pd.DataFrame({"Spec": [repeatability_expected]})).mark_rule().encode(y="Spec")

    if sensors != "All":
        average_repeatability = df.repeatability.mean()
        chart = chart.properties(title=f"{sensors} Repeatability | Avg: {average_repeatability:.5f} deg")
        chart += alt.Chart(pd.DataFrame({"Average": [average_repeatability]})).mark_rule().encode(y="Average", color=alt.value("red"))
    else:
        chart = chart.properties(title="Repeatability")

    st.altair_chart(chart, use_container_width=True)


# By Sensor Group

st.write("### Repeatability by Sensor Group")

st.write("""
    This chart shows the repeatability of each sensor group in the test. The
    sensor group is determined by sensor names of the format <group>-<number>.
    For example, if a test has sensors CC-1, CC-2, CN-1, and CN-2, the sensor
    groups are CC (containing CC-1 and CC-2) and CN (containing CN-1 and CN-2).

    The dropdown menu can be used to select which sensor groups to show.

    If a single sensor group is selected, the average repeatability is shown
    in the title and is drawn as a horizontal red line on the graph.
    """)

if data.empty:
    st.warning("No data to display")
else:
    sensor_groups = st.selectbox("Select a sensor group", ["All"] + data.sensor_groups, key="repeatability_sensor_group")

    df = data.series_repeatability_zeroed if repeatability_zeroed else data.series_repeatability
    if sensor_groups != "All":
        df = df[df.series == sensor_groups]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("angle", title="Angle (deg)"),
            y=alt.Y("repeatability", title="Repeatability (deg)"),
            color="series",
            tooltip=["series", "angle", "repeatability"],
        )
        .interactive()
    )

    if repeatability_expected > 0:
        chart += alt.Chart(pd.DataFrame({"Spec": [repeatability_expected]})).mark_rule().encode(y="Spec")

    if sensor_groups != "All":
        average_repeatability = df.repeatability.mean()
        chart = chart.properties(title=f"{sensor_groups} Repeatability | Avg: {average_repeatability:.5f} deg")
        chart += alt.Chart(pd.DataFrame({"Average": [average_repeatability]})).mark_rule().encode(y="Average", color=alt.value("red"))
    else:
        chart = chart.properties(title="Sensor Group Repeatability")

    st.altair_chart(chart, use_container_width=True)


