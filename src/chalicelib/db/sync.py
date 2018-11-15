from .models import DetectedPeopleModel

if not DetectedPeopleModel.exists():
    DetectedPeopleModel.create_table(
        read_capacity_units=1,
        write_capacity_units=1,
        wait=True,
    )
