from curses import flushinp
import pandas as pd
import schedule
import time, datetime
import sqlite3


def get_data():
    print('test', datetime.datetime.now(),flush=True)

# 8-22
for hour in range(7,23):
    for minute in range(0,60,5):
        print(f"{hour:0>2}:{minute:0>2}")
        #schedule.every().day.at(f"{hour:0>2}:{minute:0>2}").do(get_data)


print("--Start--",flush=True)
get_data()
while True:
    schedule.run_pending()
    time.sleep(1)