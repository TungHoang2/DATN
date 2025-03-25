import requests
import time
from pymongo import DESCENDING
import pymongo
import json
from AI import predict
from pymongo import MongoClient, DESCENDING
import requests
import json

# Kết nối đến MongoDB
MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["motor_database"]  # Thay "motor_database" bằng tên database thực tế


# Cấu hình ThingsBoard và Flask server
THINGSBOARD_URL = "http://localhost:8080/api/v1"
FLASK_SERVER_URL = "http://127.0.0.1/users"

# Access Tokens cho từng motor
ACCESS_TOKENS = {
    "motor_1": "HNMQrXvOxQT6nKnR4ThE",
    "motor_2": "ZO6g93N0aFvSVXsy5deq",
    "motor_3": "ZyHZaiQdwQ04xfpsBy3K",
    "motor_4": "LlTUeGxgdF2b2UgSvw0i"
}

# Lưu thời gian bản ghi cuối cùng để lấy dữ liệu mới nhất
last_timestamp = None

#################### chạy đúng nguyên mẫu chưa có machine failure
# def fetch_latest_data():
#     """Lấy dữ liệu mới nhất từ Flask server."""
#     global last_timestamp
#     params = {}

#     if last_timestamp:
#         params["last_timestamp"] = last_timestamp  # Lấy dữ liệu mới hơn timestamp trước

#     try:
#         response = requests.get(FLASK_SERVER_URL, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 last_timestamp = data["motor_1"]["timestamp"]  # Cập nhật timestamp mới nhất
#             return data
#         else:
#             print(f"Lỗi khi lấy dữ liệu từ Flask server: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Lỗi khi kết nối đến Flask server: {e}")
#         return None



############################# lần 2 đã có machine failure nhưng không chắc sẽ match với data được lấy 
# def fetch_latest_data():
#     """Lấy dữ liệu mới nhất từ Flask server và thêm machine_failure từ AI model."""
#     global last_timestamp
#     params = {}

#     if last_timestamp:
#         params["last_timestamp"] = last_timestamp  # Lấy dữ liệu mới hơn timestamp trước

#     try:
#         response = requests.get(FLASK_SERVER_URL, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             if data:
#                 # Kiểm tra nếu có dữ liệu hợp lệ trước khi cập nhật timestamp
#                 if "motor_1" in data and "timestamp" in data["motor_1"]:
#                     last_timestamp = data["motor_1"]["timestamp"]

#                 # Dự đoán machine_failure bằng model AI
#                 for motor, motor_data in data.items():
#                     collection = db[motor]
#                     latest_entry = collection.find_one(sort=[("_id", DESCENDING)])

#                     if latest_entry:
#                         prediction_results = predict.result_AI(latest_entry)
#                         motor_data["machine_failure"] = int(prediction_results)

#                         # Cập nhật vào database
#                         collection.update_one({"_id": latest_entry["_id"]}, {"$set": {"machine_failure": motor_data["machine_failure"]}})

#             return data
#         else:
#             print(f"Lỗi khi lấy dữ liệu từ Flask server: {response.status_code}")
#             return None
#     except Exception as e:
#         print(f"Lỗi khi kết nối đến Flask server: {e}")
#         return None



def fetch_latest_data():
    """Lấy dữ liệu mới nhất từ Flask server và thêm machine_failure từ AI model."""
    global last_timestamp
    params = {}

    if last_timestamp:
        params["last_timestamp"] = last_timestamp  # Chỉ lấy dữ liệu mới hơn timestamp trước

    try:
        response = requests.get(FLASK_SERVER_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                # Cập nhật timestamp nếu có dữ liệu mới
                if "motor_1" in data and "timestamp" in data["motor_1"]:
                    last_timestamp = data["motor_1"]["timestamp"]

                # Dự đoán machine_failure bằng model AI dựa trên dữ liệu từ Flask
                for motor, motor_data in data.items():
                    # Dự đoán trực tiếp trên dữ liệu từ Flask
                    prediction_results = predict.result_AI(motor_data)
                    motor_data["machine_failure"] = int(prediction_results)

                    # Cập nhật vào MongoDB (đảm bảo cùng bản ghi)
                    collection = db[motor]
                    collection.update_one(
                        {"_id": motor_data["_id"]},  # Cập nhật đúng bản ghi
                        {"$set": {"machine_failure": motor_data["machine_failure"]}}
                    )

            return data  # Dữ liệu đã có machine_failure để gửi lên ThingsBoard
        else:
            print(f"Lỗi khi lấy dữ liệu từ Flask server: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi khi kết nối đến Flask server: {e}")
        return None


def send_data_to_thingsboard(motor_name, motor_data):
    """Gửi dữ liệu của từng motor lên ThingsBoard."""
    token = ACCESS_TOKENS.get(motor_name)
    if not token:
        print(f"Không tìm thấy token cho {motor_name}")
        return

    url = f"{THINGSBOARD_URL}/{token}/telemetry"
    headers = {"Content-Type": "application/json"}

    # Loại bỏ _id và timestamp để gửi dữ liệu telemetry
    telemetry_data = {k: v for k, v in motor_data.items() if k not in ["_id", "timestamp"]}

    try:
        response = requests.post(url, json=telemetry_data, headers=headers)
        if response.status_code == 200:
            print(f"Dữ liệu {motor_name} đã gửi thành công: {telemetry_data}")
        else:
            print(f"Lỗi khi gửi dữ liệu {motor_name}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Lỗi khi gửi dữ liệu từ {motor_name}: {e}")


def main():
    """Lấy dữ liệu mới nhất từ Flask và gửi đến từng motor trên ThingsBoard mỗi 10 giây."""
    while True:
        data = fetch_latest_data()
        if data:
            for motor, motor_data in data.items():
                send_data_to_thingsboard(motor, motor_data)
        time.sleep(30)  # Lặp lại sau mỗi 10 giây


if __name__ == "__main__":
    main()
