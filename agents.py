from crewai import Agent, LLM
from tools import (
    get_jira_bugs, get_jira_issue_details, get_linked_jira_issues,
    analyze_entire_codebase, analyze_bug_with_gemini, generate_bug_solution,
    generate_comprehensive_report, add_jira_comment
)
import os
import yaml

class BugAnalysisAgents:
    def __init__(self):
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            os.environ['GOOGLE_API_KEY'] = gemini_key
            self.llm = LLM(
                model="gemini/gemini-1.5-flash",
                api_key=gemini_key
            )
        else:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Load agent configurations from YAML
        with open('config/agents.yaml', 'r') as f:
            self.agent_configs = yaml.safe_load(f)
    
    def bug_collector(self):
        config = self.agent_configs['bug_collector']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[get_jira_bugs, get_jira_issue_details],
            llm=self.llm,
            verbose=True
        )
    
    def context_enricher(self):
        config = self.agent_configs['context_enricher']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[get_linked_jira_issues, analyze_entire_codebase],
            llm=self.llm,
            verbose=True
        )
    
    def analysis_agent(self):
        config = self.agent_configs['analysis_agent']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[analyze_bug_with_gemini, generate_bug_solution],
            llm=self.llm,
            verbose=True
        )
    
    def reporting_agent(self):
        config = self.agent_configs['reporting_agent']
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            tools=[generate_comprehensive_report, add_jira_comment],
            llm=self.llm,
            verbose=True
        )