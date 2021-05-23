# Early 2021
# Author metachris 
# Part of frischluft.works
# Filename: databuffer.py
# Purpose: Manages datapoints, Provides data to various components like the webserver
# License Details found @ /LICENSE file in this repository
# 


# import json
import time

SECONDS_BETWEEN_ENTRIES = 60  # change this to speed up animation in webfrontend
MAX_ENTRIES = 100   # 60 entries for one hour

class Buffer:
    # current = 0
    last_entry_timestamp = 0
    entries = []

    def __init__(self):
        self.last_entry_timestamp = 0
        self.entries = []

    def add(self, value, force=False):
        # Do nothing if too soon
        if self.last_entry_timestamp + SECONDS_BETWEEN_ENTRIES > time.time() and not force:
            return

        # Add entry
        self.last_entry_timestamp = time.time()
        self.entries.append(value)

        # If too long, pop oldest item
        if len(self.entries) > MAX_ENTRIES:
            self.entries.pop(0)

    def __str__(self):
        return ", ".join(str(e) for e in self.entries)

    def __repr__(self):
        return self.entries


buffers = {
    "ppm": Buffer()
}


def add_datapoint(key, value, force=False):
    # print('add_datapoint data:', key, value)
    global buffers

    if key not in buffers:
        buffers[key] = Buffer()

    buffers[key].add(value, force=force)
    # print(buffers)


if __name__ == '__main__':
    add_datapoint('ppm', 123)
    add_datapoint('ppm', 28, force=True)
    add_datapoint('ppm', 13, force=True)
    add_datapoint('temp', 18, force=True)
    add_datapoint('humidity', 40, force=True)
    add_datapoint('temp', 28, force=True)
    add_datapoint('humidity', 43, force=True)   
    print(json.dumps(buffers))
