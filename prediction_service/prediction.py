import yaml
import os
import json
import joblib
import numpy as np

params_path = "params.yaml"
schema_path = os.path.join("prediction_service","schema_in.json")

class NotInRange(Exception):
    def __init__(self,message = "Values Entered are not in Range."):
        self.message = message
        super().__init__(self.message)


class NotInCols(Exception):
    def __init__(self,message = "All Required Columns are not Specified."):
        self.message = message
        super().__init__(self.message)


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
        return config


def get_schema(schema_path = schema_path):
    with open(schema_path) as schema_file:
        schema = json.load(schema_file)
        return schema


def predict(data):
    config = read_params(params_path)
    model_dir_path = config['webapp_model_dir']
    model = joblib.load(model_dir_path)
    prediction = model.predict(data).tolist()[0]

    try:
        if 3 <= prediction <= 8:
            return prediction
        else:
            raise NotInRange
    except NotInRange:
        return "Unexpected Result"




def validate_input(dict_request):
    
    def _validate_cols(col,val):
        schemas = get_schema()
        actual_cols = schemas.keys() 
        if(col not in actual_cols):
            raise NotInCols
        if(val == ""):
            raise NotInCols

    def _validate_values(col,val):
        schemas = get_schema()
        if not(schemas[col]['min'] <= float(val) <= schemas[col]['max']):
            raise NotInRange
    
    for col,value in dict_request.items():
        _validate_cols(col,value)
        _validate_values(col,value)
    
    return True



def form_response(dict_request):
    if(validate_input(dict_request)):
        data = dict_request.values()
        data = [list(map(float,data))]
        response = predict(data)
        return response


def api_response(dict_request):
    try:
        if(validate_input(dict_request)):
            data = np.array([list(dict_request.values())])
            response = predict(data)
            response = {"response": response}
            return response
    except NotInRange as e:
        response = {"expectedRange": get_schema(), "response": str(e) }
        return response

    except NotInCols as e:
        response = {"expectedCols": get_schema().keys(), "response": str(e) }
        return response

    except Exception as e:
        response = {"response": str(e) }
        return response  

