from crewai import Crew, Process
from agents import BugAnalysisAgents
from tasks import BugAnalysisTasks
import os

class BugAnalysisCrew:
    def __init__(self):
        self.agents = BugAnalysisAgents()
        self.tasks = BugAnalysisTasks()
    
    def run(self):
        # Initialize agents
        bug_collector = self.agents.bug_collector()
        context_enricher = self.agents.context_enricher()
        analysis_agent = self.agents.analysis_agent()
        reporting_agent = self.agents.reporting_agent()
        
        # Create tasks
        collect_task = self.tasks.collect_bugs_task(bug_collector)
        enrich_task = self.tasks.enrich_context_task(context_enricher)
        analyze_task = self.tasks.analyze_solution_task(analysis_agent)
        report_task = self.tasks.report_results_task(reporting_agent)
        
        # Create crew with sequential process and enhanced verbosity
        crew = Crew(
            agents=[bug_collector, context_enricher, analysis_agent, reporting_agent],
            tasks=[collect_task, enrich_task, analyze_task, report_task],
            process=Process.sequential,
            verbose=True,  # Enable verbose output
            memory=False  # Disable memory for now
        )
        
        return crew.kickoff()