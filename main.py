from fastapi import FastAPI,HTTPException, Query, Path
from pydantic import BaseModel, Field,computed_field
from typing import Annotated, Literal, Optional
from fastapi.responses import JSONResponse

import json

app = FastAPI()

# Load and Save the data in the json file
def load_data():
    with open('patients.json','r') as file:
        data = json.load(file)
    return data
def save_data(data):
    with open('patients.json','w') as file:
        json.dump(data,file)

# Creating Pydantic Model to validate the updated details of Patient
class Update_Patient(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int],Field(default=None,gt=0)]
    gender: Annotated[Optional[Literal['Male','Female','Other']],Field(default=None)]
    height: Annotated[Optional[float],Field(default=None,gt=0)]
    weight:  Annotated[Optional[float],Field(default=None,gt=0)]

# Creating Pydantic Model to validate the inserted fiedl
class Patient(BaseModel):
    id: Annotated[str, Field(...,description="Enter the id of the patient", examples=["P001"])]
    name: Annotated[str, Field(...,description="Enter the name of the patient", examples=["Rohit Sharma"])]
    city: Annotated[str, Field(...,description="Enter the city of the patient", examples=["Rohtak"])]
    age: Annotated[int, Field(..., description="Enter the age",gt=0)]
    gender: Annotated[Literal['Male','Female','Other'], Field(...,description="Enter the gender")]
    height: Annotated[float,Field(...,description="Enter the height of the patient")]
    weight: Annotated[float,Field(...,description="Enter the weight of the patient")]

    @computed_field
    @property
    def bmi(self)-> float:
        return round(self.height/(self.weight),2)
    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18:
            return "UnderWeight"
        elif self.bmi < 30:
            return "Normal"
        else:
            return "OverWeight"

 # Home URL   
@app.get("/")
def home():
    return {"message": "Hello"}

# View all the Patient
@app.get("/views")
def views():
    data = load_data()
    return data

# Get the patient details
@app.get("/patient/{Patient_id}")
def patient_data(Patient_id:str = Path(...,description="Enter the Patient ID",example="P001")):
    data = load_data()

    if Patient_id in data:
        return data[Patient_id]
    raise HTTPException(status_code=400,detail="Patient not found")

#Sorting the patient based on Height, Weight and bmi
@app.get("/sorting_patient")
def sorting_patient(sort_by: str = Query(...,description="Sort the patient by height, weight and bmi"),order:str = Query('asc',description="Sort by asc or desc")):
    data = load_data()
    valid_states = ['height','weight','bmi']
    if sort_by not in valid_states:
        raise HTTPException(status_code=400, detail=f"You have not given valid {sort_by} states")
    
    sort_order = True if order == 'desc' else False
    sorted_data = sorted(data.values(),key = lambda x:x.get('height', 0),reverse=sort_order)
    return sorted_data

# Create new patient details
@app.post("/create")
def create_patient(patient:Patient):

    # load the data
    data = load_data()

    # Check if patient id exist or not
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exist")
    
    # Add new patient to the database
    data[patient.id] = patient.model_dump(exclude = ['id'])

    # save the data
    save_data(data)

    # return response to user
    return JSONResponse(status_code=201, content={'message':'Patient details has been added successfully'})

# Update the Patient details  
@app.put("/update/{patient_id}")
def update_patient_details(patient_id:str, update_patient: Update_Patient ):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail=f"Patient id: {patient_id} not found")
    
    existing_patient_info = data[patient_id]

    update_patient_info = update_patient.model_dump(exclude_unset=True)

    for key, value in update_patient_info.items():
        existing_patient_info[key] = value
    
     # Ensure all required fields exist (fill missing ones with old values)
    required_fields = {"name", "city", "age", "gender", "height", "weight"}
    for field in required_fields:
        if field not in existing_patient_info:
            if field in data[patient_id]:  # Use old value if available
                existing_patient_info[field] = data[patient_id][field]
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

    existing_patient_info['id'] = patient_id
    patient_pydantic_object = Patient(**existing_patient_info)
    existing_patient_info = patient_pydantic_object.model_dump(exclude='id')

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Successfully update the Patient detail'})

@app.put("/delete_patient/{patient_id}")
def delete_patient(patient_id:int):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=400, detail=f"Patient id: {patient_id} not found")
    
    del data[patient_id]
    save_data(data=data)
    return JSONResponse(status_code=200, content={'message': 'Successfully deleted the Patient detail'})
