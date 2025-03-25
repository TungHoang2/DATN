import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler
import joblib

# Tạo DataFrame từ dữ liệu
data = {
    "Product ID": ["L50896"],
    "Type": ["L"],
    "Air temperature [K]": [302.3],
    "Process temperature [K]": [311.5],
    "Rotational speed [rpm]": [1499],
    "Torque [Nm]": [38.0],
    "Tool wear [min]": [60],
    "TWF": [0],
    "HDF": [0],
    "PWF": [0],
    "OSF": [0],
    "RNF": [0]
}

df = pd.DataFrame(data)

# Chọn các cột số để chuẩn hóa
num_cols = df.columns[2:6]  # Lấy từ cột số 2 đến số 6
scaler = MinMaxScaler()
df[num_cols] = scaler.fit_transform(df[num_cols])

# Hàm tạo feature
def feat(df):
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
    
    # Feature scaling cho các feature quan trọng
    features_list = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
    for feat in features_list:
        df[f'{feat}Squared'] = df[feat] ** 2
        df[f'{feat}Cubed'] = df[feat] ** 3
        df[f'{feat}Log'] = df[feat].apply(lambda x: math.log(x) if x > 0 else 0)
    
    for feat1 in features_list:
        for feat2 in features_list:
            df[f'{feat1}_{feat2}_Product'] = df[feat1] * df[feat2]
    
    # Loại bỏ các cột không cần thiết
    df.drop(['Product ID'], axis=1, inplace=True)
    df.drop(['RNF'], axis=1, inplace=True)
    return df

# Áp dụng hàm feature engineering
df = feat(df)

# Chuyển đổi categorical thành one-hot encoding
df = pd.get_dummies(df, drop_first=True)

# Định dạng lại tên cột để tránh lỗi
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

X_test = df.drop(columns=[col for col in cols_to_drop if col in df.columns], axis=1, inplace=True)

# In số lượng feature
print(f"Số lượng feature sau khi xử lý: {df.shape[1]}")
print(df.head())  # In ra dataframe sau khi xử lý


# Load mô hình đã lưu
model = joblib.load("lgbm_classifier_model_12.pkl")

# Dự đoán
y_pred = model.predict(X_test)

print(y_pred)



