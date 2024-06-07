def get_doctor_calendar():
    todays_timetable = {
        "doctor_name": "Dr.Aryan",
        "available_time_slots": {
            "21-05-2024": [
                { "fromTime": "8:00AM", "toTime": "10:00AM" },
                { "fromTime": "12:00PM", "toTime": "2:00PM" }
            ]
        },
        "booked_time_slots": {
            "21-05-2024": [
                { "fromTime": "3:00PM", "toTime": "5:00PM" }
            ]
        }
    }
    return todays_timetable
