from backend.main import app
from backend.app.dependencies import get_recommendation, get_movies_detail
from fastapi.testclient import TestClient
import pandas as pd

class MockNeuMFRecommender:
    def recommend_for_user(self, userId: int, k: int=10) -> list[dict]:
        return [{
                    "movie_id": 1,
                    "score": 0.9
                }]

def mock_get_movies_detail() -> pd.DataFrame:
    return pd.DataFrame({
        "movieId": [1],
        "title": ["Toy Story (1995)"],
        "genres": [["Adventure", "Animation", "Children"]]
    })

app.dependency_overrides[get_recommendation] = MockNeuMFRecommender
app.dependency_overrides[get_movies_detail] = mock_get_movies_detail

client = TestClient(app)

def test_existing_user_returns_recommendations():
    response = client.get("/recommend/user/42")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    
def test_recommendations_have_required_fields():
    response = client.get("/recommend/user/42")
    assert response.status_code == 200
    recommendation = response.json()['recommendations'][0]
    assert "movie_id" in recommendation
    assert "title" in recommendation
    assert "genres" in recommendation
    assert "score" in recommendation
    
def test_existing_user_not_found_returns_404():
    response = client.get("/recommend/user/99999")
    assert response.status_code == 404