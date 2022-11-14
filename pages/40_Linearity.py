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
    if zeroed:
        df = data.zeroed_samples
        angle_col = "zeroed_set_angle"
    else:
        df = data.samples
        angle_col = "set_angle"

    if linear_range > 0:
        df = df[(df[angle_col] <= linear_range) & (df[angle_col] >= -linear_range)]


    sensors = st.selectbox("Select a sensor", ["All"] + data.sensor_names, key="linearity_sensor")
    if sensors != "All":
        sensor_df = df.loc[df.sensor_name == sensors]
    else:
        sensor_df = df


    chart = (
        alt.Chart(sensor_df)
        .mark_circle(size=60)
        .encode(
            x=alt.X(angle_col, title="Angle (deg)"),
            y=alt.Y("raw", title="Raw Output"),
            color=alt.Color("sensor_name", title="Sensor"),
            tooltip=["sensor_name", angle_col, "raw"],
        )
    )

    title = "Linearity"
    if linear_range > 0:
        title += f" (+/-{linear_range} deg)"

    if sensors != "All":
        # calculate linear line of best fit
        chart += (
                chart
                .transform_regression(angle_col, "raw", method="linear")
                .mark_line(strokeDash=[5, 5])
                .encode(
                    alt.Color(legend=None)
                )
            )
        title += f" | R-squared: {linregress(sensor_df[angle_col], sensor_df['raw']).rvalue**2:.5f}"

    chart = chart.properties(title=title)


    st.altair_chart(chart, use_container_width=True)


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
    if groups != "All":
        group_df = df.loc[df.series == groups]
    else:
        group_df = df

    chart = (
        alt.Chart(group_df)
        .mark_circle(size=60)
        .encode(
            x=alt.X(angle_col, title="Angle (deg)"),
            y=alt.Y("raw", title="Raw Output"),
            color=alt.Color("series", title="Sensor Group"),
            tooltip=["series", angle_col, "raw"],
        )
    )

    title = "Linearity"
    if linear_range > 0:
        title += f" (+/-{linear_range} deg)"

    if groups != "All":
        # calculate linear line of best fit
        chart += (
                chart
                .transform_regression(angle_col, "raw", method="linear")
                .mark_line(strokeDash=[5, 5])
                .encode(
                    alt.Color(legend=None)
                )
            )
        title += f" | R-squared: {linregress(group_df[angle_col], group_df['raw']).rvalue**2:.5f}"

    chart = chart.properties(title=title)


    st.altair_chart(chart, use_container_width=True)
