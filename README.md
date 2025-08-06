# AcoReportPocCrew Crew

Welcome to the AcoReportPocCrew Crew project, powered by [crewAI](https://crewai.com). 

## High Level Design for this project
https://wiki.corp.adobe.com/pages/viewpage.action?pageId=3568266588

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to the project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file** There is an .env.example file to show the exacmple content.

- Modify `src/aco_report_poc_crew/config/agents.yaml` to define the agents
- Modify `src/aco_report_poc_crew/config/tasks.yaml` to define the tasks
- Modify `src/aco_report_poc_crew/config.py` to define the configurations
- Modify `src/aco_report_poc_crew/crew.py` to add more logic, tools and specific args
- Modify `src/aco_report_poc_crew/main.py` to add custom inputs for the agents and tasks
- Modify `src/aco_report_poc_crew/debug.py` to add custom debug
- Modify `src/aco_report_poc_crew/jsonparser.py` to do data pre-processing or post-processing 
- Modify `schemas/...` to add more schemas for agent & task output validation 

## Running the Project

To kickstart the crew of AI agents and begin task execution, run this from the root folder of the project:

```bash
$ crewai run
```
or
```bash
$ python -m aco_report_poc_crew.main
```

This command initializes the ACO_Report_POC_crew Crew, assembling the agents and assigning them tasks as defined in the configuration.

## Understanding the Crew

The ACO_Report_POC_crew Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in the crew.