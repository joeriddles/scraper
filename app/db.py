from sqlmodel import Session, create_engine
from sqlmodel.main import SQLModel

import app.models  # ignore unused import

engine = create_engine("sqlite:///items.db")


def init():
    SQLModel.metadata.create_all(engine)


def create_session() -> Session:
    return Session(engine)
