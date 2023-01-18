import hashlib
import json

import numpy as np
import croniter
import datetime

from api.utils.datetime_convertor import get_current_local_time


def create_symbol_hash(symbols):
    symbols.sort()
    return hashlib.sha1('-'.join(symbols).encode("utf-8")).hexdigest()


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def is_required_scheduling(cron_syntax, minutes: int):
    now = get_current_local_time()
    next_schedule = now + datetime.timedelta(minutes=minutes)
    # sched = '1 15 1,15 * *'    # at 3:01pm on the 1st and 15th of every month
    if not croniter.croniter.is_valid(cron_syntax):
        print("Invalid cron syntax")
        return False, None
    print(f"next_schedule==>{next_schedule}")
    cron = croniter.croniter(cron_syntax, now)
    next = cron.get_next(datetime.datetime)
    print(f"next cron schedule==>{next}")
    if now <= next_schedule < next:
        return True, next
    return False, None
