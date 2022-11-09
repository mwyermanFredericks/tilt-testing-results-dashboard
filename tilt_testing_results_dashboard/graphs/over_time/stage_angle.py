import altair as alt
import streamlit as st


def get_set_angle_over_time(data):
    df = data.downsampled[["sample_time", "set_angle", "stage_angle"]]

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            alt.X("sample_time", title="Time"),
            alt.Y("set_angle", title="Angle (° tilt)"),
            tooltip=[
                alt.Tooltip("sample_time", title="Time"),
                alt.Tooltip("set_angle", title="Angle"),
                alt.Tooltip("stage_angle", title="Reported Stage Angle"),
            ],
        )
        .properties(height=500, width=700, title="Set Angle vs Time")
    )
    return chart.interactive()


def display_graph(df):
    st.subheader("Set Angle vs Time")
    st.altair_chart(get_set_angle_over_time(df), use_container_width=True)
