from sqlmodel import Session, select
from app.database import engine, init_db
from app.models import UserPreferences
from app.tasks import run_job_process
import asyncio

async def test_run():
    init_db()
    
    cv_text = """
    Gülbahar Karabaş
    Summary: Software-oriented Computer Engineering student with hands-on experience in backend development, relational databases, and authentication-based systems.
    Experience: Research Assistant (TUBITAK), DevOps Intern (Kuika), Cloud & DevOps Intern (Otokoç), Automation Developer (Biletwise).
    Technical Skills: Python, Java, Node.js, SQL, React, MySQL, Docker, Jenkins, Selenium, Playwright, Pandas, NumPy.
    """
    
    with Session(engine) as session:
        # Check if test user exists
        user = session.exec(select(UserPreferences).where(UserPreferences.email == "gulbaharkrbs@gmail.com")).first()
        
        if not user:
            user = UserPreferences(
                email="gulbaharkrbs@gmail.com",
                linkedin_search_url="https://www.linkedin.com/jobs/search/?keywords=Backend%20Developer&location=Turkey",
                keywords="Python, Node.js, Backend, SQL, Docker",
                exclude_keywords="PHP, .NET",
                cv_text=cv_text.strip(),
                report_times="09:00,18:00"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Created test user: {user.email}")
        else:
            print(f"User {user.email} already exists.")

        print("Starting manual job process for test user...")
        await run_job_process(user.id)

if __name__ == "__main__":
    asyncio.run(test_run())
