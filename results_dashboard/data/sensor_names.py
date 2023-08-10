from typing import Any

import pandas as pd
from dash import Dash, Input, Output, callback, dcc, html

from results_dashboard.cache_manager import CacheSingleton
from results_dashboard.common_components import log_callback_trigger
from results_dashboard.data.mongo import mongo_tilt_db
from results_dashboard.data.utils import get_match_query

cache = CacheSingleton()


def ininitialize(app: Dash) -> list[dcc.Store]:
    @app.callback(
        Output("sensor-names-data", "data"),
        Input("test-id", "data"),
        background=True,
        manager=cache.background_callback_manager,
    )
    @log_callback_trigger
    def get_sensor_names_data(test_id: str | None) -> list[dict[Any, Any]] | None:
        if test_id is None:
            return None

        db = mongo_tilt_db()
        test_ids = [test_id] if test_id else []
        query = db.query.find_one({"name": "sensor_names"})
        if query is None:
            return None
        stages = get_match_query(test_ids, None) + query["stages"]
        db_response = list(db.sample.aggregate(stages))
        data = pd.DataFrame(db_response)
        return data.to_dict("records")

    return [dcc.Store(id="sensor-names-data", storage_type="memory")]
