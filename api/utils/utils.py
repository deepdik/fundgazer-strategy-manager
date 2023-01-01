import hashlib
import json

import numpy as np


def create_symbol_hash(symbols):
    symbols.sort()
    return hashlib.sha1('-'.join(symbols).encode("utf-8")).hexdigest()


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)