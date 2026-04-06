import torch
import torch.nn as nn
import os
import numpy as np

class NeuMF(nn.Module):
    def __init__(self, num_users, num_items, embedding_dim, nums_hiddens):
        super().__init__()
        self.P = nn.Embedding(num_users, embedding_dim)
        self.Q = nn.Embedding(num_items, embedding_dim)
        self.U = nn.Embedding(num_users, embedding_dim)
        self.V = nn.Embedding(num_items, embedding_dim)
        layers = []
        input_dim = embedding_dim * 2
        for num_hiddens in nums_hiddens:
            layers.append(nn.Linear(input_dim, num_hiddens))
            layers.append(nn.ReLU())
            input_dim = num_hiddens
        
        self.mlp = nn.Sequential(*layers)
        
        self.prediction_layer = nn.Linear(embedding_dim + nums_hiddens[-1], 1)

    def forward(self, user_id, item_id):
        p_mf = self.P(user_id)
        q_mf = self.Q(item_id)
        gmf = p_mf * q_mf
        p_mlp = self.U(user_id)
        q_mlp = self.V(item_id)
        
        mlp_input = torch.cat([p_mlp, q_mlp], dim=1)
        mlp_out = self.mlp(mlp_input)
        
        con_res = torch.cat([gmf, mlp_out], dim=1)
       
        return self.prediction_layer(con_res)
    
class NeuMFRecommender():
    def __init__(self, dataprep, model):
        self.dataprep = dataprep
        self.model = model
        self.history = None
    
    def recommend_for_user(self, userId, k):
        """Returns top k items and predicted scores for a user
        
        Keyword arguments:
        userId -- original user id
        k -- number of items recommended
        Return: dataframe of top k item id and its predicted score for a user
        """
        
        # Get the sequenced user id used for training embeddings
        userId_idx = self.dataprep.userId_map[userId]
        # Filter out items a user has seen
        unseen_item_ids = list(set(self.dataprep.item_ids) - set(self.dataprep.user_seen_map[userId]))
        # Map into item ids used for training
        unseen_item_idx = [self.dataprep.itemId_map[i] for i in unseen_item_ids]
        num_items = len(unseen_item_idx)
        device = torch.device('cpu')
        userId_idx_tensor = torch.tensor([userId_idx], dtype=torch.long, device=device).repeat(num_items)
        unseen_item_idx_tensor = torch.tensor(unseen_item_idx, dtype=torch.long, device=device)

        self.model.to(device)
        self.model.eval()
        with torch.no_grad():
            scores = self.model(userId_idx_tensor, unseen_item_idx_tensor)
            scores = scores.detach().cpu().numpy().flatten()
            
        top_k_rows = np.argsort(-scores)[:k]
        # Map back to item ids used for training
        top_k_ids = [unseen_item_idx[i] for i in top_k_rows]
        # Map back to original item ids
        top_k_ids = [self.dataprep.itemId_map_rev[a] for a in top_k_ids]
        final_recommendations = {}
        final_recommendations["movie_id"] = top_k_ids
        keys = final_recommendations.keys()
        final_recommendations = [dict(zip(keys, values)) for values in zip(*final_recommendations.values())]
        top_k_scores = scores[top_k_rows]
        for i, _ in enumerate(final_recommendations):
            final_recommendations[i]['score'] = top_k_scores[i]
        return final_recommendations
    
    def load_model(self, model_path):
        if hasattr(model_path, "parent"):
            os.makedirs(model_path.parent, exist_ok=True)
        self.model.load_state_dict(torch.load(model_path, weights_only=True, map_location=torch.device('cpu')))
        self.model.eval()
            
        print("Model loaded successfully.")
        
        return self.model, self.history

    
class DataPreparation:
    def __init__(self, df, user_col_ori, item_col_ori, rating_col, implicit, threshold):
        self.df = df.copy()
        self.user_col_ori = user_col_ori
        self.item_col_ori = item_col_ori
        self.rating_col = rating_col
        self.implicit = implicit
        self.threshold = threshold
        if implicit:
            self._convert_df_to_implicit()
        
        self.n_users = df[user_col_ori].nunique()
        self.n_items = df[item_col_ori].nunique()
        self.user_ids = list(df[user_col_ori].unique())
        self.item_ids = list(df[item_col_ori].unique())
        
        self.set_userId_sequenced_map()
        self.set_itemId_sequenced_map()
        
        self.user_seen_map = self._build_user_seen_map()
    
    def _convert_df_to_implicit(self):
        """Convert dataframe from 5-star rating to implicit signals
        """
        if self.implicit:
            self.df[self.rating_col] = self.df[self.rating_col].map(lambda x: 1 if x >= self.threshold else 0)
        else:
            pass
    
    def set_userId_sequenced_map(self):
        """set a dictionary of {original userId: transformed userId}
        """
        self.userId_map = {original_id: i for i, original_id in enumerate(self.user_ids)}
        self.userId_map_rev = {v: k for k, v in self.userId_map.items()}
    
    def set_itemId_sequenced_map(self):
        """set a dictionary of {original itemId: transformed itemId}
        """
        self.itemId_map = {original_id: i for i, original_id in enumerate(self.item_ids)}
        self.itemId_map_rev = {v: k for k, v in self.itemId_map.items()}
    
    def _build_user_seen_map(self):
        """Get a dictionary map of {user: set of itemIds the user interacted with in train set}
        Return: dict
        """
        user_seen_map = self.df.groupby(self.user_col_ori)[self.item_col_ori].apply(set).to_dict()
        
        return user_seen_map