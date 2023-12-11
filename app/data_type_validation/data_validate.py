import json
import xmltodict

ACCEPTED_DATA_TYPES = ["xml", "json"];

def return_correct_data(data_type: str, data_dict):
    if data_type not in ACCEPTED_DATA_TYPES:
        raise HTTPException(status_code=404, detail="data type in the end is invalid")

    if data_type == "xml":
        xml = json.dumps(data_dict, ensure_ascii=False)
        return xmltodict.unparse({"data": xml}, pretty=True)

    return data_dict