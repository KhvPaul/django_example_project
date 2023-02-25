import os
from datetime import timedelta

from celery import Celery

# set the default Django settings module for the "celery" program.
from celery.schedules import crontab  # noqa: I202


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_example_project.settings")

app = Celery("django_example_project")

# Using a string here means the worker doesn"t have to serialize
# the configuration object to child processes.
# - namespace="CELERY" means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # executes every 1 minute
    # "scraping-task-one-min": {
    #     "task": "scraping.tasks.hackernews_rss",
    #     "schedule": crontab(),
    # },
    # # executes every 15 minutes
    # "scraping-task-fifteen-min": {
    #     "task": "tasks.hackernews_rss",
    #     "schedule": crontab(minute="*/15")
    # },
    # # executes daily at midnight
    # "scraping-task-midnight-daily": {
    #     "task": "tasks.hackernews_rss",
    #     "schedule": crontab(minute=0, hour=0)
    # },
    "send-email-to-admin": {
        "task": "catalog.tasks.send_mail_to_admin",
        "schedule": crontab(minute="*/10"),
    },
    "parsing": {
        "task": "catalog.tasks.parse_news",
        "schedule": timedelta(seconds=10),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")  # noqa: T001, T201
