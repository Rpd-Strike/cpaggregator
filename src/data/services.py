import math
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.text import slugify

from core.logging import log
from data.models import MethodTag, Task, Submission, UserProfile, UserHandle, TaskSource, JudgeTaskStatistic
from scraper.database import get_db
import scraper.services as scraper_services

from celery import shared_task


def __update_task_info(db, task: Task):
    log.info("Updating {}...".format(task))

    mongo_task_info = None
    for tries in range(3):
        mongo_task_info = db['tasks'].find_one({
            'judge_id': task.judge.judge_id.lower(),
            'task_id': task.task_id.lower(),
        })
        if mongo_task_info:
            break

        log.info(f'Task info for {task} not found in mongo.')
        log.info('Redirecting to scraper...')
        scraper_services.scrape_task_info(db, f"{task.judge.judge_id}:{task.task_id}")
        log.warning('Retrying...')

    if not mongo_task_info:
        log.error(f'Fetching task info for {task} failed!')
        return

    task.name = mongo_task_info['title']
    if 'time_limit' in mongo_task_info:
        task.time_limit_ms = mongo_task_info['time_limit']
    if 'memory_limit' in mongo_task_info:
        task.memory_limit_kb = mongo_task_info['memory_limit']
    if 'statement' in mongo_task_info:
        task.statement = mongo_task_info['statement']

    for tag_id in mongo_task_info.get('tags', []):
        try:
            tag = MethodTag.objects.get(tag_id=tag_id)
            task.tags.add(tag)
        except ObjectDoesNotExist:
            log.warning('Skipped adding tag {}. Does not exist'.format(tag_id))

    if 'source' in mongo_task_info:
        source_id = slugify(mongo_task_info['source'])
        source, _ = TaskSource.objects.get_or_create(
            judge=task.judge, source_id=source_id,
            defaults={
                'name': mongo_task_info['source']})
        task.source = source

    task.save()
    statistic_defaults = dict(
        total_submission_count=mongo_task_info.get('total_submission_count'),
        accepted_submission_count=mongo_task_info.get('accepted_submission_count'),
        first_submitted_on=mongo_task_info.get('first_submitted_on'),
    )
    statistic_defaults = {k: v for k, v in statistic_defaults.items() if v}
    if len(statistic_defaults) > 0:
        JudgeTaskStatistic.objects.get_or_create(task=task, defaults=statistic_defaults)


def __update_handle(db, handle):
    log.info(f"Updating {handle}...")

    mongo_handle_info = None
    for tries in range(3):
        mongo_handle_info = db['handles'].find_one({
            'judge_id': handle.judge.judge_id.lower(),
            'handle': handle.handle.lower(),
        })
        if mongo_handle_info:
            break

        log.info(f'Handle info for {handle} not found.')
        log.info('Redirecting to scraper...')
        scraper_services.scrape_handle_info(db, ":".join([handle.judge.judge_id, handle.handle]))

    if not mongo_handle_info:
        log.error(f"Handle info for {handle} not found.")
        return

    if 'photo_url' in mongo_handle_info:
        handle.photo_url = mongo_handle_info['photo_url']
    else:
        handle.photo_url = None

    handle.save()


TASKS_TO_ADD = set()


def __update_user_quick(db, user):
    log.info(f"Updating '{user.username}' quick as a fox...")

    for user_handle in user.handles.select_related('judge').all():
        log.info(f"Updating handle '{user_handle}'")
        judge = user_handle.judge
        # Get all submissions from mongodb.
        mongo_submissions = list(db['submissions'].find({
            'judge_id': judge.judge_id.lower(),
            'author_id': user_handle.handle.lower(),
        }))

        all_task_ids = list(set([ms['task_id'] for ms in mongo_submissions]))
        available_tasks = {task.task_id: task for task in
                           Task.objects.filter(judge=judge, task_id__in=all_task_ids).all()}

        missing_tasks = set(all_task_ids) - set(available_tasks.keys())
        log.info(f"{len(missing_tasks)}/{len(all_task_ids)} tasks are missing.")

        mongo_submissions = [ms for ms in mongo_submissions if ms['task_id'] in available_tasks]
        all_submission_ids = [ms['submission_id'] for ms in mongo_submissions]
        subs_already_there = set(Submission.objects.filter(submission_id__in=all_submission_ids,
                                                           author=user_handle)
                                 .values_list('submission_id', flat=True))

        log.info(f"{len(subs_already_there)}/{len(mongo_submissions)} submissions already present.")

        mongo_submissions = [ms for ms in mongo_submissions
                             if str(ms['submission_id']) not in subs_already_there]
        log.debug([ms['submission_id'] for ms in mongo_submissions])

        submissions_to_insert = []
        for ms in mongo_submissions:
            insert_kwargs = dict(
                submission_id=ms['submission_id'],
                submitted_on=timezone.make_aware(ms['submitted_on']),
                author=user_handle,
                task=available_tasks[ms['task_id']],
                verdict=ms['verdict'],
                language=ms.get('language'),
                source_size=ms.get('source_size'),
                score=ms.get('score'),
                exec_time=ms.get('exec_time'),
                memory_used=ms.get('memory_used'),
            )
            if insert_kwargs['score'] and math.isnan(insert_kwargs['score']):
                insert_kwargs['score'] = None
            insert_kwargs = {k: v for k, v in insert_kwargs.items() if v is not None}
            submissions_to_insert.append(Submission(**insert_kwargs))

        Submission.objects.bulk_create(submissions_to_insert)


