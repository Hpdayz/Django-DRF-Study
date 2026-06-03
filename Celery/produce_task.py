from celery_task import send_email, send_msg

result1 = send_email.delay('Hpday@123.com')
print(result1.id)

result2 = send_msg.delay('Hpday')
print(result2.id)