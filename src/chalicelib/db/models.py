import os
import uuid

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute
from pynamodb.models import Model

from chalicelib import get_stage

def generate_uuid():
    return str(uuid.uuid4())

class DetectedPeopleModel(Model):
    event_id = UnicodeAttribute(hash_key=True)
    object_id = UnicodeAttribute(default=generate_uuid)
    face_id = UnicodeAttribute(null=False)
    dominant_emotion = UnicodeAttribute(null=False)
    dominant_emotion_score = NumberAttribute(null=False)
    smile = BooleanAttribute(null=False)
    smile_score = NumberAttribute(null=False)
    age_low = NumberAttribute(null=True)
    age_high = NumberAttribute(null=True)
    gender = BooleanAttribute(null=True)
    gender_score = NumberAttribute(null=True)

    class Meta:
        table_name = '{}-detected-people'.format(get_stage())

        if 'DYNAMODB_HOST' in os.environ:
            host = os.environ['DYNAMODB_HOST']
