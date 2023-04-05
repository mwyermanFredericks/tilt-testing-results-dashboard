import pandas as pd
import streamlit as st
from bson import ObjectId

from . import mongo_tilt_db


def get_tests(series=None, object_ids=None):
    db = mongo_tilt_db()
    aggregate_query = [
        {"$sort": {"test_start_time": -1}},
        {
            "$project": {
                "label": {
                    "$concat": [
                        "$name",
                        "-",
                        {
                            "$dateToString": {
                                "date": "$test_start_time",
                                "format": "%m/%d/%Y-%H:%M:%S",
                            }
                        },
                    ]
                },
                "progress": {
                    "$divide": ["$status.steps_completed", "$status.total_steps"]
                },
                "rows_written": "$rows_written",
            }
        },
    ]
    if object_ids is not None:
        search_ids = []
        for test_id in object_ids:
            if isinstance(test_id, str):
                search_ids.append(ObjectId(test_id))
            else:
                search_ids.append(test_id)
        aggregate_query.insert(0, {"$match": {"_id": {"$in": search_ids}}})
    test_df = pd.DataFrame(list(db["test"].aggregate(aggregate_query)))
    test_df["_id"] = test_df["_id"].astype(str)
    return test_df


def update_test_info(test_id, new_info):
    db = mongo_tilt_db()
    db["test"].update_one({"_id": test_id}, {"$set": {"test_info": new_info}})


def get_test_info(test_ids):
    db = mongo_tilt_db()

    if isinstance(test_ids, str) or isinstance(test_ids, ObjectId):
        test_ids = [test_ids]

    search_ids = []
    for test_id in test_ids:
        if isinstance(test_id, str):
            search_ids.append(ObjectId(test_id))
        else:
            search_ids.append(test_id)

    cursor = db["test"].aggregate(
        [{"$match": {"_id": {"$in": search_ids}}}, {"$unset": "test_info.steps"}]
    )
    results = list(cursor)

    return results


if __name__ == "__main__":
    print(get_tests())
