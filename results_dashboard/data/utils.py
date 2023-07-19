from bson import ObjectId


def get_match_query(
    test_ids: list[str], sensor_mask: list[str] | None
) -> dict[str, dict]:
    test_id_list = [ObjectId(id) for id in test_ids]
    match_query: dict[str, dict] = {"$match": {"test_id": {"$in": test_id_list}}}
    if sensor_mask is not None:
        match_query["$match"]["sensor_name"] = {"$in": sensor_mask}
    return match_query
