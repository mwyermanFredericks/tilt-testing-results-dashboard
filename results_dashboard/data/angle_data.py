import pandas as pd
from dash import Dash, Input, Output, dcc, html

from results_dashboard.data.mongo import mongo_tilt_db
from results_dashboard.data.utils import get_match_query


def get_div(app: Dash) -> html.Div:
    @app.callback(
        Output("angle-data", "data"),
        Input("test-ids", "value"),
    )
    def get_angle_data(
        test_ids: list[str] | None, sensor_mask: list[str] | None = None
    ) -> pd.DataFrame:
        print(test_ids)
        db = mongo_tilt_db()
        aggregate_query = [
            get_match_query(test_ids or [], sensor_mask),
            {
                "$group": {
                    "_id": "$sample_time",
                    "stage_data": {"$first": "$stage_data"},
                }
            },
            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$stage_data"]}}},
            {"$project": {"stage_data": 0}},
            {"$sort": {"_id": 1}},
            {"$group": {"_id": 0, "document": {"$push": "$$ROOT"}}},
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
            {"$unwind": {"path": "$documentAndPrevAngle"}},
            {
                "$replaceWith": {
                    "$mergeObjects": [
                        {"$arrayElemAt": ["$documentAndPrevAngle", 0]},
                        {"prev_angle": {"$arrayElemAt": ["$documentAndPrevAngle", 1]}},
                    ]
                }
            },
            {
                "$set": {
                    "angle_difference": {"$subtract": ["$set_angle", "$prev_angle"]}
                }
            },
            {"$match": {"angle_difference": {"$ne": 0}}},
            {"$project": {"prev_angle": 0, "angle_difference": 0}},
            {"$set": {"sample_time": "$_id"}},
        ]

        print(aggregate_query)
        db_response = list(db.sample.aggregate(aggregate_query))
        print(len(db_response))
        data = pd.DataFrame(db_response)
        print(data)
        return data.to_dict("records")

    return html.Div([dcc.Store("angle-data")])
