from celery.result import AsyncResult
from celery_task import app

async_result = AsyncResult(id="1c55da99-d9e7-448e-a0ba-4eaea2d1590e", app=app)

if async_result.successful():
    print(async_result.get())

elif async_result.failed():
    print('执行失败')
elif async_result.status == "PENDING":
    print('任务等待中被执行')
elif async_result.status == "RETRY":
    print('任务异常后正在重试')

elif async_result.status == "STARTED":
    print('任务已经开始被执行')