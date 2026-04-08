from pydantic import BaseModel
from typing import List

class Movie(BaseModel):
    movie_id: int
    title: str
    overview: str
    genres: List[str]
    casts: List[dict]
    directors: List[dict]
    poster_url: str
    keywords: List[str]
    
class RecommendedMovie(BaseModel):
    movie: Movie
    score: float
    reason: str
    
class UserMovie(BaseModel):
    movie: Movie
    rating: float
    
class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedMovie]
    
class UserIdsResponse(BaseModel):
    user_ids: List[int]