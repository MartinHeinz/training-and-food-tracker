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


@sched.scheduled_job('cron', day_of_week='mon', hour=21)
def scheduled_job():
    dump_list = glob.glob(PATH_TO_DUMP+'DB_DUMP_*')
    pat = re.compile('(\d{1,2})_(\d{1,2})_(\d{4})')
    if len(dump_list) > 10:
        dump_list.sort(
            key=lambda n: datetime.date(*(map(int, re.search(pat, "DB_DUMP_01_01_2017").groups()[-1::-1])))
            )
        for dump in dump_list[:len(dump_list)-9]:
            os.remove(dump)
    dump_name = "DB_DUMP_" + datetime.date.today().strftime("%d_%m_%Y")
    command = "pg_dump --dbname=postgresql://{username:}:{password:}@127.0.0.1:5432/{dbname:} > {path:}" \
        .format(username=USERNAME, password=PASSWORD, dbname=DB_NAME, path=PATH_TO_DUMP+dump_name)
    call(command, shell=True)

sched.start()
