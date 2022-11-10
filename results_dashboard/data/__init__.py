import numpy as np
import pandas as pd
import streamlit as st
import numpy as sn

from .mongo.samples_db import get_samples
from .mongo.tests_db import get_test_info


class SensorData:
    def __init__(self, test_ids: str | list[str]) -> None:
        self.test_ids = test_ids
        self.sensor_mask: list[str] | None = None

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
        return self._rep("set_angle")

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
        df = self.samples.copy()
        df["error"] = abs(df["error"])
        gb = df.groupby(["set_angle", "sensor_name"])
        acc_max = pd.DataFrame(gb["error"].max())
        acc_min = pd.DataFrame(gb["error"].min())
        acc_mean = pd.DataFrame(gb["error"].mean())
        acc = pd.merge(
            acc_max,
            acc_min,
            left_index=True,
            right_index=True,
            suffixes=(".max", ".min"),
        )
        acc = pd.merge(acc, acc_mean, left_index=True, right_index=True)
        acc = acc.rename_axis(["angle", "sensor_name"]).reset_index()
        acc["series"] = acc["sensor_name"].map(self.series_mapping)
        return acc

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
