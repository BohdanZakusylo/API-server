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
            raise HTTPException(status_code=422, detail="data type is invalid")
        return data_type

    def return_correct_format(self, data_dict, data_type, entity):
        print(f"Data type: {data_type}")
        if data_type == "application/xml":
            data_list = data_dict.get("data", [])
            status = data_dict.get("status")

            root = ET.Element("root")
            status_element = ET.SubElement(root, "status")
            status_element.text = status

            for item in data_list:
                xml_item = ET.SubElement(root, entity)
                for key, value in item.items():
                    ET.SubElement(xml_item, key).text = value

            xml_content = ET.tostring(root, encoding="unicode")
            xml_declaration = r"<?xml version='1.0' encoding='utf-8'?>"
            return xml_declaration + xml_content

        return data_dict
    
    def validate_input_fields(info, *args, **kwargs):
        unpacked_base_fields = vars(args[1])
        fields = unpacked_base_fields["__annotations__"]

        args_dict = {attr: str(cls).split("'")[1] for attr, cls in fields.items()}
        print(f"my {args[0]} and my {args_dict}")

        for key, value in args_dict.items():
            print(key, value)



    
