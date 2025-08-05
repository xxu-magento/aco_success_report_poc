from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# This tool calculates the percentage change between two average KPI values.
# It is used to determine the impact of changes in KPIs over time.
class DeltaCalcInput(BaseModel):
    """Average KPI values baseline and comparison time windows."""
    baseline_avg: float = Field(..., gt=0, description="Average value in the BASELINE window")
    comparison_avg: float = Field(..., description="Average value in the COMPARISON window")


class DeltaCalc(BaseTool):
    name: str = "delta_calc"
    description: str = "Returns rounded percent change between BASELINE and COMPARISON averages."
    args_schema: Type[BaseModel] = DeltaCalcInput

    def _run(self, baseline_avg: float, comparison_avg: float) -> float:
        delta = ((comparison_avg - baseline_avg) / baseline_avg) * 100
        return round(delta, 1)
