import glob
import os
from subprocess import call

import datetime

import re
from apscheduler.schedulers.blocking import BlockingScheduler

PATH_TO_DUMP = "c:\\Users\\MH\\Desktop\\ProjectVenv\\TrainingAndFoodTracker\\src\\backups\\"
USERNAME = "postgres"
PASSWORD = "123456"
DB_NAME = "TrainingAndFoodTracker"



# call(command, shell=True)

# restore command
# psql -U postgres TrainingAndFoodTracker < DB_DUMP
# psql -U <username> <DB name> < <dump file path(name)>

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon', hour=21, minute=0)
def scheduled_job():
    regex = 'DB_DUMP_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{1,2})_(\d{4})$'
    files = os.listdir(PATH_TO_DUMP)
    pat = re.compile(regex)
    dump_list = [f for f in files if re.search(pat, f)]
    if len(dump_list) > 10:
        dump_list.sort(
            key=lambda n: datetime.datetime.strptime(n, "DB_DUMP_%H_%M_%S_%d_%m_%Y")
            )
        for dump in dump_list[:len(dump_list)-9]:
            os.remove(PATH_TO_DUMP+dump)
    dump_name = "DB_DUMP_" + datetime.datetime.today().strftime("%H_%M_%S_%d_%m_%Y")
    command = "pg_dump --dbname=postgresql://{username:}:{password:}@127.0.0.1:5432/{dbname:} > {path:}" \
        .format(username=USERNAME, password=PASSWORD, dbname=DB_NAME, path=PATH_TO_DUMP+dump_name)
    call(command, shell=True)

sched.start()
