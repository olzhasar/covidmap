import atexit

from apscheduler.schedulers.blocking import BlockingScheduler

from server import server
from updater import update_data

if __name__ == "__main__":

    scheduler = BlockingScheduler()
    atexit.register(lambda: scheduler.shutdown())

    scheduler.add_job(
        func=update_data, trigger="interval", seconds=server.config["FETCH_INTERVAL"]
    )
    scheduler.start()
