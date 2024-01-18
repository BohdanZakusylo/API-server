import json
import xmltodict
from fastapi import HTTPException
import xml.etree.ElementTree as ET


ACCEPTED_DATA_TYPES = ["application/xml", "application/json"]


class Correct_Data:
    def __init__(self):
        pass

    def validate_data_type(self, data_type):
        if data_type not in ACCEPTED_DATA_TYPES:
            raise HTTPException(status_code=404, detail="data type is invalid")
        return data_type

    def return_correct_format(self, data_dict, data_type, entity):
        print(f"Data type: {data_type}")
        if data_type == "application/xml":
            data_list = data_dict.get("data", [])
            status = data_dict.get("status")

            root = ET.Element("response")
            status_element = ET.SubElement(root, "status")
            status_element.text = status

            for item in data_list:
                xml_item = ET.SubElement(root, entity)
                for key, value in item.items():
                    ET.SubElement(xml_item, key).text = value

            return ET.tostring(root, encoding="unicode")

        return data_dict
