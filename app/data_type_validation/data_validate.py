import json
import xmltodict
from fastapi import HTTPException
import xml.etree.ElementTree as ET


ACCEPTED_DATA_TYPES = ["xml", "json"]
ACCEPTED_MATERIAL_TYPE = ["Film", "Series", "Episode"]


class Correct_Data:
    def __init__(self):
        pass

    def validate_data_type(self, data_type):
        if data_type not in ACCEPTED_DATA_TYPES:
            raise HTTPException(status_code=404, detail="data type in the end is invalid")

    def return_correct_format(self, data_dict, data_type, entity):
        if data_type == "xml":
            root = ET.Element(entity + "s")  # Pluralize entity name for the root element

            for user_data in data_dict:
                user_element = ET.SubElement(root, entity)
                for key, value in user_data.items():
                    ET.SubElement(user_element, key).text = str(value)

            return ET.tostring(root, encoding='unicode', method='xml')
        
        return data_dict

    def validate_material_type(self, material_type):
        if (material_type) not in ACCEPTED_MATERIAL_TYPE:
            raise HTTPException(status_code=404, detail="Material type is invalid")