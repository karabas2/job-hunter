import asyncio
from app.database import init_db, Session, engine
from app.models import UserPreferences
from app.tasks import run_job_process
from sqlmodel import select

async def main():
    print("Initializing Database...")
    init_db()
    
    cv_text = """Gülbahar Karabaş - Backend Engineer. Skills: Python, Node.js, Docker, SQL."""
    
    with Session(engine) as session:
        user = session.exec(select(UserPreferences).where(UserPreferences.email == "gulbaharkrbs@gmail.com")).first()
        if not user:
            user = UserPreferences(
                email="gulbaharkrbs@gmail.com",
                linkedin_search_url="https://www.linkedin.com/jobs/search/?keywords=Backend%20Developer&location=Turkey",
                keywords="Python, Node.js, Backend, Docker",
                cv_text=cv_text
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"User created: {user.email}")
        
        print(f"Triggering job search for {user.email}...")
        await run_job_process(user.id)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
