import traceback

import numpy as np
import streamlit as st
import altair as alt
from sklearn.linear_model import LinearRegression
import pandas as pd

from results_dashboard.sidebar import show_sidebar


st.set_page_config(
    page_title="Linearity",
    page_icon="https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png",
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
    st.stop()

############### By Sensor ###############

try:
    df = data.linearity(zeroed)
except KeyError:
    traceback.print_exc()
    st.warning("Zeroing error. Showing unzeroed values")
    df = data.linearity(False)

if linear_range > 0:
    df = df[(df.index.get_level_values("angle") <= linear_range) & (df.index.get_level_values("angle") >= -linear_range)]

# create lindf now so we have all sensor data in it
# this way it will be available for the sensor group
# section even if the sensor itself has a filter
lindf = pd.DataFrame(index=df.index)
for sensor in df.index.get_level_values("sensor_name").unique():
    mask = df.index.get_level_values("sensor_name") == sensor
    x = df.loc[mask, "mean_raw"].to_frame()
    y = df.loc[mask].index.to_frame()["angle"]
    reg = LinearRegression().fit(x, y)
    lindf.loc[mask, "mean_residual"] = reg.predict(df.loc[mask, ["mean_raw"]]) - df.loc[mask].index.to_frame()["angle"]
    lindf.loc[mask, "max_residual"] = reg.predict(df.loc[mask, ["max_raw"]].rename(columns={"max_raw": "mean_raw"})) - df.loc[mask].index.to_frame()["angle"]
    lindf.loc[mask, "min_residual"] = reg.predict(df.loc[mask, ["min_raw"]].rename(columns={"min_raw": "mean_raw"})) - df.loc[mask].index.to_frame()["angle"]

sensors = st.selectbox("Select a sensor", ["All"] + data.sensor_names, key="linearity_sensor")
if sensors != "All":
    df = df.xs(sensors, level="sensor_name")
    df["sensor_name"] = sensors
    df = df.reset_index().set_index(["sensor_name", "angle"])

avg_chart = (
    alt.Chart(df.reset_index())
    .mark_line()
    .encode(
        x=alt.X("angle", title="Angle (deg)"),
        y=alt.Y("mean_raw", title="Raw Output", scale=alt.Scale(zero=False)),
        color=alt.Color("sensor_name", title="Sensor"),
    )
)
area_chart = (
    alt.Chart(df.reset_index())
    .mark_area(opacity=0.3)
    .encode(
        alt.X("angle", title="Angle (deg)"),
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
    x = df.index.to_frame()[["angle"]]
    y = np.array(df["mean_raw"]).reshape(-1, 1)
    reg = LinearRegression().fit(x, y)
    r2 = reg.score(x, y)

    linregr_df = pd.DataFrame({"angle": [df.index.get_level_values("angle").min(), df.index.get_level_values("angle").max()]})
    linregr_df["mean_raw"] = reg.predict(linregr_df[["angle"]])

    # calculate linear line of best fit
    avg_chart += (
        alt.Chart(linregr_df)
        .mark_line(strokeDash=[5, 5], color="red")
        .encode(
            alt.X("angle", title="Angle (deg)"),
            alt.Y("mean_raw", title="Regression"),
            alt.Color(legend=None)
        )
    )

    title += f" | R-squared: {r2:.5f}"

chart = (area_chart + avg_chart).properties(title=title)


st.altair_chart(chart.interactive(), use_container_width=True)

st.write("#### Residual Values")
st.write("""
    This graph shows the error for each sensor from the linear best
    fit line.
""")

if sensors != "All":
    snlindf = lindf.xs(sensors, level="sensor_name", drop_level=False)
else:
    snlindf = lindf

avg_chart = (
    alt.Chart(snlindf.reset_index())
    .mark_line() 
    .encode(
        x=alt.X("angle", title="Angle (deg)"),
        y=alt.Y("mean_residual", title="Residual"),
        color=alt.Color("sensor_name", title="Sensor"),
    )
) 
area_chart = (
    alt.Chart(snlindf.reset_index())
    .mark_area(opacity=0.3)
    .encode(
        alt.X("angle", title="Angle (deg)"),
        alt.Y("max_residual", title="Residual"),
        alt.Y2("min_residual"),
        color=alt.Color("sensor_name", title="Sensor"),
        tooltip=[
            alt.Tooltip("sensor_name", title="Sensor"),
            alt.Tooltip("angle", title="Angle (deg)"),
            alt.Tooltip("mean_residual", title="Residual"),
            alt.Tooltip("max_residual", title="Max Residual"),
            alt.Tooltip("min_residual", title="Min Residual"),
        ],
    )
)

# create a horizontal line at 0
zero_line = (
    alt.Chart(pd.DataFrame({"Spec": [0]})).mark_rule().encode(y="Spec")
)


chart = (zero_line + area_chart + avg_chart).properties(title="Residual Values")

st.altair_chart(chart.interactive(), use_container_width=True)




############### By Group ###############
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
    traceback.print_exc()
    st.warning("Zeroing error. Showing unzeroed values")
    df = data.linearity(False, series=True)

if linear_range > 0:
    df = df[(df.index.get_level_values("angle") <= linear_range) & (df.index.get_level_values("angle") >= -linear_range)]

if groups != "All":
    df = df.xs(groups, level="series", drop_level=False)

chart = (
    alt.Chart(df.reset_index())
    .mark_line()
    .encode(
        x=alt.X("angle", title="Angle (deg)"),
        y=alt.Y("mean_raw", title="Raw Output", scale=alt.Scale(zero=False)),
        color=alt.Color("series", title="Sensor Group"),
    )
)

title = "Linearity"
if linear_range > 0:
    title += f" (+/-{linear_range} deg)"

if groups != "All":
    x = np.array(df.index.to_frame()["angle"]).reshape(-1, 1)
    y = np.array(df["mean_raw"]).reshape(-1, 1)
    reg = LinearRegression().fit(x, y)
    r2 = reg.score(x, y)

    # calculate linear line of best fit
    chart += (
            chart
            .transform_regression("angle", "mean_raw", method="linear")
            .mark_line(strokeDash=[5, 5], color="red")
            .encode(
                alt.Color(legend=None)
            )
        )
    title += f" | R-squared: {r2:.5f}"

chart += (
    alt.Chart(df.reset_index())
    .mark_area(opacity=0.3)
    .encode(
        alt.X("angle", title="Angle (deg)"),
        alt.Y("max_raw", title="Raw Output"),
        alt.Y2("min_raw"),
        color=alt.Color("series", title="Sensor Group"),
        tooltip=[
            alt.Tooltip("series", title="Sensor Group"),
            alt.Tooltip("angle", title="Angle (deg)"),
            alt.Tooltip("mean_raw", title="Raw Output"),
            alt.Tooltip("max_raw", title="Max Raw Output"),
            alt.Tooltip("min_raw", title="Min Raw Output"),
        ],
    )
)

chart = chart.properties(title=title)


st.altair_chart(chart.interactive(), use_container_width=True)

st.write("#### Residual Values")
st.write("""
    This graph shows the error for each sensor from the linear best
    fit line.
""")

lindf["series"] = lindf.index.get_level_values("sensor_name").map(data.series_mapping)
group_by = lindf.reset_index().groupby(["angle", "series"])
lindf = group_by["mean_residual"].mean().to_frame()
lindf["max_residual"] = group_by["max_residual"].max()
lindf["min_residual"] = group_by["min_residual"].min()

if groups != "All":
    gplindf = lindf.xs(groups, level="series", drop_level=False)
else:
    gplindf = lindf

avg_chart = (
    alt.Chart(gplindf.reset_index())
    .mark_line()
    .encode(
        x=alt.X("angle", title="Angle (deg)"),
        y=alt.Y("mean_residual", title="Residual"),
        color=alt.Color("series", title="Sensor Group"),
    )
) 
area_chart = (
    alt.Chart(gplindf.reset_index())
    .mark_area(opacity=0.3)
    .encode(
        alt.X("angle", title="Angle (deg)"),
        alt.Y("max_residual", title="Residual"),
        alt.Y2("min_residual"),
        color=alt.Color("series", title="Sensor Group"),
        tooltip=[
            alt.Tooltip("series", title="Sensor Group"),
            alt.Tooltip("angle", title="Angle (deg)"),
            alt.Tooltip("mean_residual", title="Residual"),
            alt.Tooltip("max_residual", title="Max Residual"),
            alt.Tooltip("min_residual", title="Min Residual"),
        ],
    )
)

# create a horizontal line at 0
zero_line = (
    alt.Chart(pd.DataFrame({"Spec": [0]})).mark_rule().encode(y="Spec")
)


chart = (zero_line + area_chart + avg_chart).properties(title="Residual Values")

st.altair_chart(chart.interactive(), use_container_width=True)
