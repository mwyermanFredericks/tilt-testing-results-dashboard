import streamlit as st

from ..data.mongo import tests_db


def show_test_list() -> None:
    st.header("Test Selection")
    test_list = tests_db.get_tests()
    display_test_list = test_list.loc[
        :, ["test_start_time", "name", "rows_written", "description"]
    ]
    display_test_list.rename(
        columns={
            "test_start_time": "Start Time",
            "name": "Name",
            "rows_written": "Data Rows",
            "description": "Description",
        },
        inplace=True,
    )
    show = st.checkbox("Show Test List")
    if show:
        st.write(display_test_list)


def get_test_selection() -> list[str]:
    test_list = tests_db.get_tests()
    selectable_test_names = {
        f"{i[0]}-{i[2].strftime('%m/%d/%Y-%H:%M:%S')}": i[1]
        for i in list(zip(test_list.name, test_list._id, test_list.test_start_time))
    }
    state = st.experimental_get_query_params()
    selected_tests = st.multiselect(
        "Select Test(s)",
        list(selectable_test_names.keys()),
        default=state.get("tests", []),
    )
    state["tests"] = selected_tests
    st.experimental_set_query_params(**state)
    selected_ids = [selectable_test_names[i] for i in selected_tests]
    return selected_ids


def display_test_section() -> list[str]:
    show_test_list()
    return get_test_selection()
