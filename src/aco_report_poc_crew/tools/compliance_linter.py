import re
from typing import List, Type, ClassVar
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# This tool checks narrative strings for prohibited phrases that could mislead or violate compliance.
# It flags phrases like guarantees, PII references, and other misleading terms.
# It helps ensure that the narrative content adheres to compliance standards and does not mislead readers.
class LinterInput(BaseModel):
    """Input for the compliance linter tool."""
    sentences: List[str] = Field(..., description="Narrative strings to lint")


class ComplianceLinter(BaseTool):
    name: str = "compliance_linter"
    description: str = "Flags prohibited or misleading phrases (guarantees, PII, etc.)."
    args_schema: Type[BaseModel] = LinterInput

    PROHIBITED_PATTERNS: ClassVar[List[str]] = [
        r"\bguaranteed\b",
        r"\b100%+\b",
        r"\bunlimited profits?\b",
        r"\bSSN\b",  # PII example
    ]


    def _run(self, sentences: List[str]) -> List[str]:
        issues = []
        for idx, sent in enumerate(sentences):
            for pat in self.PROHIBITED_PATTERNS:
                if re.search(pat, sent, flags=re.IGNORECASE):
                    issues.append(f"Sentence {idx+1}: contains prohibited phrase '{pat}'")
        return issues
