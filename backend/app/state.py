from pathlib import Path
from backend.app.model import NeuMF, NeuMFRecommender
from backend.app.dataprep import DataPreparation
import pandas as pd
import scipy.sparse
import pickle

file_path = Path(__file__).resolve()
ratings_df = None
neumf_bce_rec = None
movies_df = None
keywords_matrix = None
genres_matrix = None
directors_matrix = None
casts_matrix = None
user_ids = None
matrix_mapping = None

def load_state():
    global neumf_bce_rec, user_ids, movies_df, ratings_df, keywords_matrix, genres_matrix, directors_matrix, casts_matrix, matrix_mapping
    
    ratings_path = file_path.parent.parent.parent / "data" / "ratings.parquet"
    movies_path = file_path.parent.parent.parent / "data" / "movies.parquet"
    model_path = file_path.parent.parent.parent / "models" / "implicit_neumf_bce.pth"
    keywords_matrix_path = file_path.parent.parent.parent / "data" / "matrix_keywords.npz"
    genres_matrix_path = file_path.parent.parent.parent / "data" / "matrix_genres.npz"
    directors_matrix_path = file_path.parent.parent.parent / "data" / "matrix_directors.npz"
    casts_matrix_path = file_path.parent.parent.parent / "data" / "matrix_casts.npz"
    matrix_mapping_path = file_path.parent.parent.parent / "data" / "matrix_mapping.pkl"

    ratings_df = pd.read_parquet(ratings_path)
    movies_df = pd.read_parquet(movies_path)
    user_ids = ratings_df['userId'].unique()
    
    keywords_matrix = scipy.sparse.load_npz(keywords_matrix_path)
    genres_matrix = scipy.sparse.load_npz(genres_matrix_path)
    directors_matrix = scipy.sparse.load_npz(directors_matrix_path)
    casts_matrix = scipy.sparse.load_npz(casts_matrix_path)
    
    with open(matrix_mapping_path, 'rb') as file:
        matrix_mapping = pickle.load(file)

    dataprep = DataPreparation(ratings_df, "userId", "movieId", "rating", implicit=True, threshold=3.0)
    neumf_bce_model = NeuMF(dataprep.n_users, dataprep.n_items, embedding_dim=30, nums_hiddens=[128, 64, 32])
    neumf_bce_rec = NeuMFRecommender(dataprep, neumf_bce_model)

    neumf_bce_rec.load_model(model_path)
    
    
    
    
    
    