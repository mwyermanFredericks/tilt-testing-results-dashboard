from typing import Literal

import streamlit as st

from ..data.mongo import tests_db


def show_test_list_generic(
    test_list,
    namespace,
) -> None:
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
    test_list = test_list.loc[test_list["rows_written"] > 0, :]
    try:
        test_selection = namespace.multiselect(
            "Select Test(s)",
            list(test_list["label"]),
            default=st.session_state["test_selection"],
            key="test_selection",
        )
    except KeyError:
        test_selection = namespace.multiselect(
            "Select Test(s)",
            list(test_list["label"]),
            key="test_selection",
        )
    selected_ids = test_list.loc[
        test_list["label"].isin(test_selection), "_id"
    ].tolist()
    return selected_ids


def get_test_selection() -> list[str]:
    return get_test_selection_generic(st)


def get_test_selection_sidebar() -> list[str]:
    return get_test_selection_generic(st.sidebar)


def display_test_section() -> list[str]:
    show_test_list()
    return get_test_selection()
