from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.radufisier.FoodTrackingCrew import FoodTrackingCrew
import os
from dotenv import load_dotenv
import json
from crewai_tools import FileWriterTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Radufisier():
    """Radufisier crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize the crew and fetch food tracking data."""
        load_dotenv()
        self.food_list = ["19 cherry", "1 slice bread"]
      
        self.food_tracking_data = self.write_food_data_to_file()

    def write_food_data_to_file(self):
        """Fetch food tracking data and write it to a file."""
        file_writer_tool = FileWriterTool()
        edamam_app_id = os.getenv('EDAMAM_APP_ID')
        edamam_api_key = os.getenv('EDAMAM_API_KEY')
        
        food_tracking_data = self.get_food_data(edamam_app_id, edamam_api_key)
        filename = 'food_tracking_data.json'

        print(f"Writing data into: {filename}")
        with open(filename, 'w') as f:
            json.dump(food_tracking_data, f, indent=4) 

        file_data = {
            'filename': filename,
            'content': food_tracking_data
        }
        file_writer_tool._run(content=file_data)
        #self.write_to_file(filename, food_tracking_data)
        return food_tracking_data
        
    def get_food_data(self, app_id, api_key):
        """Fetch data from FoodTrackingCrew API."""
        app = FoodTrackingCrew(app_id, api_key)
        results = app.track_multiple_food_items(self.food_list)
        return results

    def write_to_file(self, filename, content):
        """Write the content to a file (e.g., JSON or text)."""
        #with open(filename, 'w') as f:
            #json.dump(content, f, indent=4)  # Writing food tracking data as JSON
        #print(f"Data written to {filename}")

    @agent
    def calorie_calculator(self) -> Agent:
        return Agent(
            config=self.agents_config['calorie_calculator'],
            verbose=True
        )

    @agent
    def protein_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['protein_analyzer'],
            verbose=True
        )
    
    # New foods_analyser agent
    @agent
    def foods_analyser(self) -> Agent:
        return Agent(
            config=self.agents_config['foods_analyser'],
            verbose=True
        )

    @task
    def calorie_calculation_task(self) -> Task:
        print(self.food_tracking_data)
        return Task(
            config=self.tasks_config['calorie_calculation_task'],
            output_file='report.md'
        )

    @task
    def protein_analysis_task(self) -> Task:
        print(self.food_tracking_data)
        return Task(
            config=self.tasks_config['protein_analysis_task'],
            output_file='report.md'
        )

    # New foods_analyser_task
    @task
    def foods_analyser_task(self) -> Task:
        print(self.food_tracking_data)
        return Task(
            config=self.tasks_config['foods_analyser_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Radufisier crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
