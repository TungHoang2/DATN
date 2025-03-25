from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId  # Import ObjectId để chuyển đổi

app = Flask(__name__)

# Kết nối MongoDB (sửa lại theo URI MongoDB của bạn)
client = MongoClient("mongodb://localhost:27017/")
db = client["motor_database"]
collection = db["motor_5"]

@app.route("/data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json()
        result = collection.insert_one(data)  # Lưu vào MongoDB
        return jsonify({"message": "Data saved", "id": str(result.inserted_id)})  # Chuyển ObjectId thành chuỗi
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)