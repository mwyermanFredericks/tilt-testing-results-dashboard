import streamlit as st
from streamlit_extras.app_logo import add_logo

st.set_page_config(
    page_title="Tilt Testing Results Dashboard",
    page_icon="https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png",
)

add_logo(
    "https://frederickscompany.com/wp-content/uploads/2022/12/tfc-logo-round-edge.png"
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
