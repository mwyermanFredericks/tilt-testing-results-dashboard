import numpy as np
import pandas as pd


def calc_rep_on(sample_df, series_mapping, col, set_angles, set_angle_labels):
    set_repeatability_gb = sample_df.groupby([col, "sensor_name"])
    sr_max = pd.DataFrame(set_repeatability_gb["degrees"].max())
    sr_min = pd.DataFrame(set_repeatability_gb["degrees"].min())

    rep = pd.merge(
        sr_max, sr_min, left_index=True, right_index=True, suffixes=(".max", ".min")
    )
    rep = rep.rename_axis(["angle", "sensor_name"]).reset_index()
    rep.index = rep["angle"].astype(str) + rep["sensor_name"]

    rep["repeatability"] = (rep["degrees.max"] - rep["degrees.min"]) / 2
    rep["series"] = rep["sensor_name"].map(series_mapping)

    repc = rep.copy(deep=True)
    repc["angle"] = pd.cut(repc["angle"], set_angles, labels=set_angle_labels).fillna(
        set_angles.iloc[-1]
    )

    srep = repc.groupby(["angle", "series"]).mean(numeric_only=True)
    srep = srep.dropna(how="all")
    srep = srep.rename_axis(["angle", "series"]).reset_index()
    srep["angle"] = srep["angle"].astype(float)

    return rep, srep


def prepare_samples_df(sample_df):
    # filter large numbers
    sample_df = sample_df.loc[sample_df["degrees"] < 11.0].copy()

    sample_df["error"] = sample_df["degrees"] - sample_df["stage_angle"]
    sample_df["stage_error"] = sample_df["stage_angle"] - sample_df["set_angle"]
    sensor_names = sample_df["sensor_name"].unique()

    series_mapping = {s: "-".join(s.split("-")[:-1]) for s in sensor_names}

    # get series name from sensors
    sample_df["series"] = sample_df["sensor_name"].map(series_mapping)

    # zeroed raw
    zeroes = pd.DataFrame(
        sample_df.loc[sample_df["set_angle"] == 0.0]
        .groupby(["sensor_name"])
        .mean(numeric_only=True)["raw"]
    )
    zeroes["offset"] = 32767 - zeroes["raw"]
    sample_df["raw_offset"] = sample_df["sensor_name"].map(zeroes["offset"])
    sample_df["zeroed_raw"] = sample_df["raw"] + sample_df["raw_offset"]

    # zeroed angle
    zeroes = pd.DataFrame(
        sample_df.loc[sample_df["raw"].between(32767 - 2000, 32767 + 2000)]
        .groupby(["sensor_name"])
        .mean(numeric_only=True)["stage_angle"]
    )
    zeroes["offset"] = 0.0 - zeroes["stage_angle"]
    sample_df["stage_offset"] = sample_df["sensor_name"].map(zeroes["offset"])
    sample_df["zeroed_stage_angle"] = (
        sample_df["stage_angle"] + sample_df["stage_offset"]
    )
    sample_df["zeroed_set_angle"] = sample_df["set_angle"] + sample_df["stage_offset"]

    set_angles_temp = sorted(sample_df["set_angle"].round(4).unique())
    set_angles_temp_max = max(set_angles_temp)
    set_angles_temp_min = min(set_angles_temp)
    set_angles_temp_range = set_angles_temp_max - set_angles_temp_min
    set_angles_temp = (
        list(map(lambda x: x - set_angles_temp_range, set_angles_temp[:-1]))
        + set_angles_temp
        + list(map(lambda x: x + set_angles_temp_range, set_angles_temp[1:]))
    )

    set_angles = pd.Series([-np.inf] + set_angles_temp)
    set_angle_labels = set_angles.to_list()[1:]

    set_angle_rep_df, set_angle_series_rep_df = calc_rep_on(
        sample_df, series_mapping, "set_angle", set_angles, set_angle_labels
    )
    set_angle_rep_df_z, set_angle_series_rep_df_z = calc_rep_on(
        sample_df, series_mapping, "zeroed_set_angle", set_angles, set_angle_labels
    )

    # Create time series with fewer samples to have fewer rows
    downsampled_df = sample_df.resample("1T", on="sample_time").mean(numeric_only=True)
    downsampled_df["sample_time"] = downsampled_df.index

    return (
        sample_df,
        downsampled_df,
        set_angle_rep_df,
        set_angle_series_rep_df,
        set_angle_rep_df_z,
        set_angle_series_rep_df_z,
    )
