import altair as alt
import pandas as pd
import streamlit as st

from results_dashboard.sidebar import show_sidebar

# st.write("Work in progress")

st.set_page_config(
    page_title="Repeatability",
    page_icon="https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png",
)

data = show_sidebar()

st.sidebar.write("### Repeatability Options")
zeroed = st.sidebar.checkbox("Use zeroed values", value=True, key="zeroed")
repeatability_expected = st.sidebar.number_input(
    "Expected Repeatability",
    value=0.0,
    key="repeatability_expected",
    step=0.0001,
    format="%f",
)

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

st.write(
    """
    This chart shows the repeatability of each sensor in the test. The
    dropdown menu can be used to select which sensors to show.

    If a single sensor is selected, the average repeatability is shown in
    the title and is drawn as a horizontal red line on the graph.

    There is also an option to drop rows. This will drop the first n
    rows from the data before calculating the repeatability. This can be
    useful if there is an issue with the early samples that has a negative
    impact on the repeatability. Note that a row is a single sample for a
    single sensor. This means the number of rows to drop will vary depending
    on the test parameters. For example, if the test contains 10 sensors and
    takes 10 samples for each angle, 100 rows should be dropped to remove the
    first angle step in the test.
        """
)


if data.empty:
    st.warning("No data to display")
else:
    sensors = st.selectbox(
        "Select a sensor", ["All"] + data.sensor_names, key="repeatability_sensor"
    )

    dropped_rows = st.number_input(
        "Dropped Rows", value=0, key="repeatability_dropped_rows"
    )

    try:
        df = data.repeatability(zeroed=zeroed, dropped_rows=dropped_rows)
    except KeyError:
        st.warning("Zeroing error. Showing unzeroed values")
        df = data.repeatability(dropped_rows=dropped_rows)

    if sensors != "All":
        df = df[df.sensor_name == sensors]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("angle", title="Angle (deg)"),
            y=alt.Y(
                "repeatability",
                title="Repeatability (deg)",
                scale=alt.Scale(type="symlog", constant=0.0001),
            ),
            color="sensor_name",
            tooltip=["sensor_name", "angle", "repeatability"],
        )
        .interactive()
    )

    if repeatability_expected > 0:
        chart += (
            alt.Chart(pd.DataFrame({"Spec": [repeatability_expected]}))
            .mark_rule(color="green")
            .encode(y="Spec")
        )

    if sensors != "All":
        average_repeatability = df.repeatability.mean()
        chart = chart.properties(
            title=f"{sensors} Repeatability | Avg: {average_repeatability:.5f} deg"
        )
        chart += (
            alt.Chart(pd.DataFrame({"Average": [average_repeatability]}))
            .mark_rule(color="red")
            .encode(y="Average", color=alt.value("red"))
        )
    else:
        chart = chart.properties(title="Repeatability")

    st.altair_chart(chart, use_container_width=True, theme="streamlit")


# By Sensor Group

st.write("### Repeatability by Sensor Group")

st.write(
    """
    This chart shows the repeatability of each sensor group in the test. The
    sensor group is determined by sensor names of the format <group>-<number>.
    For example, if a test has sensors CC-1, CC-2, CN-1, and CN-2, the sensor
    groups are CC (containing CC-1 and CC-2) and CN (containing CN-1 and CN-2).

    The dropdown menu can be used to select which sensor groups to show.

    If a single sensor group is selected, the average repeatability is shown
    in the title and is drawn as a horizontal red line on the graph.
    """
)

if data.empty:
    st.warning("No data to display")
else:
    sensor_groups = st.selectbox(
        "Select a sensor group",
        ["All"] + data.sensor_groups,
        key="repeatability_sensor_group",
    )

    dropped_rows = st.number_input(
        "Dropped Rows", value=0, key="repeatability_sensor_group_dropped_rows"
    )

    try:
        df = data.repeatability(zeroed=zeroed, series=True, dropped_rows=dropped_rows)
    except KeyError:
        st.warning("Zeroing error. Showing unzeroed values")
        df = data.repeatability(series=True, dropped_rows=dropped_rows)

    if sensor_groups != "All":
        df = df[df.series == sensor_groups]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("angle", title="Angle (deg)"),
            y=alt.Y(
                "mean_repeatability",
                title="Repeatability (deg)",
                scale=alt.Scale(type="symlog", constant=0.0001),
            ),
            color=alt.Color("series", title="Sensor Group"),
        )
    )

    if sensor_groups != "All":
        chart += (
            alt.Chart(df)
            .mark_area(opacity=0.3)
            .encode(
                alt.X("angle", title="Angle (deg)"),
                alt.Y("max_repeatability", title="Repeatability (deg)"),
                alt.Y2("min_repeatability"),
                color=alt.Color("series", title="Sensor Group"),
                tooltip=["series", "angle", "mean_repeatability"],
            )
        )

    if repeatability_expected > 0:
        chart += (
            alt.Chart(pd.DataFrame({"Spec": [repeatability_expected]}))
            .mark_rule(color="green")
            .encode(y="Spec")
        )

    if sensor_groups != "All":
        average_repeatability = df.mean_repeatability.mean()
        chart = chart.properties(
            title=f"{sensor_groups} Repeatability | Avg: {average_repeatability:.6f} deg"
        )
        chart += (
            alt.Chart(pd.DataFrame({"Average": [average_repeatability]}))
            .mark_rule(color="red")
            .encode(y="Average", color=alt.value("red"))
        )
    else:
        chart = chart.properties(title="Sensor Group Repeatability")

    st.altair_chart(chart.interactive(), use_container_width=True, theme="streamlit")

st.write("### Repeatability Characteristics")

st.write(
    """
    This chart trys to help visualize the nature of the repeatability. This
    will show the residual values of the repeatability over time in the  test.
    The residual is calculated based on the sensor's average output at a
    given angle. This should help to identify whether the repeatability is
    due to a sensor's output drifting over time or if it is due to the
    sensor's output being inconsistent.
    """
)


if data.empty:
    st.warning("No data to display")
else:
    df = data.repeatability_residuals()

    sensors = st.selectbox(
        "Select a sensor",
        ["All"] + data.sensor_names,
        key="repeatability_residual_sensor",
    )

    angles = data.set_angles
    angle_range = st.slider(
        "Angle Range",
        min_value=angles[0],
        max_value=angles[-1],
        value=(angles[0], angles[-1]),
        key="repeatability_residual_angle_range",
    )

    if sensors != "All":
        df = df[df["sensor_name"] == sensors]

    df = df[(df["set_angle"] >= angle_range[0]) & (df["set_angle"] <= angle_range[1])]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("sample_time", title="Time"),
            y=alt.Y("residual", title="Residual (deg)"),
            color="sensor_name",
            tooltip=[
                "sensor_name",
                "sample_time",
                "sensor_degrees",
                "residual",
                "set_angle",
            ],
        )
    )

    if sensors != "All":
        # chart = chart.properties(title=f"{sensors} Repeatability Residuals")
        title = f"{sensors} Repeatability Residuals"
    else:
        # chart = chart.properties(title="Repeatability Residuals")
        title = "Repeatability Residuals"

    if angle_range[0] != angles[0] or angle_range[1] != angles[-1]:
        # title += f" | {angle_range[0]}° - {angle_range[1]}°"
        title += f" | {round(angle_range[0], 4)}° - {round(angle_range[1], 4)}°"
    chart = chart.properties(title=title)

    st.altair_chart(chart.interactive(), use_container_width=True, theme="streamlit")
