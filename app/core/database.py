from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:userpassword@localhost:3306/job_agent")

engine = create_engine(DATABASE_URL)

import time

def init_db():
    retries = 5
    while retries > 0:
        try:
            SQLModel.metadata.create_all(engine)
            return
        except Exception as e:
            print(f"Database not ready yet... {retries} retries left. Error: {e}")
            retries -= 1
            time.sleep(5)
    raise Exception("Could not connect to database after multiple retries.")

def get_session():
    with Session(engine) as session:
        yield session
