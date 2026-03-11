from fastapi.testclient import TestClient


def test_todo_一覧取得_初期は空(client: TestClient):
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.json() == []


def test_todo_作成(client: TestClient):
    res = client.post("/api/todos", json={"title": "牛乳を買う"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "牛乳を買う"
    assert data["completed"] is False
    assert "id" in data


def test_todo_完了状態に更新(client: TestClient):
    created = client.post("/api/todos", json={"title": "本を読む"}).json()
    res = client.patch(f"/api/todos/{created['id']}", json={"completed": True})
    assert res.status_code == 200
    assert res.json()["completed"] is True


def test_todo_タイトル編集(client: TestClient):
    created = client.post("/api/todos", json={"title": "古いタイトル"}).json()
    res = client.patch(f"/api/todos/{created['id']}", json={"title": "新しいタイトル"})
    assert res.status_code == 200
    assert res.json()["title"] == "新しいタイトル"


def test_todo_削除(client: TestClient):
    created = client.post("/api/todos", json={"title": "削除するTODO"}).json()
    res = client.delete(f"/api/todos/{created['id']}")
    assert res.status_code == 204
    todos = client.get("/api/todos").json()
    assert all(t["id"] != created["id"] for t in todos)


def test_todo_存在しないidは404(client: TestClient):
    assert client.patch("/api/todos/9999", json={"completed": True}).status_code == 404
    assert client.delete("/api/todos/9999").status_code == 404
