import numpy as np
import pandas as pd

def min_max_scaling(value, old_min, old_max, new_min, new_max):
    return new_min + ((value - old_min) / (old_max - old_min)) * (new_max - new_min)

def mappingData(data):
    dataset_stats = {
        "Air temperature [K]": (299.86, 1.86, 295, 304.4), # mean, std, min, max
        "Process temperature [K]": (309.94, 1.38, 305, 313.8),
        "Rotational speed [rpm]": (1520.33, 138.73, 1181, 2886),
        "Torque [Nm]": (40.35, 8.50, 3.8, 76.6),
        "Tool wear [min]": (104.41, 63.97, 0, 253),
    }
    
    mapped_data = {
        "Product ID": "L50896",
        "Type": "L",
        "Air temperature [K]": min_max_scaling(data["temperature"] + 273.15, 295, 304.4, 295, 304.4),
        "Process temperature [K]": min_max_scaling(data["temperature"] + 10 + 273.15, 305, 313.8, 305, 313.8),
        "Rotational speed [rpm]": min_max_scaling(data["speed"], 1181, 2886, 700, 900),
        "Torque [Nm]": min_max_scaling(data["torque"], 3.8, 76.6, 2, 6),
        "Tool wear [min]": int(np.clip(np.random.normal(104.41, 63.97), 0, 253)), # mean, std, min, max from dataset_stats
        "TWF": int (np.random.choice([0, 1], p=[0.9985, 0.0015])),
        "HDF": int (np.random.choice([0, 1], p=[0.994, 0.006])),
        "PWF": int (np.random.choice([0, 1], p=[0.9976, 0.0024])),
        "OSF": int (np.random.choice([0, 1], p=[0.996, 0.004])),
        "RNF": int (np.random.choice([0, 1], p=[0.9977, 0.0023])),
    }
    
    data_transformed = {key: [value] for key, value in mapped_data.items()}
    return data_transformed

# # Test hàm với dữ liệu mẫu
# data = {
#     "timestamp": "2025-02-07T17:25:54.195+00:00",
#     "torque": 4.94,
#     "speed": 1531,
#     "current": 2.83,
#     "voltage": 225,
#     "temperature": 54,
# }

# df_motor = mappingData(data)
# print(df_motor)
