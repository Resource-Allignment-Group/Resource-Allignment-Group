import pytest
from threading import Thread
from backend.main import create_app

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="session")
def flask_server():
    app = create_app(testing=True)  # use testing=True to trigger your test DB
    print("App created")

    def run():
        # Flask default: host=127.0.0.1, port=5000
        app.run(port=5000, use_reloader=False)

    thread = Thread(target=run)
    thread.start()
    yield
    thread.join(timeout=1)
