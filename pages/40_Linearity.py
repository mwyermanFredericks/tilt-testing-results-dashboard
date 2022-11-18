import streamlit as st
import altair as alt
from scipy.stats import linregress

from results_dashboard.sidebar import show_sidebar


st.set_page_config(
    page_title="Linearity",
    page_icon=":bar_chart:",
)

data = show_sidebar()
st.sidebar.write("### Linearity Options")
zeroed = st.sidebar.checkbox("Use zeroed values", value=True, key="zeroed")
linear_range = st.sidebar.number_input("Linear Range", value=0.0, key="linear_range", step=0.1, format="%f")

st.write("# Linearity")
st.write("""
        Linearity is a measure of how linear the sensor's raw output is relative
        to the angle of tilt.
        """)

# By Sensor

st.write("### By Sensor")
st.write("""
        The following plots show the linearity of each sensor.

        Individual sensors can be selected using the dropdown menu.
        If a sensor is selected, the plot will show the linear best fit line,
        as well as a calculated R-squared value.
        """)

if data.empty:
    st.warning("No data to display")
else:


    try:
        df = data.linearity(zeroed)
    except KeyError:
        st.warning("Zeroing error. Showing unzeroed values")
        df = data.linearity(False)

    angle_col = "angle"

    if linear_range > 0:
        df = df[(df[angle_col] <= linear_range) & (df[angle_col] >= -linear_range)]


    sensors = st.selectbox("Select a sensor", ["All"] + data.sensor_names, key="linearity_sensor")
    if sensors != "All":
        sensor_df = df.loc[df.sensor_name == sensors]
    else:
        sensor_df = df


    avg_chart = (
        alt.Chart(sensor_df)
        .mark_line()
        .encode(
            x=alt.X(angle_col, title="Angle (deg)"),
            y=alt.Y("mean_raw", title="Raw Output", scale=alt.Scale(zero=False)),
            color=alt.Color("sensor_name", title="Sensor"),
        )
    ) 
    area_chart = (
        alt.Chart(sensor_df)
        .mark_area(opacity=0.3)
        .encode(
            alt.X(angle_col, title="Angle (deg)"),
            alt.Y("max_raw", title="Raw Output"),
            alt.Y2("min_raw"),
            color=alt.Color("sensor_name", title="Sensor"),
            tooltip=[
                alt.Tooltip("sensor_name", title="Sensor"),
                alt.Tooltip("angle", title="Angle (deg)"),
                alt.Tooltip("mean_raw", title="Raw Output"),
                alt.Tooltip("max_raw", title="Max Raw Output"),
                alt.Tooltip("min_raw", title="Min Raw Output"),
                alt.Tooltip("dev_raw", title="Raw Output Std Deviation"),
            ],
        )
    )


    title = "Linearity"
    if linear_range > 0:
        title += f" (+/-{linear_range} deg)"

    if sensors != "All":

        # calculate linear line of best fit
        avg_chart += (
            avg_chart
            .transform_regression(angle_col, "mean_raw", method="linear")
            .mark_line(strokeDash=[5, 5], color="red")
            .encode(
                alt.Color(legend=None)
            )
        )

        title += f" | R-squared: {linregress(sensor_df[angle_col], sensor_df['mean_raw']).rvalue**2:.5f}"

    chart = (area_chart + avg_chart).properties(title=title)


    st.altair_chart(chart.interactive(), use_container_width=True)


    st.write("### By Group")
    st.write("""
        The following plots show the linearity of each sensor group.

        Different sensor groups can be selected using the dropdown menu.
        If a group is selected, the plot will show the linear best fit line,
        as well as a calculated R-squared value.

        Currently, the R-squared and linear best fit line are calculated using
        all of the data for each sensor concatenated together. This may result
        in worst linearity results if the sensors do not have very similar
        raw outputs over the given range.
        """)

    groups = st.selectbox("Select a group", ["All"] + data.sensor_groups, key="linearity_group")

    try:
        df = data.linearity(zeroed, series=True)
    except KeyError:
        st.warning("Zeroing error. Showing unzeroed values")
        df = data.linearity(False, series=True)

    if linear_range > 0:
        df = df[(df[angle_col] <= linear_range) & (df[angle_col] >= -linear_range)]

    if groups != "All":
        df = df.loc[df.series == groups]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X(angle_col, title="Angle (deg)"),
            y=alt.Y("mean_raw", title="Raw Output"),
            color=alt.Color("series", title="Sensor Group"),
        )
    )

    title = "Linearity"
    if linear_range > 0:
        title += f" (+/-{linear_range} deg)"

    if groups != "All":
        # calculate linear line of best fit
        chart += (
                chart
                .transform_regression(angle_col, "mean_raw", method="linear")
                .mark_line(strokeDash=[5, 5], color="red")
                .encode(
                    alt.Color(legend=None)
                )
            )
        title += f" | R-squared: {linregress(df[angle_col], df['mean_raw']).rvalue**2:.5f}"

    chart += (
        alt.Chart(df)
        .mark_area(opacity=0.3)
        .encode(
            alt.X(angle_col, title="Angle (deg)"),
            alt.Y("max_raw", title="Raw Output"),
            alt.Y2("min_raw"),
            color=alt.Color("series", title="Sensor Group"),
            tooltip=[
                alt.Tooltip("series", title="Sensor Group"),
                alt.Tooltip(angle_col, title="Angle (deg)"),
                alt.Tooltip("mean_raw", title="Raw Output"),
                alt.Tooltip("max_raw", title="Max Raw Output"),
                alt.Tooltip("min_raw", title="Min Raw Output"),
            ],
        )
    )

    chart = chart.properties(title=title)


    st.altair_chart(chart, use_container_width=True)
