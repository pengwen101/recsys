from pydantic import BaseModel
from typing import List

class Movie(BaseModel):
    movie_id: int
    title: str
    genres: List[str]
    score: float
    
class RecommendationResponse(BaseModel):
    recommendations: List[Movie]