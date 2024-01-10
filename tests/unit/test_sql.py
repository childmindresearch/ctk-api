"""Tests for the SQL module."""
from unittest import mock

import pytest
import pytest_mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ctk_api.core import config
from ctk_api.microservices import sql

settings = config.get_settings()
POSTGRES_USER = settings.POSTGRES_USER
POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
POSTGRES_URL = settings.POSTGRES_URL


@pytest.fixture()
def mock_engine(mocker: pytest_mock.MockFixture) -> mock.MagicMock:
    """Fixture for creating a mocked database engine."""
    return mocker.Mock(spec=create_engine)


@pytest.fixture()
def mock_session_factory(
    mocker: pytest_mock.MockFixture,
    mock_engine: mock.MagicMock,
) -> mock.MagicMock:
    """Fixture for creating a mocked session factory."""
    session_factory = mocker.patch("sqlalchemy.orm.sessionmaker")
    session_factory.return_value = mocker.Mock(spec=sessionmaker)
    scoped_session_factory = mocker.patch("sqlalchemy.orm.scoped_session")
    scoped_session_factory.return_value = session_factory.return_value
    return scoped_session_factory


@pytest.fixture()
def database_instance(
    mocker: pytest_mock.MockFixture,
    mock_engine: mock.MagicMock,
    mock_session_factory: mock.MagicMock,
) -> sql.Database:
    """Fixture for creating a Database instance with mocked dependencies."""
    mocker.patch("sqlalchemy.orm.declarative_base")
    db = sql.Database()
    db.engine = mock_engine
    db.session_factory = mock_session_factory
    return db


def test_create_database(
    mocker: pytest_mock.MockFixture,
    database_instance: sql.Database,
) -> None:
    """Test that the database schema is created."""
    mock_create_all = mocker.patch.object(sql.Base.metadata, "create_all")

    database_instance.create_database()

    mock_create_all.assert_called_once_with(database_instance.engine)


@pytest.mark.parametrize(
    ("env", "expected_url"),
    [
        ("testing", "sqlite:///tests/test.sqlite"),
        (
            "production",
            f"postgresql://{POSTGRES_USER.get_secret_value()}:{POSTGRES_PASSWORD.get_secret_value()}@{POSTGRES_URL}/ctk",
        ),
    ],
)
def test_get_db_url(
    mocker: pytest_mock.MockFixture,
    env: str,
    expected_url: str,
) -> None:
    """Test that the correct database URL is returned for different environments."""
    mocker.patch("ctk_api.microservices.sql.ENVIRONMENT", env)

    actual_url = sql.Database.get_db_url()

    assert actual_url == expected_url, "The correct database URL should be returned."


def test_get_session(mocker: pytest_mock.MockFixture) -> None:
    """Test that a session is provided properly."""
    mock_session = mocker.MagicMock()
    mock_scoped_session = mocker.patch("sqlalchemy.orm.scoped_session")
    mock_scoped_session.return_value = mocker.MagicMock(return_value=mock_session)
    db_instance = sql.Database()
    db_instance.session_factory = mock_scoped_session

    session_generator = sql.get_session()
    session = next(session_generator)

    assert session == mock_session
