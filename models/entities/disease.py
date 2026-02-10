from enum import Enum

class Disease:
    def __init__(self, name, complaints, anamnesis, diagnostics, correct_diagnosis):
        name = name
        complaints = complaints
        anamnesis = anamnesis
        diagnostics = diagnostics
        correct_diagnosis = correct_diagnosis


class DiseaseType(str, Enum):
    DIABETES = "diabetes"
    ANEMIA = "anemia"
    TUBERCULOSIS = "tuberculosis"
    APPENDICITIS = "appendicitis"
    EPILEPSY = "epilepsy"
