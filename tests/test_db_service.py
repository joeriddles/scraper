import os

import pytest
from app.db_service import DbService
from app.models.item import Item
from sqlmodel import SQLModel, create_engine
from sqlmodel.orm.session import Session


class TestBase:
    @pytest.fixture(autouse=True)
    def mock_db(self):
        self._remove_db()
        test_engine = create_engine("sqlite:///test.db")
        SQLModel.metadata.create_all(test_engine)
        session = Session(test_engine)
        self.service: DbService[Item] = DbService(Item, create_session_=lambda: session)
        yield
        session.close_all()
        self._remove_db()

    def _remove_db(self):
        if os.path.exists("test.db"):
            os.remove("test.db")


class TestDbService(TestBase):
    def test__db_service__add_item(self):
        item = Item(item_id="item_id", url="url", text="text")
        self.service.add(item)
        assert self.service.get(Item.item_id == "item_id") == item

    def test__db_service__update_item(self):
        item = Item(item_id="item_id", url="url", text="text")
        self.service.add(item)

        update = Item(item_id="item_id", url="new url", text="new text")
        actual = self.service.update(Item.item_id == "item_id", update)

        assert actual.item_id == "item_id"
        assert actual.url == "new url"
        assert actual.text == "new text"
