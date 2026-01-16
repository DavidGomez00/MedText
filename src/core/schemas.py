from typing import List, Literal
from pydantic import BaseModel, Field


class ClinicalEntity(BaseModel):
    text: str = Field(description="El texto exacto extraído de la nota clínica.")
    label: Literal["PROBLEM", "TREATMENT", "TEST", "ANATOMY"] = Field(description="Categoría de la entidad.")
    status: Literal["present", "absent", "possible", "conditional", "historical"] = Field(description="Estado de la afirmación.")
    subject: Literal["patient", "family_member", "other"] = Field(description="Sujeto al que se refiere la entidad.")

class ExtractionResult(BaseModel):
    clinical_entities: List[ClinicalEntity]