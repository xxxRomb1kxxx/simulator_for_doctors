from dataclasses import dataclass
from enum import Enum
from typing import List

class DiseaseType(str, Enum):
    DIABETES = "diabetes"
    ANEMIA = "anemia"
    TUBERCULOSIS = "tuberculosis"
    APPENDICITIS = "appendicitis"
    EPILEPSY = "epilepsy"

@dataclass
class Disease:
    name: str
    complaints: List[str]
    anamnesis: List[str]
    diagnostics: List[str]
    correct_diagnosis: str
