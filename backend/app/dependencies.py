from backend.app import state

def get_recommendation():
    return state.neumf_bce_rec

def get_movies_detail():
    return state.movies_genre_df

def get_user_ids():
    return state.user_ids