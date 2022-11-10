import streamlit as st

from . import samples, test_select
from results_dashboard.data import SensorData


def show_sidebar() -> SensorData:
    st.sidebar.write("### General Options")
    selected_ids = test_select.get_test_selection_sidebar()
    data = samples.show_samples_sidebar(selected_ids)
    return data


