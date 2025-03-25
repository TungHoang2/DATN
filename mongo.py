from pymongo import MongoClient
from datetime import datetime
import random
import time
import joblib  # Dùng để load model Scikit-learn hoặc XGBoost
from AI import predict

# Kết nối đến MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['motor_database']

# Danh sách các motor
motors = ['motor_1', 'motor_2', 'motor_3', 'motor_4']

# Vòng lặp gửi dữ liệu mỗi 10 giây
while True:
    for motor in motors:
        collection = db[motor]

        # Tạo dữ liệu mô phỏng cho motor hoạt động bình thường
        motor_data = {
            'timestamp': datetime.now(),
            'torque': round(random.uniform(4.0, 5.0), 2),      # Mô-men xoắn (Nm)
            'speed': random.randint(1400, 1600),               # Tốc độ (RPM)
            'current': round(random.uniform(2.8, 3.5), 2),     # Dòng điện (A)
            'voltage': random.randint(218, 230),               # Điện áp (V)
            'temperature': random.randint(40, 55)              # Nhiệt độ (C)
        }


        # Lưu dữ liệu vào MongoDB
        collection.insert_one(motor_data)
        print(f"Dữ liệu từ {motor} đã được lưu vào MongoDB!")

    time.sleep(30)  # Chờ 10 giây trước khi gửi lần tiếp theo