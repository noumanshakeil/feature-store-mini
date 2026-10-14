import pytest

@pytest.mark.asyncio
async def test_online_features(client):
    await client.post("/api/entities", json={"name": "user"})
    await client.post("/api/defs", json={"entity_name": "user", "name": "login_count_7d", "lineage": "events"})
    await client.post(
        "/api/values",
        json={"entity_name": "user", "entity_key": "u1", "feature_name": "login_count_7d", "value": 4},
    )
    r = await client.get("/api/online", params={"entity_name": "user", "entity_key": "u1"})
    assert r.status_code == 200
    assert r.json()["features"]["login_count_7d"] == 4
