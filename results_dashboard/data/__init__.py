from typing import List

import numpy as np
import pandas as pd
import streamlit as st
from bson import ObjectId

from .mongo import mongo_tilt_db
from .mongo.tests_db import get_test_info


def round_column(df: pd.DataFrame, column: str, round_to: List[float]) -> pd.Series:
    """Round a column of a datafram to the nearest value in a series."""

    def round_to_nearest(value: float, values: list) -> float:
        series = pd.Series(values, dtype=float)
        exact = series.loc[series == value]
        if not exact.empty:
            return value
        rvalue = round(float(value), 6)
        lo = float(series.loc[series < value].max())
        hi = float(series.loc[series > value].min())
        lodiff = round(rvalue - lo, 6)
        hidiff = round(hi - rvalue, 6)

        if hidiff <= lodiff:
            ret = hi
        else:
            ret = lo

        if pd.isna(ret):
            print(
                f"Error: value {value} resulted in NaN - lo: {lo} [{lodiff}], hi: {hi} [{hidiff}]"
            )

        return ret

    # extend list to prevent nan's when out of range
    round_to_lo = [x + (min(round_to) * 2) for x in round_to]
    round_to_hi = [x + (max(round_to) * 2) for x in round_to]
    round_to = round_to_lo[:-1] + round_to + round_to_hi[1:]

    df[column] = df[column].map(lambda x: round_to_nearest(x, round_to))


