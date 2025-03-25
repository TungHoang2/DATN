import time
import json
import paho.mqtt.client as mqtt
import requests
from AI import predict

# Cấu hình ThingsBoard & Flask server
THINGSBOARD_HOST = "localhost"  # Thay bằng IP của server ThingsBoard nếu khác
THINGSBOARD_ACCESS_TOKEN = "SWM6zEAVDmSkyHZUtAbP"  # Access Token của MQTT Gateway
FLASK_SERVER_URL = "http://127.0.0.1/users"

# Lưu thời gian bản ghi cuối cùng để lấy dữ liệu mới nhất
last_timestamp = None

# Kết nối MQTT
client = mqtt.Client()
client.username_pw_set(THINGSBOARD_ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)  # Cổng mặc định của MQTT

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

                # Dự đoán machine_failure bằng model AI
                for motor, motor_data in data.items():
                    prediction_results = predict.result_AI(motor_data)
                    motor_data["machine_failure"] = int(prediction_results)

            return data  # Dữ liệu đã có machine_failure để gửi lên ThingsBoard
        else:
            print(f"Lỗi khi lấy dữ liệu từ Flask server: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi khi kết nối đến Flask server: {e}")
        return None


def send_data_to_thingsboard(data):
    """Gửi dữ liệu của tất cả motor lên ThingsBoard thông qua MQTT Gateway."""
    topic = "v1/devices/me/telemetry"
    
    payload = json.dumps({"devices": data})
    
    try:
        client.publish(topic, payload)
        print(f"Dữ liệu đã gửi thành công: {payload}")
    except Exception as e:
        print(f"Lỗi khi gửi dữ liệu qua MQTT: {e}")


def main():
    """Lấy dữ liệu mới nhất từ Flask và gửi đến ThingsBoard mỗi 30 giây."""
    while True:
        data = fetch_latest_data()
        if data:
            send_data_to_thingsboard(data)
        time.sleep(30)  # Lặp lại sau mỗi 30 giây


if __name__ == "__main__":
    main()
