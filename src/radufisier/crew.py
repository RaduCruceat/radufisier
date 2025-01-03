from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.radufisier.FoodTrackingCrew import FoodTrackingCrew
import os
from dotenv import load_dotenv
import json
from crewai_tools import FileWriterTool,FileReadTool
from crewai.tools.structured_tool import CrewStructuredTool
from pydantic import BaseModel

class FoodTrackingInput(BaseModel):
    food_items: list 

def food_tracking_wrapper(food_items: list, **kwargs):
    load_dotenv()
    edamam_app_id = os.getenv("EDAMAM_APP_ID")
    edamam_api_key = os.getenv("EDAMAM_API_KEY")
    app = FoodTrackingCrew(edamam_app_id, edamam_api_key)
    results = app.track_multiple_food_items(food_items)
    return results

def create_food_tracking_tool():
    return CrewStructuredTool.from_function(
        name="Food Tracking Tool",
        description="Track nutritional information for a list of food items using the Edamam API.",
        args_schema=FoodTrackingInput,
        func=food_tracking_wrapper,
    )

@CrewBase
class Radufisier():
    """Radufisier crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        load_dotenv()
        self.food_list = ["100g of rice", "100g of chocolate"]
        self.food_tracking_data = self.write_food_data_to_file()

    def write_food_data_to_file(self):
        file_writer_tool = FileWriterTool()
        food_tracking_tool = create_food_tracking_tool()
        food_tracking_data = food_tracking_tool._run(food_items=self.food_list)
        filename = 'FoodList.json'

        print(f"Writing data into: {filename}")
        with open(filename, 'w') as f:
            json.dump(food_tracking_data, f, indent=4)

        file_data = {
            'filename': filename,
            'content': food_tracking_data
        }
        file_writer_tool._run(content=file_data)
        
        file_tool = FileReadTool()
        foodFile=file_tool.run(file_path= "C:\\Users\\Radu\\radufisier\\FoodList.json")
        print(foodFile)
        return filename  
    
    @agent
    def calorie_calculator(self) -> Agent:
        return Agent(
            config=self.agents_config['calorie_calculator'],
            verbose=True,
            tools=[FileReadTool()]
        )

    @agent
    def protein_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['protein_analyzer'],
            verbose=True,
            tools=[FileReadTool()]
        )

    @agent
    def foods_analyser(self) -> Agent:
       
        return Agent(
            config=self.agents_config['foods_analyser'],
            verbose=True,
            tools=[FileReadTool()]
        )

    @task
    def calorie_calculation_task(self) -> Task:
        return Task(
            config=self.tasks_config['calorie_calculation_task'],
            output_file='AnalyzerCalorieCalculator.md'
        )

    @task
    def protein_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['protein_analysis_task'],
            output_file='AnalyzerProtein.md'
        )

    @task
    def foods_analyser_task(self) -> Task:
        return Task(
            config=self.tasks_config['foods_analyser_task'],
            output_file='AnalyzerFoodItems.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
