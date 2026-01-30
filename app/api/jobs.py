from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.models import UserPreferences, Job
from app.services.tasks import run_job_process
from typing import List

router = APIRouter()

@router.get("/users/{user_id}", response_model=UserPreferences)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(UserPreferences, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}", response_model=UserPreferences)
def update_user(user_id: int, updated_data: dict, session: Session = Depends(get_session)):
    user = session.get(UserPreferences, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in updated_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
            
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/status/{user_id}")
def get_status(user_id: int, session: Session = Depends(get_session)):
    user = session.get(UserPreferences, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"is_scanning": user.is_scanning}

@router.post("/trigger/{user_id}")
async def trigger_report(user_id: int, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    user = session.get(UserPreferences, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Run in background to avoid timeout
    background_tasks.add_task(run_job_process, user_id)
    return {"message": "Job process started in background"}

@router.get("/jobs", response_model=List[Job])
def get_jobs(session: Session = Depends(get_session)):
    return session.exec(select(Job)).all()
