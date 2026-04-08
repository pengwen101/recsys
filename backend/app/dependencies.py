from backend.app import state

def get_recommendation():
    return state.neumf_bce_rec

def get_movies_detail():
    return state.movies_df

def get_keywords_matrix():
    return state.keywords_matrix

def get_genres_matrix():
    return state.genres_matrix

def get_directors_matrix():
    return state.directors_matrix

def get_casts_matrix():
    return state.casts_matrix

def get_user_ids():
    return state.user_ids

def get_matrix_mapping():
    return state.matrix_mapping