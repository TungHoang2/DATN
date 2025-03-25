from AI import mappingdata
from AI import resultfromai


def result_AI(data):
    # data = {
    #     "timestamp": "2025-02-07T17:25:54.195+00:00",
    #     "torque": 4.94,
    #     "speed": 1531,
    #     "current": 2.83,
    #     "voltage": 225,
    #     "temperature": 54,
    # }

    data_transform = mappingdata.mappingData(data)
    result = int (resultfromai.predict_failure(data_transform))
    return result
    # print(result)