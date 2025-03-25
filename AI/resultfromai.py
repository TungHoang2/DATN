import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# Đảm bảo đường dẫn tới model là đúng
model_path = os.path.join(os.path.dirname(__file__), "lgbm_classifier_model_12.pkl")

# Load model
model = joblib.load(model_path)


# # Load mô hình
# model = joblib.load("lgbm_classifier_model_12.pkl")

def process_features(df):
    """
    Tiền xử lý feature cho dữ liệu đầu vào.
    """
    df = df.copy()
    
    df['Power'] = df['Torque [Nm]'] * df['Rotational speed [rpm]']
    df['TemperatureDifference'] = df['Process temperature [K]'] - df['Air temperature [K]']
    df['TemperatureVariability'] = df[['Air temperature [K]', 'Process temperature [K]']].std(axis=1)
    df['TemperatureRatio'] = df['Process temperature [K]'] / df['Air temperature [K]']
    df['ToolWearRate'] = df['Tool wear [min]'] / (df['Tool wear [min]'].max())
    df['TemperatureChangeRate'] = df['TemperatureDifference'] / df['Tool wear [min]']
    df['TemperatureChangeRate'] = np.where(df['TemperatureChangeRate'] == float('inf'), 1, df['TemperatureChangeRate'])
    df['TotalFailures'] = df[['TWF', 'HDF', 'PWF', 'OSF', 'RNF']].sum(axis=1)
    df["TorqueWearRatio"] = df['Torque [Nm]'] / (df['Tool wear [min]'] + 0.0001)
    df["TorqueWearProduct"] = df['Torque [Nm]'] * df['Tool wear [min]']
    df["Product_id_num"] = pd.to_numeric(df["Product ID"].str.slice(start=1))
    
    features_list = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
    for feat in features_list:
        df[f'{feat}Squared'] = df[feat] ** 2
        df[f'{feat}Cubed'] = df[feat] ** 3
        df[f'{feat}Log'] = df[feat].apply(lambda x: math.log(x) if x > 0 else 0)
    
    for feat1 in features_list:
        for feat2 in features_list:
            df[f'{feat1}_{feat2}_Product'] = df[feat1] * df[feat2]
    
    df.drop(['Product ID'], axis=1, inplace=True)
    df.drop(['RNF'], axis=1, inplace=True)
    
    return df

def predict_failure(data):
    """
    Hàm nhận dữ liệu thô (data), xử lý feature, chuẩn hóa và đưa vào mô hình để dự đoán.
    """
    df = pd.DataFrame(data)

    # Chuẩn hóa dữ liệu
    num_cols = df.columns[2:6]  # Các cột số
    scaler = MinMaxScaler()
    df[num_cols] = scaler.fit_transform(df[num_cols])

    # Xử lý feature
    df = process_features(df)

    # One-hot encoding
    df = pd.get_dummies(df, drop_first=True)

    # Chuẩn hóa tên cột
    df.columns = df.columns.str.replace('[\[\]]', '', regex=True)

    # Loại bỏ các cột không quan trọng
    cols_to_drop = [
        'Type_M', 'Type_L', 'Tool wear min_Air temperature K_Product', 'Process temperature KSquared',
        'Air temperature KSquared', 'Torque Nm_Tool wear min_Product', 'Rotational speed rpm_Process temperature K_Product',
        'Tool wear min_Process temperature K_Product', 'Tool wear min_Rotational speed rpm_Product',
        'Rotational speed rpmSquared', 'Torque Nm_Air temperature K_Product', 'ToolWearRate',
        'Process temperature K_Air temperature K_Product', 'Process temperature KLog',
        'Rotational speed rpm_Torque Nm_Product', 'Rotational speed rpm_Air temperature K_Product',
        'Torque NmSquared', 'Air temperature KLog'
    ]

    df.drop(columns=[col for col in cols_to_drop if col in df.columns], axis=1, inplace=True)

    # Lấy danh sách feature của mô hình
    model_features = model.booster_.feature_name()

    # Chỉ giữ lại các feature có trong mô hình
    df = df.reindex(columns=model_features, fill_value=0)

    # Định dạng lại dữ liệu đầu vào
    X_test = df.values  # Không cần reshape (model xử lý nhiều dòng cùng lúc)

    # Dự đoán
    y_pred = model.predict(X_test)

    return y_pred

# # ======= TEST FUNCTION =======
# data = {
#     "Product ID": ["L52498", "L51721", "M17895", "L55926"],
#     "Type": ["L", "L", "M", "L"],
#     "Air temperature [K]": [303.9, 302.5, 300.7, 297.3],
#     "Process temperature [K]": [312.8, 310.4, 309.7, 308.6],
#     "Rotational speed [rpm]": [1345, 1307, 1878, 1258],
#     "Torque [Nm]": [56.5, 54.8, 27.9, 61.8],
#     "Tool wear [min]": [21, 174, 20, 144],
#     "TWF": [0, 0, 0, 0],
#     "HDF": [0, 1, 0, 0],
#     "PWF": [0, 0, 0, 0],
#     "OSF": [0, 0, 0, 1],
#     "RNF": [0, 0, 0, 0]
# }

# result = predict_failure(data)
# print("\nKết quả dự đoán:")
# print(result)
