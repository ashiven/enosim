import os
from sqlite3 import Connection, Row
from unittest.mock import Mock, patch

from enosimulator.backend.app import FlaskApp


def test_backend_init_and_run(backend_container):
    with patch("backend.app.FlaskApp.init_db") as mock_init_db:
        with patch("backend.app.Api.add_resource") as mock_add_resource:
            flask_app = backend_container.flask_app()
    flask_app.app = Mock()

    flask_app.run()

    assert mock_init_db.call_count == 1
    mock_add_resource.call_count == 7

    flask_app.app.run.assert_called_once_with(host="0.0.0.0", debug=False)


def test_backend_init_db(mock_fs, backend_path, backend_container):
    backend_container.reset_singletons()
    with patch("backend.app.FlaskApp.init_db") as mock_init_db:
        flask_app = backend_container.flask_app()
    flask_app.app = Mock()
    flask_app.path = backend_path

    mock_fs.add_real_file(backend_path + "/schema.sql")

    with patch("sqlite3.connect") as mock_connect:
        flask_app.init_db()

    assert mock_init_db.call_count == 1

    assert mock_connect.call_count == 1
    mock_connect.return_value.executescript.assert_called_once_with(
        open(backend_path + "/schema.sql").read()
    )
    assert mock_connect.return_value.commit.call_count == 1
    assert mock_connect.return_value.close.call_count == 1


def test_backend_delete_db(mock_fs, backend_container):
    backend_container.reset_singletons()
    with patch("backend.app.FlaskApp.init_db") as mock_init_db:
        flask_app = backend_container.flask_app()
    flask_app.app = Mock()

    mock_fs.create_file("database.db")
    assert os.path.exists("database.db")

    flask_app.delete_db()

    assert mock_init_db.call_count == 1
    assert not os.path.exists("database.db")


def test_backend_get_db_connection():
    with patch("sqlite3.connect") as mock_connect:
        FlaskApp.get_db_connection()
    mock_connect.assert_called_once_with("database.db")

    conn = FlaskApp.get_db_connection()

    assert isinstance(conn, Connection)
    assert conn.row_factory == Row


def test_backend_db_insert_values():
    test_table_name = "test_table"
    test_data = {"test_key": "test_value"}

    with patch("sqlite3.connect") as mock_connect:
        query, params = FlaskApp.db_insert_values(test_table_name, test_data)

    mock_connect.assert_called_once_with("database.db")

    assert query == "INSERT INTO test_table(test_key) VALUES (?)"
    assert params == ("test_value",)
