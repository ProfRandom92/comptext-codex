"""Nurse agent: intake and compression of patient data."""

from src.core.comptext_mock import StateCompressor
from src.core.schema import PatientState


class NurseAgent:
    """Intake agent that converts raw patient text to a PatientState.

    Acts as the first stage in the CompText State Transfer pipeline,
    compressing free-form text into a structured JSON object.
    """

    def __init__(self) -> None:
        self._compressor = StateCompressor()

    def intake(self, raw_text: str) -> PatientState:
        """Process raw patient input and return a compressed state.

        Args:
            raw_text: Free-form symptom description from the patient.

        Returns:
            A structured PatientState object.
        """
        return self._compressor.compress(raw_text)
