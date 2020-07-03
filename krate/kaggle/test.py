from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
api.authenticate()

def test():
    return api.dataset_list(search="mnist")


print(test())