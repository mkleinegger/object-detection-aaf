import json
import os
import sys
import requests
import glob
import uuid
import base64


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <inputfolder> <endpoint>")
        sys.exit(1)

    input_folder = sys.argv[1]
    endpoint = sys.argv[2]

    path = os.path.abspath(input_folder)
    for file in glob.glob(f"{path}/*.*"):
        with open(file, "rb") as f:
            encoded_string = base64.b64encode(f.read())
            file_uuid = uuid.uuid4()

            print(
                f"Requesting object-detection for image '{os.path.basename(file)}' with id '{file_uuid}'"
            )
            response = requests.post(
                endpoint,
                headers={"Content-type": "application/json"},
                json=json.dumps(
                    {"id": str(file_uuid), "image_data": encoded_string.decode("utf-8")}
                ),
            )

            if response.status_code != 200:
                print(f"-> Couldn't receive results for image with id '{file_uuid}'")
                continue

            result = response.json()
            print(f"-> Received following objects for id '{result['id']}':")
            if len(result["objects"]) == 0:
                print(f"   No objects could be detected!")
            else:
                for o in result["objects"]:
                    print(
                        f"   Object '{o['label']}' found with accuracy {o['accuracy']:.4f}"
                    )


if __name__ == "__main__":
    main()
