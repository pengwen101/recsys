from fastapi import APIRouter, Depends
from backend.app.dependencies import get_recommendation, get_movies_detail, get_user_ids
import pandas as pd
from backend.app.model import NeuMFRecommender
from backend.app.schemas import RecommendationResponse
from backend.app import services

router = APIRouter()

@router.get("/recommend/user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(user_id: int, 
                                   recommender: NeuMFRecommender = Depends(get_recommendation), 
                                   movies_df: pd.DataFrame = Depends(get_movies_detail),
                                   user_ids: list = Depends(get_user_ids)):
        
    return await services.get_user_recommendations(user_id, recommender, movies_df, user_ids)