from enum import Enum
class Disease:
    def __init__(self, name, complaints, anamnesis, diagnostics, correct_diagnosis):
        self.name = name
        self.complaints = complaints
        self.anamnesis = anamnesis
        self.diagnostics = diagnostics
        self.correct_diagnosis = correct_diagnosis


class DiseaseType(str, Enum):
    DIABETES = "diabetes"
    ANEMIA = "anemia"
    TUBERCULOSIS = "tuberculosis"
    APPENDICITIS = "appendicitis"
    EPILEPSY = "epilepsy"
