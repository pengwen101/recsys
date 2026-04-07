from fastapi import HTTPException
import pandas as pd
from backend.app.model import NeuMFRecommender


async def get_user_recommendations(user_id: int, 
                                   recommender: NeuMFRecommender, 
                                   movies_df: pd.DataFrame,
                                   user_ids: list):
    
    if user_id not in user_ids:
        raise HTTPException(status_code=404, detail="User not found")
    
    recs = recommender.recommend_for_user(user_id, 10)
    for rec in recs:
        rec['movie_id'] = int(rec['movie_id'])
        rec['score'] = float(rec['score'])
        movie_df = movies_df[movies_df["movieId"]==rec['movie_id']]
        rec['title'] = movie_df['title'].iloc[0]
        rec['genres'] = movie_df['genres'].iloc[0]
        
    return {"recommendations": recs}