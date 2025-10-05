from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from recognition.recognition import auto_mark_absent

scheduler = BackgroundScheduler()

# 后台启动每分钟自动设置Absent程序

def start():
    scheduler.add_job(auto_mark_absent, 'interval', minutes = 1, id='auto_mark_absent')
    scheduler.start()
    print("Scheduler successfully starts!")