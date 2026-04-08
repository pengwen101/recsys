from fastapi import HTTPException
import pandas as pd
from backend.app.model import NeuMFRecommender
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.schemas import RecommendedMovie, Movie
import numpy as np


async def get_user_recommendations(user_id: int, 
                                   recommender: NeuMFRecommender, 
                                   movies_df: pd.DataFrame,
                                   user_ids: list):
    
    if user_id not in user_ids:
        raise HTTPException(status_code=404, detail="User not found")
    
    recs = recommender.recommend_for_user(user_id, 10)
    result = []
    for rec in recs:
        movie_df = movies_df[movies_df["movieId"]==rec['movie_id']]
        result.append({
            "movie": {
                "movie_id": int(rec['movie_id']),
                "title": movie_df['title'].iloc[0],
                "overview": movie_df['overview'].iloc[0],
                "genres": movie_df['genres'].iloc[0],
                "casts": movie_df['casts'].iloc[0],
                "directors": movie_df['directors'].iloc[0],
                "poster_url": movie_df['poster_url'].iloc[0],
                "keywords": movie_df['keywords'].iloc[0]
            },
            "score": float(rec['score']),
            "reason": "Liked by users with similar taste"
        })
        
    return {"recommendations": result}


async def get_popular_recommendations(k: int, movies_df: pd.DataFrame):
    top_movies_df = movies_df.sort_values(by="popularity_score", ascending=False).head(k)
    top_movies_df = top_movies_df.rename(columns={
        "popularity_score": "score",
        "movieId": "movie_id"
    })
    top_movies = top_movies_df.to_dict(orient="records")
    
    recommendations = []
    for item in top_movies:
        score = item.pop("score")
     
        rec = RecommendedMovie(
            movie=Movie(**item), 
            score=score,
            reason="Popular movies"
        )
        recommendations.append(rec)
    return {"recommendations": recommendations}

async def get_similar_recommendations(item_id: int, k: int, movies_df: pd.DataFrame, keywords_matrix, genres_matrix,
                                      directors_matrix, casts_matrix, matrix_mapping):
    
    if item_id not in movies_df['movieId'].unique():
        raise HTTPException(status_code=404, detail="Movie not found")
        
    row_idx = matrix_mapping['id_to_row'][item_id]
  
    keywords_vector = keywords_matrix.getrow(row_idx)
    genres_vector = genres_matrix.getrow(row_idx)
    directors_vector = directors_matrix.getrow(row_idx)
    casts_vector = casts_matrix.getrow(row_idx)

    keywords_sim = cosine_similarity(keywords_vector, keywords_matrix).flatten()
    genres_sim = cosine_similarity(genres_vector, genres_matrix).flatten()
    directors_sim = cosine_similarity(directors_vector, directors_matrix).flatten()
    casts_sim = cosine_similarity(casts_vector, casts_matrix).flatten()
  
    matrix_sim = np.vstack([keywords_sim, genres_sim, directors_sim, casts_sim]).T
 
    ideal_vector = np.array([[1.0, 1.0, 1.0, 1.0]])
    final_sim = cosine_similarity(ideal_vector, matrix_sim).flatten()
    
    sorted_indices = final_sim.argsort()[::-1]

    top_indices = sorted_indices[1 : k + 1]

    recommendations = []
    
    reason_map = {
        0: "Features similar keywords and themes",
        1: "Matches the genres of your picks",
        2: "Directed by your liked directors",
        3: "Stars actors from your favorite movies"
    }
    
    for idx in top_indices:
        rec_movie_id = matrix_mapping['row_to_id'][idx]
        score = float(final_sim[idx])
        movie_row = movies_df[movies_df['movieId'] == rec_movie_id]
        feature_scores = matrix_sim[idx]
        best_feature_idx = int(np.argmax(feature_scores))
        reason = reason_map[best_feature_idx]
        
        if not movie_row.empty:
            title = str(movie_row['title'].iloc[0])
            genres = list(movie_row['genres'].iloc[0])
            overview = str(movie_row['overview'].iloc[0])
            casts = list(movie_row['casts'].iloc[0])
            directors = list(movie_row['directors'].iloc[0])
            poster_url = str(movie_row['poster_url'].iloc[0])
            keywords = list(movie_row['keywords'].iloc[0])
        else:
            title = "Unknown"
            genres, casts, directors, keywords = [], [], [], []
            overview, poster_url = "", ""
    
        recommendations.append({
            "movie": {
                "movie_id": rec_movie_id,
                "title": title,
                "genres": genres,
                "overview": overview,
                "casts": casts,
                "directors": directors,
                "poster_url": poster_url,
                "keywords": keywords
            },
            "score": score,
            "reason": reason
        })
    
    return {"recommendations": recommendations}