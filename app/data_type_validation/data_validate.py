import json
import xmltodict
from fastapi import HTTPException

ACCEPTED_DATA_TYPES = ["xml", "json"];


class Correct_Data:
    def __init__(self):
        pass

    def validate_data_type(self, data_type):
        if data_type not in ACCEPTED_DATA_TYPES:
            raise HTTPException(status_code=404, detail="data type in the end is invalid")

    def return_correct_format(self, data_dict, data_type):
        if data_type == "xml":
            xml = json.dumps(data_dict, ensure_ascii=False)
            return xmltodict.unparse({"data": xml}, pretty=True)

        return data_dict