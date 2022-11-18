import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import numpy as np  # type: ignore

from results_dashboard.sidebar import show_sidebar
from results_dashboard.data.mongo import mongo_tilt_db

# Sidebar/Multipage

st.set_page_config(page_title="Raw Data")

data = show_sidebar()

# Main Page
st.write("# Raw Data")


def load_raw_data(data: pd.DataFrame) -> pd.DataFrame:
    """Get raw data from the database"""
    db = mongo_tilt_db()
    df = pd.DataFrame(list(db["sample"].aggregate([
        data._match_query, {
            "$project": {
                "_id": 0,
                "sensor_name": 1,
                "sample_time": 1,
                "set_angle": "$stage_data.set_angle",
                "stage_angle": "$stage_data.stage_angle",
                "oven_set_temperature": "$temperature_data.oven_set_temperature",
                "oven_integrated_temperature": "$temperature_data.oven_integrated_temperature",
                "thermocouple_temperature": "$temperature_data.thermocouple_temperature",
                "ambient_temperature": "$temperature_data.ambient_temperature",
                "raw": "$sensor_data.raw",
                "degrees": "$sensor_data.degrees",
                "pass_fail": "$sensor_data.pass_fail",
                "debug_info": "$sensor_data.debug_info",
            }
        }
    ])))
    
    df.set_index(["sample_time", "sensor_name"], inplace=True)
    df.index.names = ["sample_time", "sensor_name"]

    info_columns = [
        "set_angle",
        "stage_angle",
        "oven_set_temperature",
        "oven_integrated_temperature",
        "thermocouple_temperature",
        "ambient_temperature"
    ]
    info_df = df[df.index.get_level_values("sensor_name") == df.index[0][1]][info_columns]
    info_df.index = info_df.index.droplevel("sensor_name")
    data_df = df.loc[:, np.invert(np.array(df.columns.isin(info_columns)))].unstack("sensor_name")
    data_df.columns = [f"{mtype}-{sensor}" for mtype, sensor in data_df.columns]

    df = pd.concat(
        [
            info_df, data_df
        ],
        axis=1
    )
    return df


def convert_sample_df(df):
    return df.to_csv().encode("utf-8")


def convert_rep_df(df):
    return df.to_csv().encode("utf-8")


st.write("## Samples")
if data.empty:
    st.warning("No data available for selected tests")
else:
    df = load_raw_data(data)

    st.write(df)

    st.download_button(
        label="Download as CSV",
        data=convert_sample_df(df),
        file_name="samples.csv",
        mime="text/csv",
    )
#
st.write("## Repeatability")
if data.empty:
    st.warning("No data available for selected tests")
else:
    df = data.repeatability()

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
