from django.core.cache import cache


def clear_locations_cache():
    cache.delete_pattern("locations:list:*")