import pandas as pd
import schedule
import time, datetime
import sqlite3


def get_data():
    try:
        df = pd.read_csv("https://data.nhi.gov.tw/Datasets/Download.ashx?rid=A21030000I-D03001-001&l=https://data.nhi.gov.tw/resource/Nhi_Fst/Fstdata.csv")
        df.columns = ['Code', 'Name', 'Addr', 'Longitude', 'Latitude', 'Tel', 'Brand','Stock', 'Time', 'Note']
        print(f"{datetime.datetime.now():%Y%m%d %H:%M:%S}  success: {len(df)}",flush=True)
        conn = sqlite3.connect("./rapidtest.sqlite")
        df.to_sql('rapidtest',conn, if_exists='append')
        conn.close()
    except Exception as e:
        print(f"{datetime.datetime.now():%Y%m%d %H:%M:%S}  error:{e}")

for hour in range(6,22):
    for minute in range(0,60,5):
        #print(f"{hour:0>2}:{minute:0>2}")
        schedule.every().day.at(f"{hour:0>2}:{minute:0>2}").do(get_data)


print("--Start--",flush=True)
get_data()
while True:
    schedule.run_pending()
    time.sleep(1)