from bson import ObjectId


def get_match_query(
    test_ids: list[str], sensor_mask: list[str] | None
) -> list[dict[str, dict]]:
    test_id_list = [ObjectId(id) for id in test_ids]
    test_id_stage: dict[str, dict] = {"$match": {"test_id": {"$in": test_id_list}}}
    if sensor_mask is not None:
        test_id_stage["$match"]["sensor_name"] = {"$in": sensor_mask}
    return [test_id_stage]
