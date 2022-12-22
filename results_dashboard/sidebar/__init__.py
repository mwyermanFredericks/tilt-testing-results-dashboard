import streamlit as st
from streamlit_extras.app_logo import add_logo

from results_dashboard.data import SensorData

from . import samples, test_select


def show_sidebar() -> SensorData:
    add_logo(
        "https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png"
    )
    st.sidebar.write("### General Options")
    selected_ids = test_select.get_test_selection_sidebar()
    data = samples.show_samples_sidebar(selected_ids)
    return data
