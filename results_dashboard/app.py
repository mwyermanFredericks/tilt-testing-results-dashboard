import streamlit as st

from .data import SensorData
from .data.mongo import tests_db
from .graphs import accuracy, over_time, repeatability
from .ui import samples, test_select


def run():
    st.set_page_config(
        page_title="Tilt Testing Results Dashboard",
        page_icon=":wave:",
    )

    st.write("# Welcome to the Tilt Testing Results Dashboard")
    st.sidebar.success("Select a page above to get started")
    st.write("## About")
    st.write(
        """
        This dashboard is designed to help you visualize the results of your Tilt
        Testing. It is linked to our MongoDB instance, so test results are
        automatically updated as they are added to the database.
        """
    )

    # selected_ids = test_select.display_test_section()
    #
    # data = samples.show_samples(selected_ids)
    #
    # st.header("Data Views")
    # st.write("Select a data view to see the data in a different format:")
    # views = {
    #     "Data over Time": over_time.display_graphs,
    #     "Accuracy": accuracy.display_graphs,
    #     "Repeatability": repeatability.display_graphs,
    # }
    #
    # try:
    #     selected_index = int(selected_index)
    # except (TypeError, ValueError):
    #     selected_index = None
    #
    # cols = st.columns(len(views))
    # for i, (name, view) in enumerate(views.items()):
    #     with cols[i]:
    #         run = st.button(name)
    #         if run:
    #             selected_index = i
    #
    # if selected_index is not None:
    #     print(selected_index, type(selected_index))
    #     view = list(views.values())[selected_index]
    #     view(data)
