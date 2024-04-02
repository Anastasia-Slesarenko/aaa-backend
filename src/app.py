import logging
from flask import Flask, request
from models.plate_reader import PlateReader, InvalidImage
from image_provider_client import get_image
import logging
import io
import requests


app = Flask(__name__)
plate_reader = PlateReader.load_from_file('./model_weights/plate_reader_model.pth')
IMAGE_PROVIDER_TIMEOUT = 5


def recognize_plate_number(img_id: int):
    try:
        image_bytes = get_image(img_id, timeout=IMAGE_PROVIDER_TIMEOUT)
        image = io.BytesIO(image_bytes)
        logging.info("The image is received %s", img_id)
    except requests.Timeout:
        logging.error("Timeout occurred while downloading image from external service")
        return {"error": "Timeout occurred while downloading image"}, 504
    except requests.RequestException as e:
        logging.error("Error retrieving image from external service: %s", e)
        return {"error": "Error retrieving image from external service"}, 500
    except Exception as e:
        logging.error("Error downloading the image: %s", e)
        return {"error": str(e)}, 500

    try:
        number = plate_reader.read_text(image)
        logging.info("Recognized plate number for image ID %s: %s", img_id, number)
        return number
    except InvalidImage:
        logging.error('invalid image')
        return {'error': 'invalid image'}, 400


# return one plate_number from one image
@app.route('/images/<int:img_id>', methods=['GET'])
def read_plate_number(img_id: int):
    logging.info("Recognizing plate number for image ID %s", img_id)
    plate_number = recognize_plate_number(img_id)
    return {
         'plate_number': plate_number,
    }


# return any plate_number from any images
@app.route('/images', methods=['POST'])
def read_plate_numbers():
    data = request.get_json()
    if not data or 'img_ids' not in data:
        logging.error('Invalid JSON data received')
        return {'error': 'Invalid JSON data'}, 400

    plate_numbers = {}
    for img_id in data['img_ids']:
        logging.info("Recognizing plate number for image ID %s", img_id)
        plate_numbers[img_id] = recognize_plate_number(img_id)
    return {
        'plate_numbers':  plate_numbers
    }


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=8080, debug=True)
