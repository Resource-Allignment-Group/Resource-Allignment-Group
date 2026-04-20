import time
import psutil
import os
import pytest
from bson import ObjectId
from helpers import hash_password

# Backend Performance & System Tests
# Reuses the client, seed_db, login_user, and login_admin fixtures from conftest.py

@pytest.fixture
def large_seed_db(client):
    """Extends the standard seed_db with 200 equipment items and 100 users
    to give performance tests a realistic amount of data to work with."""
    db = client.application.db
    hashed = hash_password("Test_Pass1!")

    db.users_db.insert_one({
        "_id": ObjectId("112233445566778899001121"),
        "email": "admin@gmail.com",
        "password": hashed,
        "name": "Test Admin",
        "phone": "1111111111",
        "role": "a",
        "checked_out_equipment": [],
        "inbox": [],
        "position": None,
    })

    users = [
        {
            "_id": ObjectId(),
            "email": f"perfuser{i}@example.com",    # Different emails
            "password": hashed,
            "name": f"Perf User {i}",   # Different names
            "phone": f"555{i:07d}",     # Different phone numbers
            "role": "u",
            "checked_out_equipment": [],
            "inbox": [],
            "position": "Researcher",
        }
        for i in range(100)
    ]
    db.users_db.insert_many(users)

    equipment = [
        {
            "_id": ObjectId(),
            "name": f"Tractor {i}",     # Different names
            "class": "Tractor",
            "farm": "Aroostook",
            "make": "John Deere",
            "year": 2020,
            "model": f"Model-{i}",  # Different model numbers
            "use": "Farming",
            "images": [],
            "reports": [],
            # Every 5th item is checked out, every 20th is damaged, every 10th is unavailable
            "checked_out": i % 5 == 0,
            "damaged": i % 20 == 0,
            "unavailable": i % 10 == 0,
            "description": f"Test tractor number {i}",
            "replacement_cost": 50000,
            "display_image": None,
        }
        for i in range(200)
    ]
    db.equipment_db.insert_many(equipment)
    return db

# Admin fixture just for the larger sample database
@pytest.fixture
def large_admin(client, large_seed_db):
    """Logs in as admin against the large dataset."""
    client.post("/authenticate", json={"email": "admin@gmail.com", "password": "Test_Pass1!"})
    return client

### DB layer benchmarks -----------------------------------------

def test_get_all_equipment_speed(benchmark, client, large_seed_db):
    """Benchmark: fetching all 200 equipment items from the DB."""
    db = client.application.db
    result = benchmark(db.get_all_equipment)
    assert len(result) == 200

def test_get_all_users_speed(benchmark, client, large_seed_db):
    """Benchmark: fetching all 101 users (100 perf users + 1 admin) from the DB."""
    db = client.application.db
    result = benchmark(db.get_all_users)
    assert len(result) == 101

def test_get_equipment_by_id_speed(benchmark, client, large_seed_db):
    """Benchmark: single equipment lookup by ID should be very fast."""
    db = client.application.db
    equip_id = db.get_all_equipment()[0].id
    result = benchmark(db.get_equipment_by_id, equip_id)
    assert result is not None

def test_dashboard_info_speed(benchmark, client, large_seed_db):
    """Benchmark: dashboard count aggregation across 200 equipment items."""
    db = client.application.db
    total, available, used, damaged, unavailable = benchmark(db.get_dashboard_info)
    assert total == 200

### Route response time benchmarks -----------------------------------------

def test_get_equipment_endpoint_speed(benchmark, large_admin):
    """/get_equipment benchmark with 200 items in the DB."""
    res = benchmark(large_admin.get, "/get_equipment")
    assert res.status_code == 200
    assert len(res.get_json()["equip_list"]) == 200

def test_search_equipment_speed(benchmark, large_admin):
    """/search_equipment fuzzy search benchmark across 200 items."""
    def search():
        return large_admin.post("/search_equipment", json={"query": "Tractor"})
    res = benchmark(search)
    assert res.get_json()["result"] is True

def test_get_dashboard_info_endpoint_speed(benchmark, large_admin):
    """/get_dashboard_info benchmark with 200 equipment items."""
    res = benchmark(large_admin.get, "/get_dashboard_info")
    assert res.get_json()["result"] is True

### Time limit assertions -----------------------------------------

def test_get_equipment_under_3_seconds(large_admin):
    # Max response time for loading all equipment
    MAX_SECONDS = 3.0
    start = time.perf_counter()
    res = large_admin.get("/get_equipment")
    elapsed = time.perf_counter() - start
    assert res.status_code == 200
    assert elapsed < MAX_SECONDS, f"/get_equipment took {elapsed:.2f}s — limit is {MAX_SECONDS}s"

def test_authenticate_under_1_second(client, large_seed_db):
    # Max time for a login request (bcrypt is slow)
    MAX_SECONDS = 1.0
    start = time.perf_counter()
    res = client.post("/authenticate", json={"email": "admin@gmail.com", "password": "Test_Pass1!"})
    elapsed = time.perf_counter() - start
    assert res.get_json()["result"] is True
    assert elapsed < MAX_SECONDS, f"/authenticate took {elapsed:.2f}s — limit is {MAX_SECONDS}s"

def test_search_under_2_seconds(large_admin):
    # Max time for a multi-word fuzzy search across 200 items
    MAX_SECONDS = 2.0
    start = time.perf_counter()
    res = large_admin.post("/search_equipment", json={"query": "John Deere Tractor"})
    elapsed = time.perf_counter() - start
    assert elapsed < MAX_SECONDS, f"/search_equipment took {elapsed:.2f}s — limit is {MAX_SECONDS}s"

def test_dashboard_under_1_second(large_admin):
    # Max time for the dashboard summary endpoint
    MAX_SECONDS = 1.0
    start = time.perf_counter()
    res = large_admin.get("/get_dashboard_info")
    elapsed = time.perf_counter() - start
    assert elapsed < MAX_SECONDS, f"/get_dashboard_info took {elapsed:.2f}s — limit is {MAX_SECONDS}s"

### Memory checks -----------------------------------------

def test_get_all_equipment_memory_stable(client, large_seed_db):
    """Fetching 200 equipment items should not cause a large memory spike."""
    db = client.application.db
    process = psutil.Process(os.getpid())
    before_mb = process.memory_info().rss / 1024 / 1024
    db.get_all_equipment()
    after_mb = process.memory_info().rss / 1024 / 1024

    delta_mb = after_mb - before_mb
    # Max memory growth for a single DB fetch of 200 items
    MAX_DELTA_MB = 50
    assert delta_mb < MAX_DELTA_MB, f"Memory grew {delta_mb:.1f}MB — limit is {MAX_DELTA_MB}MB"

# These reuse the normal seed_db and login_admin fixtures directly,
# so they run at typical data volume rather than the large dataset.

def test_get_equipment_speed_small_seed(benchmark, login_admin):
    """Benchmark /get_equipment against the standard 5-item seed."""
    res = benchmark(login_admin.get, "/get_equipment")
    assert res.status_code == 200
    assert len(res.get_json()["equip_list"]) == 5

def test_dashboard_speed_small_seed(benchmark, login_admin):
    """Benchmark /get_dashboard_info against the standard seed."""
    res = benchmark(login_admin.get, "/get_dashboard_info")
    assert res.get_json()["result"] is True