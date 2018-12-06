import schedule
import time
from soup import its_go_time

def job():
    its_go_time()

schedule.every().day.at('06:00').do(job)
schedule.every().day.at('12:00').do(job)
schedule.every().day.at('18:00').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)