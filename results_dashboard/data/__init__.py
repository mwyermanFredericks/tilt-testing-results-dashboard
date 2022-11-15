import numpy as np
import pandas as pd
import streamlit as st
from typing import List, Union
import numpy as sn
from bson import ObjectId

from .mongo.samples_db import get_samples
from .mongo.tests_db import get_test_info
from .mongo import mongo_tilt_db


def get_test_repeatability(test_ids: Union[str, List[str]], sensor_mask: Union[None, List[str]] = None) -> pd.DataFrame:
    db = mongo_tilt_db()
    if isinstance(test_ids, str):
        query_ids = [ObjectId(test_ids)]
    else:
        query_ids = [ObjectId(test_id) for test_id in test_ids]

    test_query  = {
        'test_id': {'$in': query_ids},
    }

    if isinstance(sensor_mask, str):
        test_query['sensor_name'] = sensor_mask
    elif isinstance(sensor_mask, list):
        test_query['sensor_name'] = {'$in': sensor_mask}

    aggregate_query = [
        {
            '$match': test_query,
        }, {
            '$group': {
                '_id': {
                    'angle': '$stage_data.set_angle', 
                    'sensor_name': '$sensor_name'
                }, 
                'max_degrees': {
                    '$max': '$sensor_data.degrees'
                }, 
                'min_degrees': {
                    '$min': '$sensor_data.degrees'
                }
            }
        }, {
            '$addFields': {
                'range': {
                    '$sum': [
                        '$max_degrees', {
                            '$multiply': [
                                -1, '$min_degrees'
                            ]
                        }
                    ]
                }
            }
        }, {
            '$addFields': {
                'repeatability': {
                    '$divide': [
                        '$range', 2
                    ]
                }
            }
        }
    ]

    df = pd.DataFrame(list(db["sample"].aggregate(
        aggregate_query
    )))
    df.info()
    df = df.drop('_id', axis=1).join(pd.DataFrame(df['_id'].tolist()))
    
    return df


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
        self._test_ids = test_ids

    @property
    def sensor_mask(self) -> list[str] | None:
        return self._sensor_mask
    
    @sensor_mask.setter
    def sensor_mask(self, sensor_mask: list[str] | None) -> None:
        self._sensor_mask = sensor_mask

    @property
    def _match_query(self) -> dict:
        query_ids = [ObjectId(test_id) for test_id in self.test_ids]
        query = {
            '$match': {
                'test_id': {'$in': query_ids}
            }
        }

        if self.sensor_mask:
            query['$match']['sensor_name'] = {'$in': self.sensor_mask}

        return query

    @property
    def angle_data(self) -> pd.DataFrame:
        db = mongo_tilt_db()
        aggregate_query = [
            self._match_query, {
                '$group': {
                    '_id': '$sample_time', 
                    'stage_data': {
                        '$first': '$stage_data'
                    }
                }
            }, {
                '$replaceRoot': {
                    'newRoot': {
                        '$mergeObjects': [
                            '$$ROOT', '$stage_data'
                        ]
                    }
                }
            }, {
                '$project': {
                    'stage_data': 0
                }
            }, {
                '$sort': {
                    '_id': 1
                }
            }, {
                '$group': {
                    '_id': 0, 
                    'document': {
                        '$push': '$$ROOT'
                    }
                }
            }, {
                '$project': {
                    'documentAndPrevAngle': {
                        '$zip': {
                            'inputs': [
                                '$document', {
                                    '$concatArrays': [
                                        [
                                            None
                                        ], '$document.set_angle'
                                    ]
                                }
                            ]
                        }
                    }
                }
            }, {
                '$unwind': {
                    'path': '$documentAndPrevAngle'
                }
            }, {
                '$replaceWith': {
                    '$mergeObjects': [
                        {
                            '$arrayElemAt': [
                                '$documentAndPrevAngle', 0
                            ]
                        }, {
                            'prev_angle': {
                                '$arrayElemAt': [
                                    '$documentAndPrevAngle', 1
                                ]
                            }
                        }
                    ]
                }
            }, {
                '$set': {
                    'angle_difference': {
                        '$subtract': [
                            '$set_angle', '$prev_angle'
                        ]
                    }
                }
            }, {
                '$match': {
                    'angle_difference': {
                        '$ne': 0
                    }
                }
            }, {
                '$project': {
                    'prev_angle': 0,
                    'angle_difference': 0
                }
            }, {
                '$set': {
                    'sample_time': '$_id'
                }
            }
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(
            aggregate_query
        )))
        
        return df

    @property
    def _raw_samples(self) -> pd.DataFrame:
        samples = get_samples(self.test_ids)
        if self.sensor_mask:
            samples = samples[samples["sensor_name"].isin(self.sensor_mask)]
        return samples

    @property
    def empty(self) -> bool:
        return self._raw_samples.empty

    @property
    def test_info(self) -> dict:
        return get_test_info(self.test_ids)

    @property
    def sensor_names(self) -> list[str]:
        if self._raw_samples.empty:
            return []
        return self._raw_samples["sensor_name"].unique().tolist()

    @property
    def series_mapping(self) -> dict[str, str]:
        return {s: "-".join(s.split("-")[:-1]) for s in self.sensor_names}

    @property
    def series(self) -> list[str]:
        return self.samples["series"].unique().tolist()

    @property
    def sensor_groups(self) -> list[str]:
        return self.series

    @property
    def samples(self) -> pd.DataFrame:
        df = self._raw_samples.copy()
        if df.empty:
            return df
        df["error"] = df["degrees"] - df["stage_angle"]
        df["stage_error"] = df["stage_angle"] - df["set_angle"]
        df["series"] = df["sensor_name"].map(self.series_mapping)
        return df

    @property
    def zeroed_samples(self) -> pd.DataFrame:
        df = self.samples.copy()
        if df.empty:
            return df
        zeroed_raw = pd.DataFrame(
            df.loc[df["set_angle"] == 0.0]
            .groupby(["sensor_name"])
            .mean(numeric_only=True)["raw"]
        )
        zeroed_raw["offset"] = 32767 - zeroed_raw["raw"]
        df["raw_offset"] = df["sensor_name"].map(zeroed_raw["offset"])
        df["zeroed_raw"] = df["raw"] + df["raw_offset"]

        zeroed_stage_angle = pd.DataFrame(
            df.loc[df["raw"].between(32767 - 2000, 32767 + 2000)]
            .groupby(["sensor_name"])
            .mean(numeric_only=True)["stage_angle"]
        )
        zeroed_stage_angle["offset"] = 0.0 - zeroed_stage_angle["stage_angle"]
        df["stage_offset"] = df["sensor_name"].map(zeroed_stage_angle["offset"])
        df["zeroed_stage_angle"] = df["stage_angle"] + df["stage_offset"]
        df["zeroed_set_angle"] = df["set_angle"] + df["stage_offset"]
        return df

    @property
    def set_angles(self) -> pd.DataFrame:
        df = self._raw_samples.copy()

        # generate angles at normal intervals throughout the test
        set_angles_temp = sorted(df["set_angle"].round(4).unique())
        set_angles_temp_max = max(set_angles_temp)
        set_angles_temp_min = min(set_angles_temp)
        set_angles_temp_range = set_angles_temp_max - set_angles_temp_min
        set_angles_temp = (
            list(map(lambda x: x - set_angles_temp_range, set_angles_temp[:-1]))
            + set_angles_temp
            + list(map(lambda x: x + set_angles_temp_range, set_angles_temp[1:]))
        )

        set_angles = pd.Series([-np.inf] + set_angles_temp)
        return set_angles

    def _rep(self, set_angle_col: str) -> pd.DataFrame:
        if self.empty:
            return pd.DataFrame()
        set_repeatability_gb = self.zeroed_samples.groupby(
            [set_angle_col, "sensor_name"]
        )
        sr_max = pd.DataFrame(set_repeatability_gb["degrees"].max())
        sr_min = pd.DataFrame(set_repeatability_gb["degrees"].min())

        rep = pd.merge(
            sr_max, sr_min, left_index=True, right_index=True, suffixes=(".max", ".min")
        )
        rep = rep.rename_axis(["angle", "sensor_name"]).reset_index()
        rep.index = rep["angle"].astype(str) + rep["sensor_name"]

        rep["repeatability"] = (rep["degrees.max"] - rep["degrees.min"]) / 2
        rep["series"] = rep["sensor_name"].map(self.series_mapping)
        return rep

    @property
    def repeatability(self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            self._match_query,
            {
                '$group': {
                    '_id': {
                        'angle': '$stage_data.set_angle', 
                        'sensor_name': '$sensor_name'
                    }, 
                    'max_degrees': {
                        '$max': '$sensor_data.degrees'
                    }, 
                    'min_degrees': {
                        '$min': '$sensor_data.degrees'
                    }
                }
            }, {
                '$addFields': {
                    'range': {
                        '$sum': [
                            '$max_degrees', {
                                '$multiply': [
                                    -1, '$min_degrees'
                                ]
                            }
                        ]
                    }
                }
            }, {
                '$addFields': {
                    'repeatability': {
                        '$divide': [
                            '$range', 2
                        ]
                    }
                }
            }
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(
            aggregate_query
        )))
        df = df.drop('_id', axis=1).join(pd.DataFrame(df['_id'].tolist()))
        
        return df

    @property
    def repeatability_zeroed(self) -> pd.DataFrame:
        return self._rep("zeroed_set_angle")

    def _series_rep(self, df: pd.DataFrame) -> pd.DataFrame:
        set_angles = self.set_angles.copy()
        set_angle_labels = set_angles.to_list()[1:]
        df = df.copy()
        df["angle"] = pd.cut(df["angle"], set_angles, labels=set_angle_labels).fillna(
            set_angles.iloc[-1]
        )

        df = df.groupby(["angle", "series"]).mean(numeric_only=True)
        df = df.dropna(how="all")
        df = df.rename_axis(["angle", "series"]).reset_index()
        df["angle"] = df["angle"].astype(float)
        return df

    @property
    def accuracy(self) -> pd.DataFrame:
        db = mongo_tilt_db()

        aggregate_query = [
            self._match_query, {
                '$addFields': {
                    'error': {
                        '$sum': [
                            '$stage_data.stage_angle', {
                                '$multiply': [
                                    -1, '$sensor_data.degrees'
                                ]
                            }
                        ]
                    }
                }
            }, {
                '$group': {
                    '_id': {
                        'angle': '$stage_data.set_angle', 
                        'sensor_name': '$sensor_name'
                    }, 
                    'max_error': {
                        '$max': '$error'
                    }, 
                    'min_error': {
                        '$min': '$error'
                    }, 
                    'mean_error': {
                        '$avg': '$error'
                    }, 
                    'dev_error': {
                        '$stdDevSamp': '$error'
                    }
                }
            }
        ]

        df = pd.DataFrame(list(db["sample"].aggregate(
            aggregate_query
        )))
        df.info()
        df = df.drop('_id', axis=1).join(pd.DataFrame(df['_id'].tolist()))
        
        return df

    @property
    def series_repeatability(self) -> pd.DataFrame:
        return self._series_rep(self.repeatability)

    @property
    def series_repeatability_zeroed(self) -> pd.DataFrame:
        return self._series_rep(self.repeatability_zeroed)

    @property
    def downsampled(self) -> pd.DataFrame:
        df = self.samples.copy()
        downsampled_df = df.resample("1T", on="sample_time").mean(numeric_only=True)
        downsampled_df["sample_time"] = downsampled_df.index
        return downsampled_df
