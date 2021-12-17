from __future__ import annotations

from typing import Callable, Generic, TypeVar

import sqlmodel
from sqlalchemy.exc import DatabaseError
from sqlmodel import Session, SQLModel

from app import db

DT = TypeVar("DT", bound=SQLModel)


class DbService(Generic[DT]):
    """Generic SQLModel CRUS service"""

    session = None

    def __init__(
        self,
        model_class: DT,
        get_pk: Callable[[], str] = None,
        create_session_: Callable[[], Session] = None,
    ):
        self.model_class: DT = model_class
        self._get_pk = get_pk or self._get_pk
        self._create_session = create_session_ or db.create_session

    def __enter__(self) -> DbService:
        self.session = self._create_session()
        return self

    def __exit__(self, _, __, ___) -> None:
        self.session.close()

    def get(self, where) -> DT:
        """Get item for primary key value"""
        session = self.session or self._create_session()
        stmt = sqlmodel.select(self.model_class).where(where)
        item = session.exec(stmt).one()
        return item

    def list(self) -> list[DT]:
        session = self.session or self._create_session()
        stmt = sqlmodel.select(self.model_class)
        items = session.exec(stmt)
        items = list(items)
        return items

    def exists(self, where) -> bool:
        """Check if item with item_id exists"""
        session = self.session or self._create_session()
        stmt = sqlmodel.select(self.model_class).where(where)
        item = session.exec(stmt).first()
        return item is not None

    def add(self, model: DT) -> DT:
        """Adds item to database and returns it"""
        session = self.session or self._create_session()
        session.add(model)
        self._commit(session)
        session.refresh(model)
        return model

    def update(self, where, update: DT) -> DT:
        """Updates item in database. Returns updated item"""
        session = self.session or self._create_session()
        model = self.get(where)
        for key, update_value in update.dict(exclude_unset=True).items():
            setattr(model, key, update_value)
        session.add(model)
        self._commit(session)
        session.refresh(model)
        return model

    def add_or_update(self, where: str, model: DT) -> DT:
        """Adds item to database if it does not exist, else updates it"""
        if self.exists(where):
            return self.update(where, model)
        else:
            return self.add(model)

    def _get_pk(self) -> str:
        """Gets default name primary key of class"""
        class_name = self.model_class.__name__.casefold()
        pk = f"{class_name}_id"
        return pk

    def _commit(self, session: sqlmodel.Session) -> None:
        """
        Tries committing the database session,
            automatically does a rollback if an error is raised
        """
        try:
            session.commit()
        except DatabaseError:
            session.rollback()
            raise
