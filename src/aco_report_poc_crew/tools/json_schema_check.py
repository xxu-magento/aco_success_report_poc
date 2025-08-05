import jsonschema
from typing import Any, Dict, List, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# This tool validates JSON data against a provided schema.
class SchemaCheckInput(BaseModel):
    json_to_validate: Dict[str, Any] = Field(..., description="JSON produced by one of the tasks")
    schema: Dict[str, Any]       = Field(..., description="Draft-7 JSON schema to validate against")


class JsonSchemaCheck(BaseTool):
    name: str = "json_schema_check"
    description: str = "Validates JSON against a provided schema; returns issue list."
    args_schema: Type[BaseModel] = SchemaCheckInput

    def _run(self, json_to_validate: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        issues = []
        validator = jsonschema.Draft7Validator(schema)
        for error in validator.iter_errors(json_to_validate):
            issues.append(f"{list(error.path)} → {error.message}")
        return issues