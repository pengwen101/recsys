from pathlib import Path
from backend.app.model import NeuMF, NeuMFRecommender, DataPreparation
import pandas as pd

file_path = Path(__file__).resolve()
ratings_path = file_path.parent.parent.parent / "data" / "ratings.parquet"
movies_path = file_path.parent.parent.parent / "data" / "movies_genre.parquet"
model_path = file_path.parent.parent.parent / "models" / "implicit_neumf_bce.pth"

ratings_df = pd.read_parquet(ratings_path)
movies_genre_df = pd.read_parquet(movies_path)
movies_genre_df = movies_genre_df.groupby(['movieId', 'title'])['genres'].agg(list).reset_index()
user_ids = ratings_df['userId'].unique()

dataprep = DataPreparation(ratings_df, "userId", "movieId", "rating", implicit=True, threshold=3.0)
neumf_bce_model = NeuMF(dataprep.n_users, dataprep.n_items, embedding_dim=30, nums_hiddens=[128, 64, 32])
neumf_bce_rec = NeuMFRecommender(dataprep, neumf_bce_model)

neumf_bce_rec.load_model(model_path)

def get_recommendation():
    return neumf_bce_rec

def get_movies_detail():
    return movies_genre_df

def get_user_ids():
    return user_ids