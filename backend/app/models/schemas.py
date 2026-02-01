from pydantic import BaseModel
from typing import Optional

class MemoInput(BaseModel):
    text: str

class QueryInput(BaseModel):
    question: str

class PersonData(BaseModel):
    name: str
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class CompanyData(BaseModel):
    name: str

class ContactInput(BaseModel):
    person_data: PersonData
    company_data: Optional[CompanyData] = None
