import streamlit as st

from ...graphs.repeatability import (by_sensor,
                                                                 by_series)


def display_graphs(data) -> None:
    st.header("Repeatability")
    st.write(
        "Sensor repeatability is calculated at each angle by taking"
        "the maximum sensor output minus the minumum sensor output."
    )
    st.write(
        "Repeatability is calculated using set angle rather than the stage's"
        "reported angle. This will not compensate for small differences in the real "
        "angle that the stage goes to, but it guarantees the maximum "
        "number of samples is used at each point. As the tilt stage has "
        "a repeatability significantly higher than any of our sensors, "
        "this is usually gives the most accurate  measure of sensor "
        "repeatability."
    )
    st.write(
        "Note that the graphs in this section use a logarithmic scale on the Y axis."
    )
    expected_repeatability = st.number_input("Expected Repeatability")
    zeroed = st.checkbox("Use zeroed set angles")
    by_sensor.display_graph(data, expected_repeatability, zeroed)
    by_series.display_graph(data, expected_repeatability, zeroed)
