"""Pydantic model for the compressed CompText patient state."""

from pydantic import BaseModel, Field


class PatientState(BaseModel):
    """Compressed patient state object (CompText State Transfer).

    Instead of passing full chat history between agents, patient data
    is compressed into this structured JSON State Object, reducing
    token usage by ~90%.
    """

    chief_complaint: str = Field(
        default="",
        description="Primary reason for the patient visit",
    )
    vitals: dict = Field(
        default_factory=dict,
        description="Patient vital signs (e.g. temperature, heart_rate)",
    )
    symptoms: list = Field(
        default_factory=list,
        description="List of reported symptoms",
    )
    history_summary: str = Field(
        default="",
        description="Brief summary of relevant medical history",
    )
