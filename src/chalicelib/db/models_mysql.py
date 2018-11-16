import os
import uuid

import peewee
from peewee import *

from chalicelib import get_stage

def generate_uuid():
    return str(uuid.uuid4())

db_name = '{}_jogo_db'.format(get_stage())
db = peewee.MySQLDatabase(
    db_name,
    user="adminsletic",
    password="ZgSd8epmKymkbBZ9",
    host="sajogodb.cq66ndcmzkl3.us-east-1.rds.amazonaws.com",
    port=3306
)

class DetectedPeopleModel(peewee.Model):
    event_id = peewee.CharField()
    object_id = peewee.CharField()
    face_id = peewee.CharField()
    timestamp = peewee.TimestampField()
    dominant_emotion = peewee.CharField()
    dominant_emotion_score = peewee.DoubleField()
    smile = peewee.BooleanField()
    smile_score = peewee.DoubleField()
    age_low = peewee.DecimalField()
    age_high = peewee.DecimalField()
    gender = peewee.CharField()
    gender_score = peewee.DoubleField()

    class Meta:
        database = db
        # indexes = (
        #     (('event_id', 'object_id', 'face_id'), True),
        # )