def __update_user(db, user):
    log.info(f"Updating '{user.username}'...")

    for user_handle in user.handles.all():
        judge = user_handle.judge
        # Get all submissions from mongodb.
        mongo_submissions = db['submissions'].find(dict(
            judge_id=judge.judge_id.lower(),
            author_id=user_handle.handle.lower(),
        ))
        # Migrate submission model to SQL model.
        for mongo_submission in mongo_submissions:
            submission_id = mongo_submission['submission_id']
            task_id = mongo_submission['task_id'].lower()
            try:
                task = Task.objects.get(
                    judge=judge,
                    task_id=task_id)
            except ObjectDoesNotExist:
                TASKS_TO_ADD.add(task_id)
                continue

            try:
                update_dict = dict(
                    submitted_on=timezone.make_aware(mongo_submission['submitted_on']),
                    task=task,
                    verdict=mongo_submission['verdict'],
                    language=mongo_submission.get('language'),
                    source_size=mongo_submission.get('source_size'),
                    score=mongo_submission.get('score'),
                    exec_time=mongo_submission.get('exec_time'),
                    memory_used=mongo_submission.get('memory_used'),
                )
                if update_dict['score'] and math.isnan(update_dict['score']):
                    update_dict['score'] = None

                # Filter values that are None.
                update_dict = dict(filter(lambda x: x[1] and x[1], update_dict.items()))

                _, created = Submission.objects.update_or_create(
                    submission_id=submission_id,
                    author=user_handle, defaults=update_dict
                )

                if created:
                    log.info("Submission %s created." % mongo_submission['submission_id'])

            except Exception as e:
                log.exception('Submission %s failed. Error: %s' % (mongo_submission['submission_id'], e))


@shared_task
def update_tasks_info(*tasks):
    db = get_db()
    log.info(f'Updating tasks info for {tasks}...')
    for task in tasks:
        try:
            judge_id, task_id = task.split(':', 1)
            task_obj = Task.objects.get(judge__judge_id=judge_id, task_id=task_id)
            __update_task_info(db, task_obj)
        except Exception as e:
            log.exception(e)


@shared_task
def update_all_tasks_info():
    db = get_db()
    log.info(f'Updating all tasks info got called')
    for task in Task.objects.all():
        try:
            __update_task_info(db, task)
        except Exception as e:
            log.exception(e)


@shared_task
def update_handles(*handles):
    db = get_db()
    log.info(f'Updating handles {handles}...')

    if handles:
        for handle in handles:
            try:
                judge_id, handle_id = handle.split(':', 1)
                handle_obj = UserHandle.objects.get(judge__judge_id=judge_id, handle=handle_id)
                __update_handle(db, handle_obj)
            except Exception as e:
                log.exception(e)


@shared_task
def update_all_handles():
    db = get_db()
    log.info(f'Updating all handles...')

    for handle in UserHandle.objects.all():
        __update_handle(db, handle)


@shared_task
def update_users(*usernames):
    db = get_db()
    log.info(f'Updating users {usernames}...')

    for username in usernames:
        try:
            user = UserProfile.objects.get(user__username=username)
            __update_user_quick(db, user)
        except Exception as e:
            log.exception(e)


@shared_task
def update_all_users():
    db = get_db()
    log.info(f'Updating all users...')
    now = timezone.now()
    for profile in UserProfile.objects.select_related('user').all():
        if not profile.user.last_login or profile.user.last_login < now - timedelta(days=21):
            log.info(f'Skipping user {profile.user.username}: too stale.')
            continue
        __update_user_quick(db, profile)
