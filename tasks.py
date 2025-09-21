from crewai import Task
import yaml

class BugAnalysisTasks:
    def __init__(self):
        # Load task configurations from YAML
        with open('config/tasks.yaml', 'r') as f:
            self.task_configs = yaml.safe_load(f)
    
    def collect_bugs_task(self, agent):
        config = self.task_configs['bug_collection_task']
        return Task(
            description=config['description'],
            agent=agent,
            expected_output=config['expected_output'],
            output_file=config.get('output_file')
        )
    
    def enrich_context_task(self, agent):
        config = self.task_configs['context_enrichment_task']
        return Task(
            description=config['description'],
            agent=agent,
            expected_output=config['expected_output'],
            output_file=config.get('output_file')
        )
    
    def analyze_solution_task(self, agent):
        config = self.task_configs['code_analysis_task']
        return Task(
            description=config['description'],
            agent=agent,
            expected_output=config['expected_output'],
            output_file=config.get('output_file')
        )
    
    def report_results_task(self, agent):
        config = self.task_configs['reporting_task']
        return Task(
            description=config['description'],
            agent=agent,
            expected_output=config['expected_output'],
            output_file=config.get('output_file')
        )