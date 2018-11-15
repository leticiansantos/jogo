import logging
import base64
import boto3
import uuid

import requests
from chalice import Chalice, Response, BadRequestError

from chalicelib import get_stage

app = Chalice(app_name='concierge-api')
app.debug = True
app.log.setLevel(logging.DEBUG)

from chalicelib.db.models import SampleModel

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

@app.route('/upload', methods=['POST'])
def upload_picture():
    if app.current_request.json_body.get('uuid'):
        user_uuid = app.current_request.json_body['uuid']
    else:
        user_uuid = str(uuid.uuid4())
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
        Key='selfies/{}.jpg'.format(user_uuid),
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
                'Name': 'selfies/{}.jpg'.format(user_uuid),
            },
        },
    )

    return response

    # if not len(response['FaceRecords']) > 0:
    #     raise BadRequestError('Could not find valid faces')
    #
    # rekognition_face_id = response['FaceRecords'][0]['Face']['FaceId']
    #
    # return {
    #     'uuid': user_uuid,
    #     'face_id': rekognition_face_id
    # }
