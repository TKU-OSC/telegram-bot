def _signed_num_sizeof(value):
    from math import log2, ceil
    return ceil((ceil(log2(value + 1 if value >= 0 else abs(value))) + 1) / 8)
