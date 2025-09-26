from math import radians, cos, sin, asin, sqrt


def haversine(lat1, lon1, lat2, lon2, unit="km"):
    """Return distance between two points in km, miles, or meters."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    R_km = 6371
    distance_km = R_km * c
    if unit == "km":
        return distance_km
    elif unit == "miles":
        return distance_km * 0.621371
    elif unit == "meters":
        return distance_km * 1000
    else:
        raise ValueError("Invalid unit. Choose 'km', 'miles', or 'meters'.")
