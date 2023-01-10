# __init__.py
import pytest
from flask import Flask
from flask.testing import FlaskClient
from game_test.app import app

@pytest.fixture
def client() -> FlaskClient:
    client: FlaskClient = app.test_client()
    return client
