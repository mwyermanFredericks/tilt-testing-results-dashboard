import streamlit as st

from . import by_sensor, by_series


def display_graphs(data) -> None:
    st.header("Linear Range")
    show = st.checkbox("Show Linear Range Graphs")
    if show:
        linear_range = st.number_input("Lienar Range of Sensor")
        zeroed = st.checkbox("Use zeroed set angles")
        by_sensor.display_graph(data, linear_range, zeroed)
        by_series.display_graph(data, linear_range, zeroed)
