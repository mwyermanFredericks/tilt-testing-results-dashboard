from copy import deepcopy
from datetime import datetime

import pandas as pd
import streamlit as st  # type: ignore

from results_dashboard.data.mongo import tests_db
from results_dashboard.sidebar import show_sidebar

# Sidebar/Multipage

st.set_page_config(
    page_title="Test Info",
    page_icon="https://frederickscompany.com/wp-content/uploads/2017/08/F_logo_082017-e1502119400827.png",
)

data = show_sidebar()

# Main Page
st.write("# Test Info")

if data.empty:
    st.info("No test selected")
    st.stop()

info = data.test_info
# st.write(info)

tests = tests_db.get_tests(object_ids=data.test_ids)
selected_test_name = st.selectbox(
    "Select a test",
    options=tests["label"].tolist(),
)

test_id = tests[tests["label"] == selected_test_name]["_id"].iloc[0]
test_index = None
for i, test in enumerate(info):
    if str(test["_id"]) == test_id:
        test_index = i
        break

if test_index is None:
    st.warning("Test not found")
    st.stop()

new_info = deepcopy(info[test_index])

col1, col2 = st.columns(2)
col1.metric("Test Date", new_info["test_start_time"].strftime("%m/%d/%Y"))
col2.metric("Test Start Time", new_info["test_start_time"].strftime("%I:%M:%S %p"))
col1.metric("Test Progress", f"{new_info['test_progress']: .2%}")
col2.metric("Samples Taken", f"{new_info['rows_written']:,}")

with st.expander("Hardware Info"):
    st.metric("Hostname", new_info["test_info"]["hostname"])
    st.write("##### Oven")
    oven_info = {
        key: value
        for key, value in new_info["test_info"]["oven"].items()
        if key != "device_class" and type(value) != dict
    }
    if (
        "registers" in new_info["test_info"]["oven"]
        and "oven_name" in new_info["test_info"]["oven"]["registers"]
    ):
        oven_info["oven_name"] = new_info["test_info"]["oven"]["registers"]["oven_name"]
    oven_info_df = pd.DataFrame.from_dict(oven_info, orient="index", columns=["Value"])
    st.table(oven_info_df)

    st.write("##### Stage")
    stage_info = {
        key: value
        for key, value in new_info["test_info"]["stage"].items()
        if key != "device_class" and type(value) != dict
    }
    stage_info_df = pd.DataFrame.from_dict(
        stage_info, orient="index", columns=["Value"]
    )
    st.table(stage_info_df)

with st.form("test_info"):
    st.warning(
        "Pushing changes to the database is not yet implemented. Instead, the update button will display the updated json document."
    )

    new_info["name"] = st.text_input("Test Name", value=info[test_index]["name"])
    new_info["description"] = st.text_area(
        "Test Description", value=info[test_index]["description"]
    )

    st.write("##### Sensors")
    if "sensors" not in new_info["test_info"]:
        st.warning("Test does not contain sensor info")
    elif "signal_conditioners" not in new_info["test_info"]["sensors"]:
        st.warning(
            "Test does not support editing sensor info. Raw JSON data is available below."
        )
        with st.expander("Raw Sensor JSON"):
            st.write(new_info["test_info"]["sensors"])
    else:
        for i, sc in enumerate(new_info["test_info"]["sensors"]["signal_conditioners"]):
            with st.expander(
                f"{sc['name']} ({', '.join([s['name'] for s in sc['sensors']])})"
            ):
                st.write("###### Signal Conditioner Info")
                sc["name"] = st.text_input(
                    "Signal Conditioner Name",
                    value=sc["name"],
                    key=f"sc_name_{i}",
                )
                col1, col2 = st.columns(2)
                sc["part_number"] = col1.text_input(
                    "Signal Conditioner Part Number",
                    value=sc["part_number"],
                    key=f"sc_part_number_{i}",
                )
                sc["type"] = col2.text_input(
                    "Signal Conditioner Type",
                    value=sc["type"],
                    key=f"sc_type_{i}",
                )

                for j, sensor in enumerate(sc["sensors"]):
                    st.write(f"###### {sensor['axis']} Axis Info")
                    col1, col2 = st.columns(2)
                    sensor["name"] = col1.text_input(
                        "Sensor Name",
                        value=sensor["name"],
                        key=f"sensor_name_{i}_{j}",
                    )
                    sensor["part_number"] = col2.text_input(
                        "Sensor Part Number",
                        value=sensor["part_number"],
                        key=f"sensor_part_number_{i}_{j}",
                    )
                    sensor["description"] = st.text_area(
                        "Sensor Description",
                        value=""
                        if "description" not in sensor
                        else sensor["description"],
                        key=f"sensor_description_{i}_{j}",
                    )

    submitted = st.form_submit_button("Update")
    if submitted:
        st.write(new_info)
