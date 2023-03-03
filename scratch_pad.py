# import importlib

# strategy = "mpt_strategies"

# module = importlib.import_module(f"api.utils.strategy_logics.strategy.{strategy}")

# print(module.MIN_ORDER_SIZE_CRYPTO)


import asyncio
import datetime
from api.repository.task_schedular import get_task_list_new, get_task_list


# tasks = asyncio.run(get_task_list())
tasks = asyncio.run(get_task_list_new())
# print(tasks)

for task in tasks:
    # print(task)

    if task.get("startDate", False):
        startDate = task["startDate"]
        startDate = datetime.datetime.strptime(startDate, "%d-%m-%Y")
        # print(startDate)
    if task.get("runTime", False):
        runTime = task["runTime"]
        runTime = datetime.datetime.strptime(runTime, "%H:%M").time()
        # print(runTime)

    print("Run-Time: ", datetime.datetime.combine(startDate, runTime))

    # print(f"got status and runtime {status}, {schedule_time}")
    if task.get("status"):
        if isinstance(task.get("symbolList"), list):
            symbol_list = task.get("symbolList")
        elif isinstance(task.get("symbolList"), str):
            symbol_list = task.get("symbolList").split(",")

    print(symbol_list)
