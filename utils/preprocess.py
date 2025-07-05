def clean_data(data_dict):
    """
    Ensures the fetched data is clean and usable for DCF calculations.
    Replaces None, NaN, or 0 shares with safe defaults.
    """
    clean = {}

    for key, value in data_dict.items():
        if value is None:
            clean[key] = 0
        elif isinstance(value, float) and (value != value):  # Check for NaN
            clean[key] = 0
        else:
            clean[key] = value

    # Prevent divide-by-zero errors
    if clean.get("shares_outstanding", 0) <= 0:
        clean["shares_outstanding"] = 1

    return clean
