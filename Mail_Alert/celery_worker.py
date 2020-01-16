#!/usr/bin/env python3
from mailalert import celery, create_app
from mailalert.tasks.tasks import update_students
from celery.schedules import crontab

app = create_app()
app.app_context().push()

celery.conf.beat_schedule = {
    'update-students-task': {
        'task': 'tasks.update_students',
        'schedule': crontab(minute=0, hour=0)  # daily at midnight
    }
}
