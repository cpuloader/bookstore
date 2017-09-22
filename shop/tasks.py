from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
from celery.decorators import periodic_task

from bookstoreproj.celery import app as celery_app


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    #sender.add_periodic_task(30.0, top_books.s())

    sender.add_periodic_task(
        crontab(hour=6, minute=0), top_books.s(),
    )

@celery_app.task
def top_books():
    from shop.utils import set_top_books
    set_top_books()
