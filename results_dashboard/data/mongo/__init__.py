import streamlit as st
from pymongo import MongoClient

username = st.secrets["mongo_username"]
password = st.secrets["mongo_password"]


def mongo_tilt_db():
    client = MongoClient(
        f"mongodb+srv://{username}:{password}@frederickscluster.tyiku.mongodb.net/?retryWrites=true&w=majority"
    )
    db = client.tilt_test
    return db
