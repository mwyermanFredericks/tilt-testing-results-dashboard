import streamlit as st

from ..data.mongo import tests_db


def show_test_list_generic(test_list, namespace) -> None:
    namespace.header("Test Selection")
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
    show = namespace.checkbox("Show Test List")
    if show:
        namespace.write(display_test_list)


def show_test_list() -> None:
    show_test_list_generic(test_list, st)


def show_test_list_sidebar() -> None:
    show_test_list_generic(test_list, st.sidebar)


def get_test_selection_generic(namespace) -> list[str]:
    test_list = tests_db.get_tests()
    selectable_test_names = {
        f"{i[0]}-{i[2].strftime('%m/%d/%Y-%H:%M:%S')}": i[1]
        for i in list(zip(test_list.name, test_list._id, test_list.test_start_time))
    }
    try:
        test_selection = namespace.multiselect(
            "Select Test(s)",
            list(selectable_test_names.keys()),
            default=st.session_state["test_selection"],
            key="test_selection",
        )
    except KeyError:
        test_selection = namespace.multiselect(
            "Select Test(s)",
            list(selectable_test_names.keys()),
            key="test_selection",
        )
    selected_ids = [selectable_test_names[i] for i in test_selection]
    return selected_ids


def get_test_selection() -> list[str]:
    return get_test_selection_generic(st)

def get_test_selection_sidebar() -> list[str]:
    return get_test_selection_generic(st.sidebar)


def display_test_section() -> list[str]:
    show_test_list()
    return get_test_selection()
