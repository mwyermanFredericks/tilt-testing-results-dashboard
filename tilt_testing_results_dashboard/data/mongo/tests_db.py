import pandas as pd
import streamlit as st

from . import mongo_tilt_db


@st.cache(ttl=60)
def get_tests(series=None):
    db = mongo_tilt_db()
    filter = {}
    if series is not None:
        filter = {"test_series": series}
    sort = list({"test_start_time": -1}.items())
    test_df = pd.DataFrame(list(db["test"].find(filter=filter, sort=sort)))

    test_df["_id"] = test_df["_id"].astype(str)

    return test_df


@st.cache(ttl=60)
def get_test_info(test_id):
    db = mongo_tilt_db()
    test = db["test"].find_one(
        {"_id": test_id},
    )

    return test


if __name__ == "__main__":
    print(get_tests())
