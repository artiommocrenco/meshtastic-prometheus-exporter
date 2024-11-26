def get_decoded_node_metadata_from_redis(redis, node: float, metadata: str):
    v = redis.hget(node, metadata)
    try:
        v = "unknown" if v is None else v.decode("utf-8")
    except UnicodeDecodeError:
        v = "unknown"
    return v


def save_node_metadata_in_redis(redis, node: float, node_info: dict, ex=3600 * 72):
    redis.hset(
        node,
        mapping={
            "long_name": node_info["longName"],
            "short_name": node_info["shortName"],
            "hw_model": node_info["hwModel"],
            "is_licensed": str(node_info.get("isLicensed", False)),
        },
    )
    redis.expire(node, ex)
