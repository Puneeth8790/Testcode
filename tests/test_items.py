import pytest


def test_create_item(client):
    """Test creating a new task item successfully."""
    payload = {
        "title": "Design Database Schema",
        "description": "Create PostgreSQL relational schema using SQLAlchemy 2.0",
        "priority": "high",
        "status": "in_progress"
    }
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["priority"] == "high"
    assert data["status"] == "in_progress"
    assert "id" in data
    assert "created_at" in data


def test_create_item_validation_error(client):
    """Test payload validation when creating an item with empty title."""
    payload = {
        "title": "",
        "description": "Invalid item with empty title"
    }
    response = client.post("/api/v1/items", json=payload)
    assert response.status_code == 422


def test_read_items(client):
    """Test reading items list with filters."""
    # Create sample items
    client.post("/api/v1/items", json={"title": "Task 1", "priority": "high", "status": "pending"})
    client.post("/api/v1/items", json={"title": "Task 2", "priority": "low", "status": "completed"})

    # Fetch all items
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Filter by status
    response_pending = client.get("/api/v1/items?status=pending")
    assert response_pending.status_code == 200
    assert len(response_pending.json()) == 1
    assert response_pending.json()[0]["title"] == "Task 1"

    # Search filter
    response_search = client.get("/api/v1/items?search=Task 2")
    assert response_search.status_code == 200
    assert len(response_search.json()) == 1
    assert response_search.json()[0]["title"] == "Task 2"


def test_read_item_by_id(client):
    """Test fetching a specific item by ID."""
    create_resp = client.post("/api/v1/items", json={"title": "Specific Task"})
    item_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Task"


def test_read_item_not_found(client):
    """Test fetching a non-existent item returns 404."""
    response = client.get("/api/v1/items/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_item(client):
    """Test updating an existing item."""
    create_resp = client.post("/api/v1/items", json={"title": "Old Title", "status": "pending"})
    item_id = create_resp.json()["id"]

    update_payload = {"title": "New Title", "status": "completed"}
    update_resp = client.put(f"/api/v1/items/{item_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["title"] == "New Title"
    assert updated_data["status"] == "completed"


def test_delete_item(client):
    """Test deleting an item."""
    create_resp = client.post("/api/v1/items", json={"title": "Task to Delete"})
    item_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/items/{item_id}")
    assert delete_resp.status_code == 200

    # Verify deletion
    get_resp = client.get(f"/api/v1/items/{item_id}")
    assert get_resp.status_code == 404


def test_read_item_stats(client):
    """Test item statistics calculations."""
    client.post("/api/v1/items", json={"title": "High Task 1", "priority": "high", "status": "pending"})
    client.post("/api/v1/items", json={"title": "High Task 2", "priority": "high", "status": "in_progress"})
    client.post("/api/v1/items", json={"title": "Normal Task", "priority": "medium", "status": "completed"})

    stats_resp = client.get("/api/v1/items/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total"] == 3
    assert stats["pending"] == 1
    assert stats["in_progress"] == 1
    assert stats["completed"] == 1
    assert stats["high_priority"] == 2
