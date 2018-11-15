from .models import DetectedPeopleModel
from .models_mysql import DetectedPeopleModel as SQLDetectedPeopleModel

## RDS
SQLDetectedPeopleModel.create_table()

## DDB
if not DetectedPeopleModel.exists():
    DetectedPeopleModel.create_table(
        read_capacity_units=1,
        write_capacity_units=1,
        wait=True,
    )
