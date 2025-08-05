from .delta_calc import DeltaCalc
from .baseline_variance import BaselineVariance
from .significant_flag import SignificanceFlag
from .json_schema_check import JsonSchemaCheck
from .reference_matcher import ReferenceMatcher
from .compliance_linter import ComplianceLinter

# TOOLS = [
#     DeltaCalc(),
#     BaselineVariance(),
#     SignificanceFlag(),
#     JsonSchemaCheck(),
#     ReferenceMatcher(),
#     ComplianceLinter(),
# ]


# one instance per tool
delta_calc         = DeltaCalc()
baseline_variance  = BaselineVariance()
significance_flag  = SignificanceFlag()
json_schema_check  = JsonSchemaCheck()

# export a list CrewAI can consume
TOOLS = [
    delta_calc,
    baseline_variance,
    significance_flag,
    json_schema_check,
]