class SensorData:
    def __init__(self, test_ids: str | list[str]) -> None:
        self._test_ids = test_ids if isinstance(test_ids, list) else [test_ids]
        self._sensor_mask: list[str] | None = None

    @property
    def test_ids(self) -> list[str]:
        if isinstance(self._test_ids, str):
            return [self._test_ids]
        return self._test_ids

    @test_ids.setter
    def test_ids(self, test_ids: str | list[str]) -> None:
        self._test_ids = test_ids if isinstance(test_ids, list) else [test_ids]

    @property
    def sensor_mask(self) -> list[str] | None:
        return self._sensor_mask

    @sensor_mask.setter
    def sensor_mask(self, sensor_mask: list[str] | None) -> None:
        self._sensor_mask = sensor_mask

    @property
    def _match_query(self) -> dict:
        query_ids = [ObjectId(test_id) for test_id in self.test_ids]
        query = {"$match": {"test_id": {"$in": query_ids}}}

        if self.sensor_mask:
            query["$match"]["sensor_name"] = {"$in": self.sensor_mask}

        return query

    @property
    @st.cache_data(ttl=60)
    def angle_data(_self) -> pd.DataFrame:
        db = mongo_tilt_db()
        aggregate_query = [
            _self._match_query,
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

        df = pd.DataFrame(list(db["sample"].aggregate(aggregate_query)))

        return df

    @property
    @st.cache_data(ttl=60)
    def temperature_data(_self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            _self._match_query,
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$sample_time"},
                        "month": {"$month": "$sample_time"},
                        "day": {"$dayOfMonth": "$sample_time"},
                        "hour": {"$hour": "$sample_time"},
                        "minute": {"$minute": "$sample_time"},
                    },
                    "oven_set_temperature_max": {
                        "$max": "$temperature_data.oven_set_temperature"
                    },
                    "oven_set_temperature_min": {
                        "$min": "$temperature_data.oven_set_temperature"
                    },
                    "oven_set_temperature_mean": {
                        "$avg": "$temperature_data.oven_set_temperature"
                    },
                    "oven_set_temperature_dev": {
                        "$stdDevSamp": "$temperature_data.oven_set_temperature"
                    },
                    "oven_integrated_temperature_max": {
                        "$max": "$temperature_data.oven_integrated_temperature"
                    },
                    "oven_integrated_temperature_min": {
                        "$min": "$temperature_data.oven_integrated_temperature"
                    },
                    "oven_integrated_temperature_mean": {
                        "$avg": "$temperature_data.oven_integrated_temperature"
                    },
                    "oven_integrated_temperature_dev": {
                        "$stdDevSamp": "$temperature_data.oven_integrated_temperature"
                    },
                    "thermocouple_temperature_max": {
                        "$max": "$temperature_data.thermocouple_temperature"
                    },
                    "thermocouple_temperature_min": {
                        "$min": "$temperature_data.thermocouple_temperature"
                    },
                    "thermocouple_temperature_mean": {
                        "$avg": "$temperature_data.thermocouple_temperature"
                    },
                    "thermocouple_temperature_dev": {
                        "$stdDevSamp": "$temperature_data.thermocouple_temperature"
                    },
                    "ambient_temperature_max": {
                        "$max": "$temperature_data.ambient_temperature"
                    },
                    "ambient_temperature_min": {
                        "$min": "$temperature_data.ambient_temperature"
                    },
                    "ambient_temperature_mean": {
                        "$avg": "$temperature_data.ambient_temperature"
                    },
                    "ambient_temperature_dev": {
                        "$stdDevSamp": "$temperature_data.ambient_temperature"
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "sample_time": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day",
                            "hour": "$_id.hour",
                            "minute": "$_id.minute",
                        }
                    },
                    "oven_integrated_temperature": {
                        "source": "integrated",
                        "mean": "$oven_integrated_temperature_mean",
                        "max": "$oven_integrated_temperature_max",
                        "min": "$oven_integrated_temperature_min",
                        "dev": "$oven_integrated_temperature_dev",
                    },
                    "oven_set_temperature": {
                        "source": "setpoint",
                        "mean": "$oven_set_temperature_mean",
                        "max": "$oven_set_temperature_max",
                        "min": "$oven_set_temperature_min",
                        "dev": "$oven_set_temperature_dev",
                    },
                    "thermocouple_temperature": {
                        "source": "thermocouple",
                        "mean": "$thermocouple_temperature_mean",
                        "max": "$thermocouple_temperature_max",
                        "min": "$thermocouple_temperature_min",
                        "dev": "$thermocouple_temperature_dev",
                    },
                    "ambient_temperature": {
                        "source": "ambient",
                        "mean": "$ambient_temperature_mean",
                        "max": "$ambient_temperature_max",
                        "min": "$ambient_temperature_min",
                        "dev": "$ambient_temperature_dev",
                    },
                }
            },
            {
                "$project": {
                    "sample_time": 1,
                    "docs": [
                        "$oven_integrated_temperature",
                        "$oven_set_temperature",
                        "$thermocouple_temperature",
                        "$ambient_temperature",
                    ],
                }
            },
            {"$unwind": {"path": "$docs"}},
            {
                "$project": {
                    "sample_time": 1,
                    "source": "$docs.source",
                    "mean": "$docs.mean",
                    "max": "$docs.max",
                    "min": "$docs.min",
                    "dev": "$docs.dev",
                }
            },
        ]
        return pd.DataFrame(list(db["sample"].aggregate(aggregate_query)))

    @property
    def empty(_self) -> bool:
        db = mongo_tilt_db()
        sample = db["sample"].find_one(_self._match_query["$match"])
        return sample is None

    # TODO
    @property
    def test_info(self) -> dict:
        return get_test_info(self.test_ids)

    @property
    @st.cache_data(ttl=60)
    def sensor_names(_self) -> list[str]:
        if _self.empty:
            return []
        db = mongo_tilt_db()
        return list(db["sample"].distinct("sensor_name", _self._match_query["$match"]))

    @property
    def series_mapping(self) -> dict[str, str]:
        return {s: "-".join(s.split("-")[:-1]) for s in self.sensor_names}

    @property
    def series(self) -> list[str]:
        return list(set(self.series_mapping.values()))

    @property
    def sensor_groups(self) -> list[str]:
        return self.series

    @property
    @st.cache_data(ttl=60)
    def set_angles(_self) -> pd.DataFrame:
        if _self.empty:
            return []
        db = mongo_tilt_db()
        vals = list(
            db["sample"].distinct("stage_data.set_angle", _self._match_query["$match"])
        )
        return [round(v, 6) for v in vals]

    @property
    @st.cache_data(ttl=60)
    def zeroes(_self) -> pd.Series:
        df = _self._linearity()
        df = df.loc[(df["mean_raw"] > 32768 - 6000) & (df["mean_raw"] < 32768 + 6000)]
        ser = (
            df.groupby("sensor_name")
            .mean()
            .reset_index()[["angle", "sensor_name"]]
            .set_index("sensor_name")["angle"]
        )
        ser.name = "zero"

        return ser

    @st.cache_data(ttl=60)
    def _linearity(_self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            _self._match_query,
            {
                "$group": {
                    "_id": {
                        "angle": "$stage_data.set_angle",
                        "sensor_name": "$sensor_name",
                    },
                    "max_raw": {"$max": "$sensor_data.raw"},
                    "min_raw": {"$min": "$sensor_data.raw"},
                    "mean_raw": {"$avg": "$sensor_data.raw"},
                    "dev_raw": {"$stdDevSamp": "$sensor_data.raw"},
                }
            },
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(aggregate_query)))
        df = df.drop("_id", axis=1).join(pd.DataFrame(df["_id"].tolist()))

        df["angle"].round(6)

        return df

    def linearity(self, zeroed: bool = False, series: bool = False) -> pd.DataFrame:
        df = self._linearity().copy()

        if zeroed:
            df["zero"] = df["sensor_name"].map(self.zeroes)
            df["angle"] = df["angle"] - df["zero"]
            df.drop("zero", axis=1, inplace=True)
            round_column(df, "angle", self.set_angles)

        if series:
            df["series"] = df["sensor_name"].map(self.series_mapping)
            gb = df.groupby(["series", "angle"])
            df = gb["mean_raw"].mean().to_frame()
            df["max_raw"] = gb["max_raw"].max()
            df["min_raw"] = gb["min_raw"].min()
        else:
            df.set_index(["angle", "sensor_name"], inplace=True)

        return df

    @st.cache_data(ttl=60)
    def _repeatability(_self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            _self._match_query,
            {
                "$project": {
                    "angle": {"$round": ["$stage_data.set_angle", 6]},
                    "degrees": "$sensor_data.degrees",
                    "sensor_name": 1,
                }
            },
            {
                "$group": {
                    "_id": {
                        "angle": "$angle",
                        "sensor_name": "$sensor_name",
                    },
                    "max_degrees": {"$max": "$degrees"},
                    "min_degrees": {"$min": "$degrees"},
                }
            },
            {
                "$addFields": {
                    "range": {
                        "$sum": ["$max_degrees", {"$multiply": [-1, "$min_degrees"]}]
                    }
                }
            },
            {"$addFields": {"repeatability": {"$divide": ["$range", 2]}}},
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(aggregate_query)))
        df = df.drop("_id", axis=1).join(pd.DataFrame(df["_id"].tolist()))
        return df

    def repeatability(self, zeroed: bool = False, series: bool = False) -> pd.DataFrame:
        df = self._repeatability().copy()

        if zeroed:
            df["zero"] = df["sensor_name"].map(self.zeroes)
            df["angle"] = df["angle"] - df["zero"]

        if series:
            df["series"] = df["sensor_name"].map(self.series_mapping)
            round_column(df, "angle", self.set_angles)
            new_df = (
                df.groupby(["series", "angle"]).mean()[["repeatability"]].reset_index()
            )
            new_df.rename(columns={"repeatability": "mean_repeatability"}, inplace=True)
            new_df["max_repeatability"] = (
                df.groupby(["series", "angle"])
                .max()[["repeatability"]]
                .reset_index()["repeatability"]
            )
            new_df["min_repeatability"] = (
                df.groupby(["series", "angle"])
                .min()[["repeatability"]]
                .reset_index()["repeatability"]
            )
            df = new_df

        return df

    @property
    @st.cache_data(ttl=60)
    def accuracy(_self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            _self._match_query,
            {
                "$addFields": {
                    "error": {
                        "$sum": [
                            "$stage_data.stage_angle",
                            {"$multiply": [-1, "$sensor_data.degrees"]},
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "angle": "$stage_data.set_angle",
                        "sensor_name": "$sensor_name",
                    },
                    "max_error": {"$max": "$error"},
                    "min_error": {"$min": "$error"},
                    "mean_error": {"$avg": "$error"},
                    "dev_error": {"$stdDevSamp": "$error"},
                }
            },
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(aggregate_query)))
        df.info()
        df = df.drop("_id", axis=1).join(pd.DataFrame(df["_id"].tolist()))

        return df
