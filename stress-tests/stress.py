import datetime
import os
import random

import pandas as pd
from locust import HttpUser, between, task, LoadTestShape
from locust.event import EventHook
from loguru import logger

header_names = ['file_path', 'transcription', 'transcription_2', 'duration']
DATA = pd.read_csv('datasets/transcript.txt', sep="|", header=None, names=header_names)
SIZE = len(DATA)
logger.info(f"Loads {SIZE} wav")
print(DATA.head())
print(DATA.iloc[200].file_path)

rtf_report_filename = "rtf_report.txt"


try:
    os.remove(rtf_report_filename)
except OSError:
    pass
with open(rtf_report_filename, "a") as f:
    f.write(f"date;filename;rtf;duration;processing_time\n")
my_event = EventHook()


def on_rtf_event(date, rtf, filename, duration, processing_time, **kw):
    with open(rtf_report_filename, "a") as f:
        f.write(f"{date};{filename};{rtf};{duration};{processing_time} \n")


my_event.add_listener(on_rtf_event)


class Speech2TextStressTest(HttpUser):
    wait_time = between(0.01, 0.1)

    def on_start(self):
        pass

    @task
    def index(self):
        random_index = random.randint(0, SIZE - 1)
        file_path = DATA.iloc[random_index].file_path
        path, filename = os.path.split(os.path.relpath(file_path))
        file_path_16k = f"datasets/{path}/16k_{filename}"

        files = [
            ('file', (file_path_16k, open(file_path_16k, "rb"), 'audio/wav')),
        ]
        t1 = datetime.datetime.now()

        self.client.post("/rest/speech2text/fr", files=files)
        t2 = datetime.datetime.now()
        delta = t2 - t1

        processing_time = delta.total_seconds()
        duration = DATA.iloc[random_index].duration
        rtf = processing_time / duration

        my_event.fire(date=datetime.datetime.now(), rtf=rtf, filename=filename, duration=duration,
                      processing_time=processing_time)



class StagesShapeWithCustomUsers(LoadTestShape):
    """
    A simply load test shape class that has different user and spawn_rate at
    different stages.

    Keyword arguments:

        stages -- A list of dicts, each representing a stage with the following keys:
            duration -- When this many seconds pass the test is advanced to the next stage
            users -- Total user count
            spawn_rate -- Number of users to start/stop per second
            stop -- A boolean that can stop that test at a specific stage

        stop_at_end -- Can be set to stop once all stages have run.
    """

    stages = [
        {"duration": 60, "users": 1, "spawn_rate": 1},
        {"duration": 120, "users": 2, "spawn_rate": 2},
        {"duration": 180, "users": 3, "spawn_rate": 3},
        {"duration": 240, "users": 4, "spawn_rate": 4},
        {"duration": 280, "users": 1, "spawn_rate": 1},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                try:
                    tick_data = (stage["users"], stage["spawn_rate"], stage["user_classes"])
                except KeyError:
                    tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data

        return None