import time

from celery import Celery

backend = 'redis://:Hpday@8.136.200.128:6379/1'
broker = 'redis://:Hpday@8.136.200.128:6379/2'

app = Celery('Test', backend=backend, broker=broker)


@app.task
def send_email(name):
    print(f'正在发送邮件...{name}')
    time.sleep(5)
    print('邮件发送完成')


@app.task
def send_msg(name):
    print(f'正在发送短信...{name}')
    time.sleep(5)
    print('短信发送完成')
