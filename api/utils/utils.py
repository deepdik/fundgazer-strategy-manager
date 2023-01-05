import hashlib
import json

import numpy as np
import croniter
import datetime


def create_symbol_hash(symbols):
    symbols.sort()
    return hashlib.sha1('-'.join(symbols).encode("utf-8")).hexdigest()


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def is_required_scheduling(cron_syntax, minutes: int):
    now = datetime.datetime.now()
    next_schedule = now + datetime.timedelta(minutes=minutes)
    # sched = '1 15 1,15 * *'    # at 3:01pm on the 1st and 15th of every month
    cron = croniter.croniter(cron_syntax, now)
    next = cron.get_next(datetime.datetime)
    if next_schedule > cron.get_next(datetime.datetime):
        return True, next
    return False, None
