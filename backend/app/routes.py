from fastapi import APIRouter, Depends, HTTPException
from backend.app.dependencies import get_recommendation, get_movies_detail, get_user_ids
import pandas as pd
from backend.app.model import NeuMFRecommender
from backend.app.schemas import RecommendationResponse

router = APIRouter()

@router.get("/recommend/user/{user_id}")
async def get_user_recommendations(user_id: int, 
                                   recommender: NeuMFRecommender = Depends(get_recommendation), 
                                   movies_df: pd.DataFrame = Depends(get_movies_detail),
                                   user_ids: list = Depends(get_user_ids),
                                   response_model=RecommendationResponse):
    
    if user_id not in user_ids:
        raise HTTPException(status_code=404, detail="User not found")
    
    recs = recommender.recommend_for_user(user_id, 10)
    for rec in recs:
        rec['movie_id'] = int(rec['movie_id'])
        rec['score'] = float(rec['score'])
        movie_df = movies_df[movies_df["movieId"]==rec['movie_id']]
        rec['title'] = movie_df['title'].iloc[0]
        rec['genres'] = movie_df['genres']
        
    return {"recommendations": recs}