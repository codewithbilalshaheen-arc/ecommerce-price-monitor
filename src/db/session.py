from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.db.models import Base

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        if "already exists" in str(e).lower():
            pass
        else:
            raise

    # Auto-seed demo data if database is empty (e.g. fresh deployment)
    try:
        from src.db.seed import seed_demo_data
        seed_demo_data(force_reseed=False)
    except Exception:
        pass


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()