import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore

from results_dashboard.sidebar import show_sidebar

# Sidebar/Multipage

st.set_page_config(page_title="Raw Data")

data = show_sidebar()

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
    df = data.samples.copy()
    
    df.set_index(["sample_time", "sensor_name"], inplace=True)
    df.index.names = ["sample_time", "sensor_name"]

    info_columns = [
            "set_angle",
            "stage_angle",
            "stage_error",
            "oven_set_temperature",
            "oven_integrated_temperature",
            "thermocouple_temperature",
            "ambient_temperature"
            ]
    exclude_columns = ["series"]
    info_df = df[df.index.get_level_values("sensor_name") == df.index[0][1]][info_columns]
    info_df.index = info_df.index.droplevel("sensor_name")
    data_df = df.loc[:, np.invert(np.array(df.columns.isin(info_columns + exclude_columns)))].unstack("sensor_name")
    data_df.columns = [f"{mtype}-{sensor}" for mtype, sensor in data_df.columns]

    df = pd.concat(
        [
            info_df, data_df
        ],
        axis=1
    )

    st.write(df)
    csv = convert_samples_df(df)
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
    df = data.repeatability.copy()

    df.set_index(["angle", "sensor_name"], inplace=True)
    df.index.names = ["angle", "sensor_name"]
    df = df["repeatability"].unstack("sensor_name")

    st.write(df)
    csv = convert_rep_df(df)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="repeatability.csv",
        mime="text/csv",
    )
