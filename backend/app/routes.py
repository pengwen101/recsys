from fastapi import APIRouter, Depends
from backend.app.dependencies import get_recommendation, get_movies_detail, get_user_ids, get_keywords_matrix, get_genres_matrix, get_directors_matrix, get_casts_matrix, get_matrix_mapping
import pandas as pd
from backend.app.model import NeuMFRecommender
from backend.app.schemas import RecommendationResponse, UserIdsResponse
from backend.app import services

router = APIRouter()

@router.get("/recommend/user/{user_id}", response_model=RecommendationResponse)
async def get_user_recommendations(user_id: int, 
                                   recommender: NeuMFRecommender = Depends(get_recommendation), 
                                   movies_df: pd.DataFrame = Depends(get_movies_detail),
                                   user_ids: list = Depends(get_user_ids)):
        
    return await services.get_user_recommendations(user_id, recommender, movies_df, user_ids)


@router.get("/recommend/popular", response_model=RecommendationResponse)
async def get_popular_recommendations(k: int, movies_df: pd.DataFrame = Depends(get_movies_detail)):
    return await services.get_popular_recommendations(k, movies_df)

@router.get("/recommend/similar/{item_id}", response_model=RecommendationResponse)
async def get_similar_recommendations(item_id: int, k: int, movies_df: pd.DataFrame = Depends(get_movies_detail),
                                      keywords_matrix = Depends(get_keywords_matrix), genres_matrix = Depends(get_genres_matrix),
                                      directors_matrix = Depends(get_directors_matrix), casts_matrix = Depends(get_casts_matrix),
                                      matrix_mapping = Depends(get_matrix_mapping)):
    
    return await services.get_similar_recommendations(item_id, k, movies_df, keywords_matrix, genres_matrix, directors_matrix, casts_matrix, matrix_mapping)
    