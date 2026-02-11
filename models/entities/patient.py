from dataclasses import dataclass
from typing import Literal
from .disease import Disease

Gender = Literal["М", "Ж"]

@dataclass
class Patient:
    fio: str
    gender: Gender
    age: int
    profession: str
    disease: Disease
