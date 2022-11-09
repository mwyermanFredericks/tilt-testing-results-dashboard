import streamlit as st

from . import by_sensor


def display_graphs(data) -> None:
    st.header("Accuracy")
    st.write(
        "Sensor accuracy is a test of how well the linearization algorithm "
        "performs. It is calculated by taking the difference between the "
        "sensor output and the set angle. The difference is then averaged "
        "over all samples at each angle."
    )
    st.write(
        "For bare sensors and unlinearized boards, this will be a measure "
        "of how well the test performed the linearization. For linearized "
        "boards, this will be a measure of how well the linearization "
        "algorithm of the sensor itself performed. For this reason, this"
        "test is normally only useful for linearized boards."
    )
    expeected_accuracy = st.number_input("Expected Accuracy")
    by_sensor.display_graph(data, expeected_accuracy)
