from backend.main import app
from fastapi.testclient import TestClient
import pandas as pd
import pytest
from backend.app import state

class MockNeuMFRecommender:
    def recommend_for_user(self, userId: int, k: int=10) -> list[dict]:
        return [{
                    "movie_id": 1,
                    "score": 0.9
                }]

@pytest.fixture(autouse=True)
def mock_state(monkeypatch):
    monkeypatch.setattr(state, "movies_genre_df", pd.DataFrame({
        "movieId": [1],
        "title":   ["Toy Story (1995)"],
        "genres":  [["Animation"]]
    }))
    monkeypatch.setattr(state, "neumf_bce_rec", MockNeuMFRecommender())
    monkeypatch.setattr(state, "user_ids", [42, 43])

@pytest.fixture
def client():
    return TestClient(app)

def test_existing_user_returns_recommendations(client):
    response = client.get("/recommend/user/42")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    
def test_recommendations_have_required_fields(client):
    response = client.get("/recommend/user/42")
    assert response.status_code == 200
    recommendation = response.json()['recommendations'][0]
    assert "movie_id" in recommendation
    assert "title" in recommendation
    assert "genres" in recommendation
    assert "score" in recommendation
    
def test_existing_user_not_found_returns_404(client):
    response = client.get("/recommend/user/99999")
    assert response.status_code == 404