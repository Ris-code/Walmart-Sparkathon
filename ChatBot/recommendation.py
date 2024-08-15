import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Define Dataset
class RatingsDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        user = torch.tensor(self.data.iloc[idx]['user_id'], dtype=torch.long)
        product = torch.tensor(self.data.iloc[idx]['product_id'], dtype=torch.long)
        rating = torch.tensor(self.data.iloc[idx]['rating'], dtype=torch.float)
        return torch.stack([user, product]), rating

# Define Model
class RecommenderModel(nn.Module):
    def __init__(self, num_users, num_products, embedding_dim):
        super(RecommenderModel, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.product_embedding = nn.Embedding(num_products, embedding_dim)
        self.fc1 = nn.Linear(embedding_dim * 2, 128)
        self.fc2 = nn.Linear(128, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        user_emb = self.user_embedding(x[:, 0])
        product_emb = self.product_embedding(x[:, 1])
        x = torch.cat([user_emb, product_emb], dim=1)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = torch.sigmoid(x)
        return x

num_users = 18100
num_products = 2702
model = RecommenderModel(num_users, num_products, embedding_dim = 128 )

model = torch.load("customerRecommendationModel.pth")

def recommend_products(model, user_id, userDict, productDict, device):
    l = [] 
    productIds = []
    for i in productDict.keys():
        if(not isinstance(i, str)):
            l.append(np.array([user_id , i ]) )
            productIds.append(i)
    x = np.array(l)
    x = torch.tensor(x)
    model.eval()
    x = x.to(device)
    output = model(x).squeeze()
    recommendations = pd.DataFrame()
    recommendations['productID'] = productIds
    scores = []
    for i in range(len(productIds)):
        scores.append(output[i].item())
    recommendations['rating'] = scores
    
    recommendations = recommendations.sort_values(by='rating', ascending=False)
    return recommendations

