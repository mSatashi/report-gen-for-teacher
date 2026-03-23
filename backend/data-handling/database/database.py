from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# temporary, dummy will need to replace it once postgreSQL is set up
DATABASE_URL = "postgresql://postgres:password_anda@localhost:5432/db_pendidikan"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()