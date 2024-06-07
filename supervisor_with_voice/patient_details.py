patients = [
    {
        "name": "Tejas Kale",
        "age": 23,
        "email": "tejas.kale@gmail.com"
    },
    {
        "name": "Jane Smith",
        "age": 25,
        "email": "jane.smith@example.com"
    },
    {
        "name": "Alice Johnson",
        "age": 35,
        "email": "alice.johnson@example.com"
    }
]

def get_patients_array():
    return patients

# def get_patiant_details_tool(patient_name: str, patient_age: int, patient_email: str = None):
#     """
#     Retrieve patient details based on provided name, age, and optional email.

#     Args:
#         patient_name (str): Full name of the patient.
#         patient_age (int, optional): Age of the patient. Defaults to None.
#         patient_email (str, optional): Email of the patient. Defaults to None.

#     Returns:
#         dict: Patient details if a match is found, None otherwise.
#     """
#     if patient_name != None and patient_age != None:
#         first_name, last_name = patient_name.split()
#         for patient in get_patients_array():
#             patient_first_name, patient_last_name = patient["name"].split()
#             print(f'patient first name: {patient_first_name}, last name: {patient_last_name}')
#             if (patient_first_name.lower() == first_name.lower() and 
#                 patient_last_name.lower() == last_name.lower() and 
#                 patient["age"] == patient_age):
#                 if patient_email is not None:
#                     if patient["email"].lower() == patient_email.lower():
#                         return "patient identified as regular patient"
#                     else:
#                         continue  # Email does not match, continue to the next patient
#                 return patient  # No email provided, match found with name and age only
#     else:
#         return 'appropriate details not provided'
#     return None

# print(get_patiant_details_tool('Tejas Kale',23))
