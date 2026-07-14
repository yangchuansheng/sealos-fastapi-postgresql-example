from typing import Any

from app.api.routes import create_item, read_item
from app.models import ItemCreate


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection
        self.row: dict[str, Any] | None = None

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def execute(self, query: str, parameters: tuple[Any, ...]) -> None:
        self.connection.queries.append((query, parameters))
        if query.lstrip().startswith("INSERT"):
            self.connection.next_id += 1
            self.connection.items[self.connection.next_id] = {
                "id": self.connection.next_id,
                "name": parameters[0],
                "description": parameters[1],
            }
            self.row = self.connection.items[self.connection.next_id]
        else:
            self.row = self.connection.items.get(parameters[0])

    def fetchone(self) -> dict[str, Any] | None:
        return self.row


class FakeConnection:
    def __init__(self) -> None:
        self.items: dict[int, dict[str, Any]] = {}
        self.next_id = 0
        self.queries: list[tuple[str, tuple[Any, ...]]] = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def test_create_and_read_item() -> None:
    connection = FakeConnection()
    created = create_item(
        ItemCreate(name="synthetic-item", description="isolated-test"),
        connection,
    )
    read = read_item(created.id, connection)

    assert read == created
    assert connection.commits == 2
    assert connection.rollbacks == 0
    assert connection.queries[0][1] == ("synthetic-item", "isolated-test")
    assert connection.queries[1][1] == (created.id,)
