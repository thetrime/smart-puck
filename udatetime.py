"""
Date conversion functions not provided by micropython
"""

from time import mktime, gmtime

def timestamp_to_iso8601(timestamp):
    # Convert to tuple (year, month, day, hour, minute, second)
    t = gmtime(timestamp)

    # Format as ISO 8601 string (YYYY-MM-DDTHH:MM:SSZ)
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*t[:6])

def iso8601_to_timestamp(sync_time):
    # Parse the ISO-8601 timestamp manually because micropython doesnt have datetime
    year, month, day, hour, minute, second = map(int, [
        sync_time[0:4],  sync_time[5:7],  sync_time[8:10],
        sync_time[11:13], sync_time[14:16], sync_time[17:19]
    ])

    # Convert to struct_time
    dt_0 = (year, month, day, hour, minute, second, 0, 0, 0)

    # Convert to Unix timestamp
    t_0 = mktime(dt_0)

    return t_0

def format_date(timestamp):
    return timestamp_to_iso8601(timestamp)
