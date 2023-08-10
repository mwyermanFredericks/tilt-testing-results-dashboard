import pandas as pd
from dash import Dash, Input, Output, dcc, html

from results_dashboard.cache_manager import CacheSingleton
from results_dashboard.common_components import log_callback_trigger
from results_dashboard.data.mongo import mongo_tilt_db
from results_dashboard.data.utils import get_match_query

cache = CacheSingleton()


def initialize(app: Dash) -> list[dcc.Store]:
    @app.callback(
        Output("angle-data", "data"),
        Input("test-id", "data"),
        background=True,
        manager=cache.background_callback_manager,
    )
    @log_callback_trigger
    def get_angle_data(
        test_id: str | None, sensor_mask: list[str] | None = None
    ) -> pd.DataFrame | None:
        if test_id is None:
            return None

        db = mongo_tilt_db()
        test_ids = [test_id] if test_id else []
        aggregate_query = [
            # get test data
            get_match_query(test_ids, sensor_mask),
            # group stage data by sample time
            {
                "$group": {
                    "_id": "$sample_time",
                    "stage_data": {"$first": "$stage_data"},
                }
            },
            # promote stage data to root
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$stage_data"]}}},
            # remove stage data
            {"$project": {"stage_data": 0}},
            # round set angle to 5 decimal places
            {"$set": {"set_angle": {"$round": ["$set_angle", 5]}}},
            # sort by sample time
            {"$sort": {"_id": 1}},
            # group by sample time
            {"$group": {"_id": 0, "document": {"$push": "$$ROOT"}}},
            # add previous angle field to each document
            {
                "$project": {
                    "documentAndPrevAngle": {
                        "$zip": {
                            "inputs": [
                                "$document",
                                {"$concatArrays": [[None], "$document.set_angle"]},
                            ]
                        }
                    }
                }
            },
            # unwind document and previous angle
            {"$unwind": {"path": "$documentAndPrevAngle"}},
            # replace document with document and previous angle
            {
                "$replaceWith": {
                    "$mergeObjects": [
                        {"$arrayElemAt": ["$documentAndPrevAngle", 0]},
                        {"prev_angle": {"$arrayElemAt": ["$documentAndPrevAngle", 1]}},
                    ]
                }
            },
            # get difference between set angle and previous angle
            {
                "$set": {
                    "angle_difference": {"$subtract": ["$set_angle", "$prev_angle"]}
                }
            },
            # filter out documents where angle difference is 0
            {"$match": {"angle_difference": {"$ne": 0}}},
            # remove previous angle and angle difference
            {"$project": {"prev_angle": 0, "angle_difference": 0}},
            # create sample time field
            {"$set": {"sample_time": "$_id"}},
        ]

        db_response = list(db.sample.aggregate(aggregate_query))
        data = pd.DataFrame(db_response)
        return data.to_dict("records")

    return [dcc.Store(id="angle-data", data=[])]
