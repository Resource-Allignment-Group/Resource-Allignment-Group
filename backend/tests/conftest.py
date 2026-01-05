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
    app = create_app(testing=True) 
    print("App created")

    def run():
        app.run(port=5000, use_reloader=False)

    thread = Thread(target=run)
    thread.start()
    yield
    thread.join(timeout=1)
