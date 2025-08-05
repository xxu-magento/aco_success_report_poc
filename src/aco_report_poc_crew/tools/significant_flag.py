from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# This tool determines if the change in a KPI is statistically significant.
class SigFlagInput(BaseModel):
    delta: float = Field(..., description="Percent change from delta_calc")
    baseline_stdev: float = Field(..., gt=0, description="Stdev from baseline_variance")


class SignificanceFlag(BaseTool):
    name: str = "significance_flag"
    description: str = "Returns True if |delta| > 3 x baseline_stdev."
    args_schema: Type[BaseModel] = SigFlagInput

    def _run(self, delta: float, baseline_stdev: float) -> bool:
        return abs(delta) > (3 * baseline_stdev)
