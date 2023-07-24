import pandas as pd
from dash import Dash, Input, Output, dcc, html

from results_dashboard.data.mongo import mongo_tilt_db
from results_dashboard.data.utils import get_match_query


def initialize(app: Dash) -> list[dcc.Store]:
    @app.callback(
        Output("sensor-repeatability-data", "data"),
        Input("test-id", "value"),
    )
    def get_sensor_repeatability_data(
        test_id: str | None, sensor_mask: list[str] | None = None
    ) -> pd.DataFrame | None:
        if test_id is None:
            return None
        db = mongo_tilt_db()
        test_ids = [test_id] if test_id else []
        aggregate_query = [
            # get test data
            get_match_query(test_ids, sensor_mask),
            # reduce to set angle, sensor degrees, and sensor name
            {
                "$project": {
                    "set_angle": {"$round": ["$stage_data.set_angle", 5]},
                    "measured": "$sensor_data.degrees",
                    "sensor_name": "$sensor_name",
                }
            },
            # group by set angle and sensor name
            {
                "$group": {
                    "_id": {"set_angle": "$set_angle", "sensor_name": "$sensor_name"},
                    "max_measured": {"$max": "$measured"},
                    "min_measured": {"$min": "$measured"},
                }
            },
            # calculate range
            {
                "$addFields": {
                    "range_measured": {"$subtract": ["$max_measured", "$min_measured"]}
                }
            },
            # calculate repeatability
            {"$addFields": {"repeatability": {"$divide": ["$range_measured", 2]}}},
            # convert ids to multiple fields
            {
                "$addFields": {
                    "set_angle": "$_id.set_angle",
                    "sensor_name": "$_id.sensor_name",
                }
            },
            # sort by set angle, then sensor name
            {"$sort": {"set_angle": 1, "sensor_name": 1}},
        ]

        db_response = list(db.sample.aggregate(aggregate_query))
        data = pd.DataFrame(db_response)
        return data.to_dict("records")

    return [dcc.Store(id="sensor-repeatability-data", data=[])]
