from cachetools import TTLCache


def get_decoded_node_metadata_from_cache(cache, node: float, metadata: str):
    node_data = cache.get(node)
    if not node_data:
        return "unknown"
    v = node_data.get(metadata)
    if v is None:
        return "unknown"
    return v


def save_node_metadata_in_cache(cache, node: float, node_info: dict, ex=3600 * 72):
    cache[node] = {
        "long_name": node_info["longName"],
        "short_name": node_info["shortName"],
        "hw_model": node_info["hwModel"],
        "is_licensed": str(node_info.get("isLicensed", False)),
    }
    # TTL is managed by cachetools, so 'ex' is set at cache creation
