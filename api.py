from flask import Flask
from flask_restful import Resource, Api, reqparse, abort 
from yolo_model import object_detection, load_model


app = Flask(__name__)
api = Api(app)


data={}
net = load_model()


img_post_args = reqparse.RequestParser()
img_post_args.add_argument("id", type=str, required=True, help="Unique identifier of type int requiered.")
img_post_args.add_argument("image_data", type=str, required=True, help="Image in base64-encoding requiered.")


class Image(Resource):
    def get(self, image_id):
        if image_id not in data:
            abort(404, message="Image ID {} doesn't exist".format(image_id))
        return data[image_id] 
        

    def post(self, image_id):
        args = img_post_args.parse_args()

        result = object_detection(args["id"], args["image_data"], net)

        data[image_id] = {
            "id": args["id"],
            "objects": [{"label": key, "accuracy": value} for key, value in result.items()]
        }

        return data[image_id]


api.add_resource(Image, "/images/<string:image_id>")


if __name__ == '__main__':
    app.run(debug=True)