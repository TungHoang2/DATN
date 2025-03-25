from flask import Flask, Response, jsonify
from pymongo import DESCENDING
import pymongo
import json
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import joblib  # Dùng để load model Scikit-learn hoặc XGBoost
from AI import predict


app = Flask(__name__)
model = joblib.load('xgboost_machine_failure_model.joblib')

try :
    mongo = pymongo.MongoClient(
        host="localhost",
        port= 27017,
        serverSelectionTimeoutMS = 1000
    )
    db = mongo.motor_database
    mongo.server_info() # trigger exception if cannot connect to db

except:
    print("ERROR - Cannot connect to db")
##############################
# @app.route("/users", methods=["GET"])
# def get_some_users():
#     try:
#         data = list(db.users.find())
#         for user in data:
#             user["_id"] = str(user["_id"])
#         return data
#     except Exception as ex:
#         print(ex)
#         return Response(
#             response=json.dumps(data), 
#             status=500,
#             mimetype="application/json"
#             )        

##############################

@app.route("/users", methods=["GET"])
def get_latest_data():
    try:
        all_collections = db.list_collection_names()  # Lấy danh sách tất cả các collection
        latest_data = {}

        for collection_name in all_collections:
            collection = db[collection_name]
            # Lấy bản ghi mới nhất từ từng collection
            latest_record = collection.find_one(sort=[("_id", DESCENDING)])
            
            if latest_record:
                latest_record["_id"] = str(latest_record["_id"])  # Chuyển ObjectId thành string
                latest_data[collection_name] = latest_record  # Lưu dữ liệu theo từng motor

        if latest_data:
            return jsonify(latest_data)
        else:
            return jsonify({"message": "No data found"}), 404

    except Exception as ex:
        print(ex)
        return Response(
            response=json.dumps(latest_data), 
            status=500,
            mimetype="application/json"
            )        

##############################
# @app.route("/users", methods=["POST"])
# def create_user():
#     try:
#         user = {"name": "A", "lastName": "AA"}
#         dbResponse = db.users.insert_one(user)
#         print(dbResponse.inserted_id)
#         # for attr in dir(dbResponse):
#         #     print(attr)
#         return Response(
#             response=json.dumps(
#                 {"message" :"user created",
#                 "id": f"{dbResponse.inserted_id}"
#                 }),
#             status=200,
#             mimetype="application/json"
#         )
#     except Exception as ex:
#         print("***********")
#         print(ex)
#         print("***********")

##############################
# @app.route("/users/<id>", methods = ["PATCH"])
# def update_user(id):
#     return id

##############################

@app.route("/predict_data", methods=["GET"])
def predict_from_latest_data():
    """
    Hàm mới: Dự đoán dữ liệu mới nhất từ MongoDB và trả kết quả dự đoán.
    """
    try:
        all_collections = db.list_collection_names()
        prediction_results = {}
        collection = db["motor_1"]
        input_data = collection.find_one(sort=[("_id", DESCENDING)])
        # print(input_data)
        # x_test = pd.DataFrame({
        #     'Air temperature': [295.6047912117915],        # Kelvin
        #     'Process temperature': [309.61797267803036],    # Kelvin
        #     'Rotational speed': [1796.7481337230379],      # rpm
        #     'Torque': [50.02459876637642],                  # Nm
        #     'Tool wear (min)': [183]         # phút
        # })
        prediction_results = predict.result_AI(input_data)
        # prediction_results = model.predict(x_test)[0]
        # print(prediction_results)
        # Chuyển đổi prediction từ int64 sang int
        # prediction = model.predict(x_test)[0]
        prediction_int = int(prediction_results)
        json_data = json.dumps({'machine_failure': prediction_int})
        # input_data["machine_failure"] = prediction_int
        # collection.update_one({"_id": input_data["_id"]}, {"$set": input_data})
        return prediction_int
    
        # for collection_name in all_collections:
        #     collection = db[collection_name]
        #     latest_record = collection.find_one(sort=[("_id", DESCENDING)])
        #     print(latest_record)
            # if latest_record:
            #     # Chuẩn bị dữ liệu cho mô hình dự đoán
            #     input_data = {
            #         "current": latest_record["current"],
            #         "speed": latest_record["speed"],
            #         "temperature": latest_record["temperature"],
            #         "torque": latest_record["torque"],
            #         "voltage": latest_record["voltage"]
            #     }

            #     df = pd.DataFrame([input_data])  # Chuyển dữ liệu thành DataFrame

            #     # Dự đoán kết quả bằng mô hình AI
            #     prediction = model.predict(df)[0]  # Lấy kết quả dự đoán đầu tiên

            #     # Lưu kết quả vào dictionary để trả về JSON
            #     prediction_results[collection_name] = {
            #         "input_data": input_data,
            #         "prediction": prediction
            #     }

        if prediction_results:
            return jsonify({
             "result": prediction_results
            })
        else:
            return jsonify({"message": "No data found for prediction"}), 404

    except Exception as ex:
        print(f"Error during prediction: {ex}")
        return Response(
            response=json.dumps({"error": "Prediction failed"}), 
            status=500,
            mimetype="application/json"
        )

##############################

##############################
if __name__ == "__main__":
    app.run(port= 80, debug= True)