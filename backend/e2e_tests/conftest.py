# backend/end-to-end-tests/conftest.py
import pytest
from threading import Thread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from main import create_app
from werkzeug.serving import make_server

@pytest.fixture(scope="session")
def flask_server():
    app = create_app(testing=True)
    print("App created")

    server = make_server("127.0.0.1", 5000, app)
    thread = Thread(target=server.serve_forever)
    thread.start()
    
    yield  # tests run here

    server.shutdown()  # stop the server after tests
    thread.join()

@pytest.fixture(scope="session")
def driver(flask_server):  # depends on flask_server
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:3000"
