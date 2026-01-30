from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started.")

def schedule_job_report(user_id: int, times: str, func):
    # times is comma separated "HH:MM"
    for time_str in times.split(','):
        hour, minute = time_str.split(':')
        job_id = f"report_{user_id}_{hour}_{minute}"
        
        # Remove existing job if any
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            
        scheduler.add_job(
            func,
            CronTrigger(hour=hour, minute=minute),
            id=job_id,
            args=[user_id]
        )
        logger.info(f"Scheduled report for user {user_id} at {time_str}")
