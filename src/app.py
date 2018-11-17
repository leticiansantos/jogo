import logging
import base64
import boto3
import uuid
import time
import json
import requests
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from chalice import Chalice, Response, BadRequestError

from chalicelib import get_stage
# from chalicelib.db.models import DetectedPeopleModel
from chalicelib.db.models_mysql import DetectedPeopleModel

app = Chalice(app_name='jogo')
app.debug = True
app.log.setLevel(logging.DEBUG)

PICTURE_S3_BUCKET = 'sa-jogo-pictures-{}'.format(get_stage())

@app.route('/')
def index():
    response = requests.get('http://httpbin.org/ip')
    return response.json()

@app.route('/hi')
def hi():
    return {
        'hello':'world'
    }

@app.route('/stage')
def check_stage():
    return {
        'stage':get_stage()
    }

@app.route('/event/{event_id}')
def get_aggregated_event(event_id):
    data = DetectedPeopleModel.query(event_id)
    return json.dumps(list(data), default=lambda o: o.__dict__)

@app.route('/upload/{event_id}', methods=['POST'])
def upload_picture(event_id):
    if app.current_request.json_body.get('uuid'):
        pic_uuid = app.current_request.json_body['uuid']
    else:
        pic_uuid = str(uuid.uuid4())
    selfie = app.current_request.json_body['image']

    s3 = boto3.resource('s3')

    try:
        # move to CloudFormation template or app load
        s3.create_bucket(
            Bucket=PICTURE_S3_BUCKET,
        )
    except:
        pass

    rekognition = boto3.client('rekognition')

    s3.Bucket(PICTURE_S3_BUCKET).put_object(
        Key='selfies/{}.jpg'.format(pic_uuid),
        Body=base64.b64decode(selfie),
    )

    collection_id = 'sa-jogo-people-{}'.format(get_stage())

    try:
        rekognition.create_collection(
            CollectionId=collection_id,
        )
    # todo: define exact exception (botocore.errorfactory.ResourceAlreadyExistsException)
    except Exception:
        pass

    response = rekognition.index_faces(
        CollectionId=collection_id,
        Image={
            'S3Object': {
                'Bucket': PICTURE_S3_BUCKET,
                'Name': 'selfies/{}.jpg'.format(pic_uuid),
            },
        },
        DetectionAttributes=[
            'ALL'
        ]
    )

    ## parse rekognition response

    if not len(response['FaceRecords']) > 0:
        raise BadRequestError('Could not find valid faces')

    total_people = 0
    now=int(time.time())

    # get image with PIL
    image = Image.open(BytesIO(base64.b64decode(selfie))).convert("RGBA")
    image_width, image_height = image.size

    for face in response['FaceRecords']:
        rekognition_face_id = face['Face']['FaceId']
        age_high = face['FaceDetail']['AgeRange']['High']
        age_low = face['FaceDetail']['AgeRange']['Low']
        gender = face['FaceDetail']['Gender']['Value']
        gender_score = face['FaceDetail']['Gender']['Confidence']
        smile = face['FaceDetail']['Smile']['Value']
        smile_score = face['FaceDetail']['Smile']['Confidence']

        dom_emotion_score = 0
        dom_emotion = None
        for emotion in face['FaceDetail']['Emotions']:
            if emotion['Confidence'] > dom_emotion_score:
                dom_emotion_score = emotion['Confidence']
                dom_emotion = emotion['Type']

        detected = DetectedPeopleModel(
            event_id=event_id,
            object_id=pic_uuid,
            face_id=rekognition_face_id,
            timestamp=now,
            dominant_emotion=dom_emotion,
            dominant_emotion_score=dom_emotion_score,
            smile=smile,
            smile_score=smile_score,
            age_low=age_low,
            age_high=age_high,
            gender=gender,
            gender_score=gender_score
        )
        detected.save()
        total_people = total_people+1

        # FIXME saving image in local file system
        # what happens when running in the cloud?

        # add bounding boxes
        width = image_width * face['FaceDetail']['BoundingBox']['Width']
        height = image_height * face['FaceDetail']['BoundingBox']['Height']
        left = image_width * face['FaceDetail']['BoundingBox']['Left']
        top = image_height * face['FaceDetail']['BoundingBox']['Top']

        draw = ImageDraw.Draw(image)
        draw.rectangle(((left, top), (left + height, top + width)), outline="red")

        # FIXME font path to change image size in picture
        # what happens when running in the cloud?

        # TODO set font size based on image size
        # if image is too big, font size needs to be bigger
        font_path = "/Library/Fonts/Arial.ttf"
        font = ImageFont.truetype(font_path, 16)

        draw.text((left + 10, top - 10), dom_emotion, fill="yellow", font=font)

    # export image
    # TODO save image in S3
    image.save("/Users/sletic/Pictures/JoGoOut/"+pic_uuid+".jpg", "JPEG")

    return {
        'event_id': event_id,
        'object_id': pic_uuid,
        'total_rek_people': total_people
    }
