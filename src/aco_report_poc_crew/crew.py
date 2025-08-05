# ACO Report PoC Crew

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

import openai
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, tool
from crewai.agents.agent_builder.base_agent import BaseAgent

from .config import agents_config, tasks_config
from .tools import TOOLS  # unified list of BaseTool instances
from .tools import DeltaCalc, BaselineVariance, SignificanceFlag, JsonSchemaCheck, ReferenceMatcher, ComplianceLinter

# # -------------------- Azure OpenAI client -------------------------------
# client = openai.AzureOpenAI(
#     azure_endpoint=os.getenv("AZURE_API_BASE"),
#     api_key=os.getenv("AZURE_API_KEY"),
#     api_version=os.getenv("AZURE_API_VERSION"),
# ) 
# # Test the connection
# try:
#    client.chat.completions.create(
#        model=os.getenv("MODEL"),
#        messages=[{"role": "system", "content": "Test connection"}],
#    )
# except Exception as e:
#    raise RuntimeError(f"Failed to connect to Azure OpenAI: {e}")

# # -------------------- ACO Report PoC Crew --------------------------------
llm = LLM(
    model=os.getenv("MODEL"),
    base_url=os.getenv("AZURE_API_BASE"),
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    # timeout=60,
    temperature=0.0,  # deterministic output
)


@CrewBase
class AcoReportPocCrew():
    """Impact Analyzer → Story Generator → Validator → (optional) Corrector"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def save_combine_stories_callback(self, output: TaskOutput):
        """Save success stories to cache"""
        # self.cache.put_item_in_cache("final_stories.json", output.raw)
        out_file = Path(f"combine_report_test.txt")
        out_file.write_text(output.raw)

    def save_validate_stories_callback(self, output: TaskOutput):
        """Save success stories to cache"""
        # self.cache.put_item_in_cache("final_stories.json", output.raw)
        out_file = Path(f"validate_report_test.txt")
        out_file.write_text(output.raw)

    def save_correct_stories_callback(self, output: TaskOutput):
        """Save success stories to cache"""
        # self.cache.put_item_in_cache("final_stories.json", output.raw)
        out_file = Path(f"correct_report_test.txt")
        out_file.write_text(output.raw)

    @tool
    def delta_calc(self):
        return DeltaCalc()

    @tool
    def baseline_variance(self):
        return BaselineVariance()

    @tool
    def significance_flag(self):
        return SignificanceFlag()

    @tool
    def json_schema_check(self):
        return JsonSchemaCheck()

    @tool
    def reference_matcher(self):
        return ReferenceMatcher()

    @tool
    def compliance_linter(self):
        return ComplianceLinter()
    # ---------------- AGENTS -------------------------------------------

    @agent
    def impact_analyzer_agent(self) -> Agent:
        return Agent(
            config=agents_config["impact_analyzer_agent"],
            tools=TOOLS, #[json_schema_check],
            verbose=True,
            llm=llm,  # use shared LLM instance
        )

    @agent
    def story_generator_agent(self) -> Agent:
        return Agent(
            config=agents_config["story_generator_agent"],
            verbose=True,
            llm=llm,  # use shared LLM instance
        )

    @agent
    def report_validator_agent(self) -> Agent:
        return Agent(
            config=agents_config["report_validator_agent"],
            tools=TOOLS,
            verbose=True,
            llm=llm,  # use shared LLM instance
        )

    @agent
    def report_corrector_agent(self) -> Agent:
        return Agent(
            config=agents_config["report_corrector_agent"],
            tools=TOOLS,  # json_schema_check for self-validation
            verbose=True,
            llm=llm,  # use shared LLM instance
        )

    # ---------------- TASKS --------------------------------------------

    @task
    def analyze_impact_attribution_task(self) -> Task:
        return Task(config=self.tasks_config["analyze_impact_attribution_task"])

    @task
    def generate_top_highlights_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_top_highlights_task"],
            input_results=[self.analyze_impact_attribution_task],
        )

    @task
    def generate_dimension_pages_task(self) -> Task:
        return Task(
            config=self.tasks_config["generate_dimension_pages_task"],
            input_results=[self.analyze_impact_attribution_task],
        )

    @task
    def combine_stories_task(self) -> Task:
        return Task(
            config=self.tasks_config["combine_stories_task"],
            input_results=[
                self.generate_top_highlights_task,
                self.generate_dimension_pages_task,
            ],
            callback=self.save_combine_stories_callback,
        )    

    @task
    def validate_final_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["validate_final_report_task"],
            input_results=[
                self.combine_stories_task,
                self.analyze_impact_attribution_task,
            ],
            callback=self.save_validate_stories_callback,
        )

    @task
    def correct_report_with_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config["correct_report_with_validation_task"],
            input_results=[
                self.combine_stories_task,
                self.validate_final_report_task,
            ],
            callback=self.save_correct_stories_callback,
        )

    # ---------------- CREW ---------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Sequential execution with optional correction."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
