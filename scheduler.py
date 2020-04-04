import atexit

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from server import cache, server
from updater import update_data

if __name__ == "__main__":

    scheduler = BlockingScheduler(timezone=pytz.timezone("Asia/Almaty"))
    atexit.register(lambda: scheduler.shutdown())

    scheduler.add_job(
        func=update_data, trigger="interval", minutes=server.config["FETCH_INTERVAL"]
    )
    scheduler.add_job(func=cache.clear, trigger="cron", minute=0, hour=0)

    scheduler.start()
