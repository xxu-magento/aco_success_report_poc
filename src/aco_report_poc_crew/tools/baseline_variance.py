import statistics
from typing import List, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# This tool computes the standard deviation of a list of baseline KPI values.
class VarianceInput(BaseModel):
    """Window of baseline KPI values (at least 4, ideally 7+)."""
    baseline_values: List[float] = Field(..., min_items=3)


class BaselineVariance(BaseTool):
    name: str = "baseline_variance"
    description: str = "Computes standard deviation of baseline KPI values."
    args_schema: Type[BaseModel] = VarianceInput


    def _run(self, baseline_values: List[float]) -> float:
        return round(statistics.stdev(baseline_values), 4)
