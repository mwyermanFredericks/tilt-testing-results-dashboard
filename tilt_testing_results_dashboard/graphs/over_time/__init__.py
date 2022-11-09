import streamlit as st

from . import stage_angle, temperature

show_section = True


def display_graphs(data):
    st.header("Data over Time")
    st.write(
        "These graphs show various metrics over time during a test."
        " This gives a basic overview of the test process and can"
        " highlight any major performance issues."
    )

    stage_angle.display_graph(data)
    temperature.display_graph(data)
