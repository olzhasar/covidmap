import atexit

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from app.cache import cache
from app.config import Config
from tasks.update import update_task

if __name__ == "__main__":

    scheduler = BlockingScheduler(timezone=pytz.timezone("Asia/Almaty"))
    atexit.register(lambda: scheduler.shutdown())

    scheduler.add_job(
        func=update_task, trigger="interval", minutes=Config.FETCH_INTERVAL
    )
    scheduler.add_job(func=cache.clear, trigger="cron", minute=0, hour=0)

    scheduler.start()
