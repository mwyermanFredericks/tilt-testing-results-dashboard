import streamlit as st  # type: ignore

from results_dashboard.ui import samples, test_select

# Sidebar/Multipage

st.set_page_config(page_title="Raw Data")
st.sidebar.title("Report Settings")

selected_ids = test_select.get_test_selection_sidebar()
data = samples.show_samples_sidebar(selected_ids)

# Main Page
st.write("# Raw Data")


@st.cache
def convert_samples_df(df):
    return df.to_csv().encode("utf-8")


@st.cache
def convert_rep_df(df):
    return df.to_csv().encode("utf-8")


st.write("## Samples")
if data.empty:
    st.warning("No data available for selected tests")
else:
    st.write(data.samples)
    csv = convert_samples_df(data.samples)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="samples.csv",
        mime="text/csv",
    )

st.write("## Repeatability")
if data.empty:
    st.warning("No data available for selected tests")
else:
    st.write(data.repeatability)
    csv = convert_rep_df(data.repeatability)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="repeatability.csv",
        mime="text/csv",
    )
