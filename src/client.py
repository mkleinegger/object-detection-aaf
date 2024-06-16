import os
from yolo_model import load_image_as_base64
import requests
import sys


input_folder = sys.argv[1]
endpoint = sys.argv[2]


for file_name in os.listdir(input_folder):
    path_to_img = input_folder + file_name
    img_data, uuid = load_image_as_base64(path_to_img)

    post_data = {"id":str(uuid), "image_data":img_data}

    response = requests.post(f"{endpoint}/{uuid}",json=post_data)
    print(response.json())