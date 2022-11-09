import altair as alt
import pandas as pd
import streamlit as st
from scipy.stats import linregress


def prepare_sensor_data(df):
    lin_df = df.groupby(["set_angle", "sensor_name"]).mean()
    lin_df = lin_df.rename_axis(["set_angle", "sensor_name"]).reset_index()
    lin_df = lin_df.rename(
        columns={
            "stage_angle": "Stage Angle",
            "zeroed_stage_angle": "Stage Angle (Zeroed)",
            "raw": "Raw Output",
            "zeroed_raw": "Raw Output (Zeroed)",
            "sensor_name": "Sensor Name",
        }
    )

    return lin_df


def prepare_series_data(df):
    lin_series_df = df.groupby(["set_angle", "series"]).mean()
    lin_series_df = lin_series_df.rename_axis(["set_angle", "series"]).reset_index()
    lin_series_df = lin_series_df.rename(
        columns={
            "stage_angle": "Stage Angle",
            "zeroed_stage_angle": "Stage Angle (Zeroed)",
            "raw": "Raw Output",
            "zeroed_raw": "Raw Output (Zeroed)",
            "series": "Series",
        }
    )


def generate_graph(data, expected_linear_range: float, sensor_to_graph: str = None):
    # df = prepare_sensor_data(df)
    df = data.samples

    df = df.loc[
        df["zeroed_set_angle"].between(-expected_linear_range, +expected_linear_range)
    ]

    if sensor_to_graph is not None:
        df = df.loc[df["Sensor Name"] == sensor_to_graph]
        chart = (
            alt.Chart(df)
            .mark_circle(size=40)
            .encode(
                alt.X("Stage Angle (Zeroed)"),
                alt.Y("Raw Output"),
                tooltip=["Sensor Name", "Stage Angle (Zeroed)", "Raw Output"],
            )
            .properties(
                title=f"Linear Range of {sensor_to_graph}",
            )
        )
        chart += chart.transform_regression(
            "Stage Angle (Zeroed)", "Raw Output"
        ).mark_line(opacity=0.2)
        x, y = "Stage Angle (Zeroed)", "Raw Output"
        r_squared = linregress(df[x], df[y]).rvalue ** 2
        # print(r_squared)
    else:
        selection = alt.selection_multi(fields=["Sensor Name"], bind="legend")

        chart = (
            alt.Chart(df)
            .mark_circle(size=40)
            .encode(
                alt.X("Stage Angle (Zeroed)"),
                alt.Y("Raw Output"),
                tooltip=["Sensor Name", "Stage Angle (Zeroed)", "Raw Output"],
                color=alt.Color(
                    field="Sensor Name",
                    legend=alt.Legend(
                        orient="none",
                        direction="horizontal",
                        columns=8,
                        legendX=15,
                        legendY=470,
                        title="",
                    ),
                ),
                opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            )
            .add_selection(selection)
        )

    return chart.interactive()


def display_graph(df, expected_linear_range: float):
    chart = generate_graph(df, expected_linear_range)
    st.subheader("Linear Range by Sensor")
    st.altair_chart(chart, use_container_width=True)
