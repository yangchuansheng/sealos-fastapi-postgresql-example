import importlib.util
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect



MIGRATION_PATH = Path(__file__).parents[1] / "alembic/versions/0001_create_items.py"
migration_spec = importlib.util.spec_from_file_location(
    "controlled_items_migration", MIGRATION_PATH
)
if migration_spec is None or migration_spec.loader is None:
    raise RuntimeError("unable to load controlled migration")
migration = importlib.util.module_from_spec(migration_spec)
migration_spec.loader.exec_module(migration)
upgrade = migration.upgrade
downgrade = migration.downgrade


def test_alembic_upgrade_and_downgrade(tmp_path: Path) -> None:
    database_path = tmp_path / "migration.db"
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    assert "items" in inspect(engine).get_table_names()
    engine.dispose()

    command.downgrade(config, "base")
    engine = create_engine(f"sqlite:///{database_path}")
    assert "items" not in inspect(engine).get_table_names()
    engine.dispose()

    assert upgrade.__name__ == "upgrade"
    assert downgrade.__name__ == "downgrade"
