import streamlit as st

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
