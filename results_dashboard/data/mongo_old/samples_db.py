import pandas as pd
import streamlit as st
from bson import ObjectId

from . import mongo_tilt_db


@st.cache(ttl=60 * 15)
def get_samples(test_ids):
    db = mongo_tilt_db()

    if isinstance(test_ids, str):
        test_ids = [test_ids]

    sample_df = pd.DataFrame(
        list(
            db["sample"].find(
                {"test_id": {"$in": [ObjectId(id) for id in test_ids]}},
                {
                    "_id": 0,
                    "sample_time": 1,
                    "sensor_name": 1,
                    "set_angle": "$stage_data.set_angle",
                    "stage_angle": "$stage_data.stage_angle",
                    "raw": "$sensor_data.raw",
                    "degrees": "$sensor_data.degrees",
                    "oven_set_temperature": "$temperature_data.oven_set_temperature",
                    "oven_integrated_temperature": "$temperature_data.oven_integrated_temperature",
                    "thermocouple_temperature": "$temperature_data.thermocouple_temperature",
                    "ambient_temperature": "$temperature_data.ambient_temperature",
                },
            )
        )
    )

    # sample_df["_id"] = sample_df["_id"].astype(str)

    return sample_df
