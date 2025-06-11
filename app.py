from fastapi import FastAPI , Path , HTTPException , Query
import json
from pydantic import BaseModel , Field , computed_field
from typing import Annotated , Literal , Optional
from fastapi.responses import JSONResponse

class Patient(BaseModel):
    id : Annotated[str , Field(... , description = "Id of the patient" , examples = ["P001" , "P002"])]
    name : Annotated[str , Field(... , description = "Name of the patient")]
    city : Annotated[str , Field(... , description = "Name of the city")]
    age : Annotated[int , Field(... , description = "Age of patient" , gt = 0 , lt = 100)]
    gender : Annotated[Literal['male' , 'female' , 'others'] , Field(... , description = "Gender of the patient")]
    height : Annotated[float , Field(... , description = "Height of patient" , gt = 0)]
    weight : Annotated[float , Field(... , description = "Weight of patient" , gt = 0)] 

    @computed_field
    @property
    def bmi(self) -> float:
        return round((self.weight / ((self.height)**2)),2)

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight" 
        elif self.bmi >= 18.5 and self.bmi < 25:
            return "Normal"
        elif self.bmi >= 25 and self.bmi <= 30:
            return "Overweight"
        else:
            return "Obese"
        


class Patient_Updated(BaseModel):
    name : Annotated[Optional[str] , Field(... , description = "Name of the patient")]
    city : Annotated[Optional[str] , Field(... , description = "Name of the city")]
    age : Annotated[Optional[int] , Field(... , description = "Age of patient" , gt = 0 , lt = 100)]
    gender : Annotated[Optional[Literal['male' , 'female' , 'others']] , Field(... , description = "Gender of the patient")]
    height : Annotated[Optional[float] , Field(... , description = "Height of patient" , gt = 0)]
    weight : Annotated[Optional[float] , Field(... , description = "Weight of patient" , gt = 0)] 

app = FastAPI()

with open('./patients.json' , 'r') as f:
    data = json.load(f)

@app.get('/')
def home():
    return {'msg' : 'This is the home page'}

@app.get('/view')
def view():
    global data
    return data

@app.get('/view/sort')
def view_patients_query(sort_by : str = Query(... , description = 'Field to filter the patients details by' ) , order_by : str = Query('asc' , description = 'order in which to sort')):
    global data

    sort_fields = ['age' , 'height' , 'weight' , 'bmi']
    order = ['asc' , 'desc']

    if sort_by.lower() not in sort_fields:
        raise HTTPException(status_code = 404 , detail = f"Sort only by the fields {sort_fields}")
    
    if order_by.lower() not in order:
        raise HTTPException(status_code = 404 , detail = f"Order only by the fields {order}")
    
    result = {} 

    for patient_id in data.keys():
        result[patient_id] = data[patient_id][sort_by]

    reverse_order = order_by.lower() == 'desc'
    sorted_res = [(key, result[key]) for key in sorted(result, key=result.get, reverse=reverse_order)]
    return sorted_res 

@app.get('/view/{patient_id}')
def view_patient(patient_id : str = Path(... , description = "This shows the information of a particular patient" , example = ['P001' , 'P002'])):
    global data
    if patient_id not in data.keys():
        raise HTTPException(status_code = 404 , detail = "Invalid Patient ID")
    return data[patient_id]


    
@app.post('/create')
def create_patient(patient : Patient):
    global data
    
    if patient.id in data.keys():
        raise HTTPException(status_code = 400 , detail = "Patient already exists")
    
    data[patient.id] = patient.model_dump(exclude=["id"])

    with open('patients.json' , 'w') as f:
        json.dump(data , f) 
    
    return JSONResponse(status_code = 201 , content = "Patient added to the database successully")


@app.put('/edit/{param_id}')
def update_patient(patient_id : str , updated_patient : Patient_Updated):
    global data

    if patient_id not in data.keys():
        raise HTTPException(status_code = 404 , detail = "No patient found with the given id")
    
    existing_info = data[patient_id]
    updated_info = updated_patient.model_dump(exclude_unset = True)

    for key , value in updated_info.items():
        existing_info[key] = value

    existing_info['id'] = patient_id
    pydantic_patient = Patient(**existing_info)
    updated_patient = pydantic_patient.model_dump(exclude = ['id'])

    data[patient_id] = updated_patient

    with open('patients.json' , 'w') as f:
        json.dump(data , f) 

    return JSONResponse(status_code = 200 , content = f"Updated patient {patient_id}")


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    global data

    if patient_id not in data.keys():
        raise HTTPException(status_code = 404 , detail = "No patient found with this ID")
    
    del data[patient_id]

    with open('patients.json' , 'w') as f:
        json.dump(data , f) 

    return JSONResponse(status_code = 200 , content = f"Deleted patient {patient_id}")



