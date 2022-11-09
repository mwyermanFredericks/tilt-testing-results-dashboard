import streamlit as st

from .data import SensorData
from .data.mongo import tests_db
from .graphs import accuracy, over_time, repeatability
from .ui import samples, test_select

def run():
    st.title("Tilt Testing Results Dashboard")

    selected_ids = test_select.display_test_section()

    data = samples.show_samples(selected_ids)

    st.header("Data Views")
    st.write("Select a data view to see the data in a different format:")
    views = {
        "Data over Time": over_time.display_graphs,
        "Accuracy": accuracy.display_graphs,
        "Repeatability": repeatability.display_graphs,
    }

    state = st.experimental_get_query_params()
    selected_index = state.get("view", [None])[0]

    try:
        selected_index = int(selected_index)
    except (TypeError, ValueError):
        selected_index = None

    cols = st.columns(len(views))
    for i, (name, view) in enumerate(views.items()):
        with cols[i]:
            run = st.button(name)
            if run:
                selected_index = i

    if selected_index is not None:
        print(selected_index, type(selected_index))
        view = list(views.values())[selected_index]
        view(data)

    state["view"] = selected_index
    st.experimental_set_query_params(**state)
