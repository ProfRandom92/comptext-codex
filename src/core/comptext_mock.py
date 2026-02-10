"""Mock CompText state compressor using simple heuristics."""

import re

from src.core.schema import PatientState


class StateCompressor:
    """Compress raw patient text into a structured PatientState.

    Uses regex-based heuristics to extract symptoms, vitals, and
    complaint information from free-form text. This mock allows
    running the demo without a GPU-backed model.
    """

    SYMPTOM_KEYWORDS = [
        "headache",
        "fever",
        "cough",
        "nausea",
        "vomiting",
        "fatigue",
        "dizziness",
        "chest pain",
        "shortness of breath",
        "sore throat",
        "runny nose",
        "body aches",
        "chills",
        "diarrhea",
        "abdominal pain",
        "rash",
        "joint pain",
        "muscle pain",
        "back pain",
        "insomnia",
    ]

    TEMPERATURE_PATTERN = re.compile(
        r"(\d{2,3}(?:\.\d)?)\s*°?\s*[CcFf]"
    )
    HEART_RATE_PATTERN = re.compile(
        r"(?:heart\s*rate|hr|pulse)[\s:a-z]*?(\d{2,3})\s*(?:bpm)?",
        re.IGNORECASE,
    )
    BP_PATTERN = re.compile(
        r"(?:blood\s*pressure|bp)[:\s]*(\d{2,3})/(\d{2,3})",
        re.IGNORECASE,
    )
    DURATION_PATTERN = re.compile(
        r"(?:since|for|past)\s+(.+?)(?:\.|,|$)",
        re.IGNORECASE,
    )

    def compress(self, raw_text: str) -> PatientState:
        """Extract structured patient data from raw text.

        Args:
            raw_text: Free-form patient symptom description.

        Returns:
            A PatientState with extracted fields.
        """
        text_lower = raw_text.lower()

        symptoms = [
            kw for kw in self.SYMPTOM_KEYWORDS if kw in text_lower
        ]

        vitals: dict = {}
        temp_match = self.TEMPERATURE_PATTERN.search(raw_text)
        if temp_match:
            unit = "C" if "c" in raw_text[temp_match.end() - 1].lower() else "F"
            vitals["temperature"] = f"{temp_match.group(1)}°{unit}"

        hr_match = self.HEART_RATE_PATTERN.search(raw_text)
        if hr_match:
            vitals["heart_rate"] = f"{hr_match.group(1)} bpm"

        bp_match = self.BP_PATTERN.search(raw_text)
        if bp_match:
            vitals["blood_pressure"] = (
                f"{bp_match.group(1)}/{bp_match.group(2)} mmHg"
            )

        chief_complaint = symptoms[0] if symptoms else "unspecified"

        history_summary = ""
        duration_match = self.DURATION_PATTERN.search(raw_text)
        if duration_match:
            history_summary = (
                f"Symptoms present {duration_match.group(0).strip()}"
            )

        return PatientState(
            chief_complaint=chief_complaint,
            vitals=vitals,
            symptoms=symptoms,
            history_summary=history_summary,
        )
