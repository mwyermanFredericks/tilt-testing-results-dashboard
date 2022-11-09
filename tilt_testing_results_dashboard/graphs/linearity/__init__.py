import streamlit as st

from . import full_test_range, linear_range, operating_range


def display_graphs(data):
    st.header("Linearity")
    linear_range.display_graphs(data)
