from pymongo import MongoClient

class Database:
    def __init__(self):
        cluster = MongoClient("mongodb+srv://dbUser:CSE412@cluster0.8grfz.mongodb.net/CBRS?")
        db = cluster["CBRS"]
        self.images_collection = db["images"]
        self.videos_collection = db["videos"]

    def insert(self, docs):
        self.images_collection.insert_one(docs)
        print('stored')

    def mean_color_find(self, query_img_mean):
        return self.images_collection.find(
            {"$and": [{"$and": [{"features.0": {"$gt": 0.9 * query_img_mean[0]}},
                                {"features.0": {"$lt": 1.1 * query_img_mean[0]}}]},
                      {"$and": [{"features.1": {"$gt": 0.9 * query_img_mean[0]}},
                                {"features.1": {"$lt": 1.1 * query_img_mean[0]}}]},
                      {"$and": [{"features.2": {"$gt": 0.9 * query_img_mean[0]}},
                                {"features.2": {"$lt": 1.1 * query_img_mean[0]}}]}]}, {"_id": 0, "path": 1})

    def mean_color_find2(self):
        return self.images_collection.find({}, {"_id": 0, "path": 1, "features": 1})

    def histogram_find(self):
        return self.images_collection.find({}, {"_id": 0, "path": 1, "hist": 1})

    def colorLayout_find(self):
        return self.images_collection.find({}, {"_id": 0, "path": 1, "colorLayout": 1})

    def colorLayout_find2(self):
        return self.images_collection.find({}, {"_id": 0, "path": 1, "colorLayout2": 1})

    def delete_all(self):
        self.images_collection.delete_many({})

    #Videos Collection Functions Define
    def insert_video(self, video):
        self.videos_collection.insert_one(video)
        print('stored')

    def mean_color_find_video(self):
        return self.videos_collection.find({}, {"_id": 0, "path": 1, "features": 1})

    def histogram_find_video(self):
        return self.videos_collection.find({}, {"_id": 0, "path": 1, "hist": 1})

    def destroy_videos_collection(self):
        self.videos_collection.delete_many({})
