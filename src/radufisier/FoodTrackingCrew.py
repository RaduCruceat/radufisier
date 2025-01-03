import requests

class FoodTrackingCrew:
    def __init__(self, edamam_app_id, edamam_api_key):
        """
        Initialize the FoodTrackingCrew with API credentials.
        This class can be called from other classes to track food items.
        """
        self.EDAMAM_APP_ID = edamam_app_id
        self.EDAMAM_API_KEY = edamam_api_key
        self.food_log = {
            'items': [],
            'total_calories': 0,
            'total_protein': 0,
            'total_fat': 0,
            'total_sugar': 0
        }
    
    def get_nutrition_info(self, food_item):
        """Get nutrition information for a food item from Edamam API."""
        url = f'https://api.edamam.com/api/nutrition-data?app_id={self.EDAMAM_APP_ID}&app_key={self.EDAMAM_API_KEY}&ingr={food_item}'
        response = requests.get(url)
        return response.json()
    
    def track_food_item(self, food_item):
        """Track a single food item and update the food log."""
        nutrition_data = self.get_nutrition_info(food_item)
        
        # Extract relevant nutritional information
        calories = nutrition_data.get('calories', 0)
        protein = nutrition_data.get('totalNutrients', {}).get('PROCNT', {}).get('quantity', 0)
        fat = nutrition_data.get('totalNutrients', {}).get('FAT', {}).get('quantity', 0)
        sugar = nutrition_data.get('totalNutrients', {}).get('SUGAR', {}).get('quantity', 0)
        
        # Log the food item and its nutritional content
        item_info = {
            'item': food_item,
            'calories': round(calories),
            'protein_g': round(protein, 2),
            'fat_g': round(fat, 2),
            'sugar_g': round(sugar, 2)
        }
        self.food_log['items'].append(item_info)
        self.food_log['total_calories'] += calories
        self.food_log['total_protein'] += protein
        self.food_log['total_fat'] += fat
        self.food_log['total_sugar'] += sugar

        return item_info
    
    def track_multiple_food_items(self, food_items):
        """
        Track a list of food items and return the results.
        
        Args:
        - food_items (list of str): List of food items to track.
        
        Returns:
        - List of results with nutritional details for each item.
        """
        results = []
        for food_item in food_items:
            try:
                result = self.track_food_item(food_item)
                results.append(result)
            except Exception as e:
                results.append({
                    'item': food_item,
                    'error': str(e)
                })
        return results

