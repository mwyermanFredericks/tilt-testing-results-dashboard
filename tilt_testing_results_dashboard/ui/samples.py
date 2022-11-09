import streamlit as st

from ..data import SensorData


@st.experimental_memo
def save_data(samples):
    return samples.to_csv(index=False).encode("utf-8")


def filter_sensors(data):
    hide = st.checkbox("Show All Sensors", value=True)
    if hide:
        return
    sensors = data.sensor_names
    selected = st.multiselect("Sensors", sensors, default=sensors)
    data.sensor_mask = selected


def show_samples(test_ids):
    st.header("Raw Data")

    data = SensorData(test_ids)

    filter_sensors(data)

    show = st.checkbox("Show Raw Data")
    if show:
        st.write(data.samples)

    csv = save_data(data.samples)
    st.download_button(
        label="Download Raw Data",
        data=csv,
        file_name="rawdata.csv",
        mime="text/csv",
        key="download_raw_data",
    )
    return data
