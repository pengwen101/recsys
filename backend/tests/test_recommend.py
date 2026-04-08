from backend.main import app
from fastapi.testclient import TestClient
import pandas as pd
import pytest
from backend.app import state
import scipy.sparse as sp
import numpy as np

class MockNeuMFRecommender:
    def recommend_for_user(self, userId: int, k: int=10) -> list[dict]:
        return [{
                    "movie_id": 1,
                    "score": 0.9
                }]

@pytest.fixture(autouse=True)
def mock_state(monkeypatch):
    monkeypatch.setattr(state, "movies_df", pd.DataFrame({
        "movieId": [1, 2],
        "title":   ["Toy Story (1995)", "Jumanji (1995)"],
        "genres":  [["Animation"], ["Adventure"]],
        "popularity_score": [3.5, 4.0],
        "overview": ["lalala", "A game comes to life"],
        "keywords": [["keyword 1", "keyword 2"], ["keyword 3"]],
        "casts": [[{"id": "id 1", "name": "cast 1"}], [{"id": "id 2", "name": "cast 2"}]],
        "directors": [[{"id": "id 1", "name": "director 1"}], [{"id": "id 2", "name": "director 2"}]],
        "poster_url": ["someurl", "someurl2"],
    }))
    monkeypatch.setattr(state, "neumf_bce_rec", MockNeuMFRecommender())
    monkeypatch.setattr(state, "user_ids", [42, 43])
    
    dummy_matrix = sp.csr_matrix(np.array([
        [1.0], 
        [0.8]
    ]))
    
    monkeypatch.setattr(state, "keywords_matrix", dummy_matrix)
    monkeypatch.setattr(state, "genres_matrix", dummy_matrix)
    monkeypatch.setattr(state, "directors_matrix", dummy_matrix)
    monkeypatch.setattr(state, "casts_matrix", dummy_matrix)
 
    monkeypatch.setattr(state, "matrix_mapping", {
        "id_to_row": {1: 0, 2: 1},
        "row_to_id": {0: 1, 1: 2}
    })

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
    assert "movie" in recommendation
    assert "score" in recommendation
    assert "reason" in recommendation
    assert "movie_id" in recommendation['movie']
    assert "title" in recommendation['movie']
    assert "overview" in recommendation['movie']
    assert "keywords" in recommendation['movie']
    assert "directors" in recommendation['movie']
    assert "casts" in recommendation['movie']
    assert "genres" in recommendation['movie']
    assert "poster_url" in recommendation['movie']
    
def test_existing_user_not_found_returns_404(client):
    response = client.get("/recommend/user/99999")
    assert response.status_code == 404
    
def test_popular_return_recommendations(client):
    response = client.get("/recommend/popular", params={"k": 5})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    
def test_popular_recommendations_have_required_fields(client):
    response = client.get("/recommend/popular",params= {"k": 5})
    assert response.status_code == 200
    recommendation = response.json()['recommendations'][0]
    assert "movie" in recommendation
    assert "score" in recommendation
    assert "reason" in recommendation
    assert "movie_id" in recommendation['movie']
    assert "title" in recommendation['movie']
    assert "overview" in recommendation['movie']
    assert "keywords" in recommendation['movie']
    assert "directors" in recommendation['movie']
    assert "casts" in recommendation['movie']
    assert "genres" in recommendation['movie']
    assert "poster_url" in recommendation['movie']
    
    
def test_similar_return_recommendations(client):
    response = client.get("/recommend/similar/1", params={"k": 5})
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    
def test_similar_recommendations_have_required_fields(client):
    response = client.get("/recommend/similar/1",params= {"k": 5})
    assert response.status_code == 200
    recommendation = response.json()['recommendations'][0]
    assert "movie" in recommendation
    assert "score" in recommendation
    assert "reason" in recommendation
    assert "movie_id" in recommendation['movie']
    assert "title" in recommendation['movie']
    assert "overview" in recommendation['movie']
    assert "keywords" in recommendation['movie']
    assert "directors" in recommendation['movie']
    assert "casts" in recommendation['movie']
    assert "genres" in recommendation['movie']
    assert "poster_url" in recommendation['movie']
    
def test_similar_item_not_found_returns_404(client):
    response = client.get("/recommend/similar/99999", params= {"k": 5})
    assert response.status_code == 404