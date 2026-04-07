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
        
        self._set_userId_sequenced_map()
        self._set_itemId_sequenced_map()
        
        self.user_seen_map = self._build_user_seen_map()
    
    def _convert_df_to_implicit(self):
        """Convert dataframe from 5-star rating to implicit signals
        """
        if self.implicit:
            self.df[self.rating_col] = self.df[self.rating_col].map(lambda x: 1 if x >= self.threshold else 0)
    
    def _set_userId_sequenced_map(self):
        """set a dictionary of {original userId: transformed userId}
        """
        self.userId_map = {original_id: i for i, original_id in enumerate(self.user_ids)}
        self.userId_map_rev = {v: k for k, v in self.userId_map.items()}
    
    def _set_itemId_sequenced_map(self):
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