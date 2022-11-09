import streamlit as st

from ..data import SensorData


def show_samples_generic(test_ids, namespace):
    data = SensorData(test_ids)

    try:
        show_all_sensors = namespace.checkbox("Show All Sensors", value=st.session_state["show_all_sensors"], key="show_all_sensors")
    except KeyError:
        show_all_sensors = namespace.checkbox("Show All Sensors", value=True, key="show_all_sensors")

    if show_all_sensors:
        return data

    sensors = data.sensor_names
    try:
        sensor_mask = namespace.multiselect("Sensors", sensors, default=st.session_state["sensor_mask"], key="sensor_mask")
    except KeyError:
        sensor_mask = namespace.multiselect("Sensors", sensors, default=sensors, key="sensor_mask")
    data.sensor_mask = sensor_mask
    return data


def show_samples(test_ids):
    return show_samples_generic(test_ids, st)


def show_samples_sidebar(test_ids):
    return show_samples_generic(test_ids, st.sidebar)
