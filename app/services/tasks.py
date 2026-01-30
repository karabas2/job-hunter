from app.core.database import engine, Session
from app.core.models import UserPreferences, Job
from app.services.scraper_service import scrape_linkedin_jobs
from app.services.matcher_service import match_job, simple_ranking, detect_seniority
from app.services.email_service import send_job_report
from sqlmodel import select
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def run_job_process(user_id: int):
    logger.info(f"Starting job process for user {user_id}")
    
    with Session(engine) as session:
        user = session.get(UserPreferences, user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return
            
        # Mark as scanning
        user.is_scanning = True
        session.add(user)
        session.commit()
        
        try:
            # 1. Scrape jobs
            new_jobs_data = await scrape_linkedin_jobs(user.linkedin_search_url)
            
            keywords = [k.strip() for k in user.keywords.split(',')]
            exclude = [k.strip() for k in user.exclude_keywords.split(',')] if user.exclude_keywords else []
            target_status = user.target_status or "Student"
            
            matched_jobs = []
            
            for data in new_jobs_data:
                statement = select(Job).where(Job.linkedin_job_id == data['linkedin_job_id'])
                existing_job = session.exec(statement).first()
                
                if not existing_job:
                    # Use description for matching if available, else title
                    full_text = data.get('description', f"{data['title']} @ {data['company']}")
                    
                    is_match = match_job(full_text, keywords, exclude, target_status)
                    
                    if is_match:
                        seniority = detect_seniority(full_text)
                        
                        score = simple_ranking(data, keywords)
                        
                        # Create save data without the massive description
                        save_data = {k: v for k, v in data.items() if k != 'description'}
                        
                        job = Job(
                            **save_data,
                            match_score=score,
                            seniority_requirement=seniority,
                            is_reported=False
                        )
                        session.add(job)
                        matched_jobs.append(job)
            
            session.commit()
            
            # 2. Prepare Report
            if matched_jobs:
                logger.info(f"Report: Found {len(matched_jobs)} matches for user {user.email}")
                send_job_report(user.email, matched_jobs)
                for job in matched_jobs:
                    job.is_reported = True
                session.commit()
            else:
                logger.info(f"No new matches found for user {user.email}")
        except Exception as e:
            logger.error(f"Error during job process: {e}")
            session.rollback()
            # We don't re-raise here so the finally block can clear the scanning status
        finally:
            # Always mark as finished
            user.is_scanning = False
            session.add(user)
            session.commit()
