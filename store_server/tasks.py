from django.core.management import call_command

from celery import shared_task

@shared_task()
def dbackup_task():
    '''¬ыполнение резервного копировани€ базы'''

    call_command('dbackup')