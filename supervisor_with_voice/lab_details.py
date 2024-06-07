def get_X_ray_timetable():
    X_Ray_timetable = {
        "test_name": "Tooth X-ray",
        "cost": 450,
        "available_time_slots": {
            "21-05-2024": [
                { "fromTime": "7:00AM", "toTime": "8:00AM" },
                { "fromTime": "1:00PM", "toTime": "2:00PM" }
            ]
        },
        "booked_time_slots": {
            "21-05-2024": [
                { "fromTime": "3:00PM", "toTime": "5:00PM" }
            ]
        }
    }
    return X_Ray_timetable
