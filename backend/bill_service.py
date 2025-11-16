import os
import base64
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

load_dotenv()

class BillService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use gemini-pro-vision for image analysis
        self.model = genai.GenerativeModel('gemini-2.5-pro')
    
    def parse_bill_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Parse a bill image using Gemini Vision API
        Returns structured data with items, quantities, prices, tax, and tip
        """
        try:
            from PIL import Image
            import io
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Create prompt for Gemini
            prompt = """
            Analyze this receipt/bill image and extract the following information in JSON format:
            
            {
                "items": [
                    {
                        "name": "item name",
                        "quantity": number,
                        "price": number (price per unit)
                    }
                ],
                "subtotal": number,
                "tax": number,
                "tip": number,
                "total": number
            }
            
            Rules:
            - Extract ALL items with their names, quantities, and unit prices
            - If quantity is not specified, assume 1
            - Separate tax and tip from the subtotal
            - If tip is not present, set it to 0
            - All prices should be positive numbers
            - Return ONLY valid JSON, no additional text
            """
            
            # Generate content with image
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*$', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            parsed_data = json.loads(response_text)
            
            # Validate and add default values
            if 'items' not in parsed_data:
                parsed_data['items'] = []
            
            # Add selected and splitBy fields to each item
            for item in parsed_data['items']:
                item['selected'] = True  # Default to selected
                item['splitBy'] = 1  # Default split by 1
                
                # Ensure required fields
                if 'quantity' not in item:
                    item['quantity'] = 1
                if 'price' not in item:
                    item['price'] = 0
            
            # Ensure all required fields exist
            if 'subtotal' not in parsed_data:
                parsed_data['subtotal'] = sum(item['price'] * item['quantity'] for item in parsed_data['items'])
            
            if 'tax' not in parsed_data:
                parsed_data['tax'] = 0
            
            if 'tip' not in parsed_data:
                parsed_data['tip'] = 0
            
            if 'total' not in parsed_data:
                parsed_data['total'] = parsed_data['subtotal'] + parsed_data['tax'] + parsed_data['tip']
            
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            print(f"Error parsing bill: {e}")
            raise ValueError(f"Failed to parse bill image: {str(e)}")
    
    def calculate_split_amount(
        self, 
        items: List[Dict[str, Any]], 
        tax: float, 
        tip: float
    ) -> float:
        """
        Calculate the amount for selected items with proportional tax and tip
        """
        # Calculate total of selected items
        selected_total = sum(
            item['price'] * item['quantity'] / item.get('splitBy', 1)
            for item in items
            if item.get('selected', False)
        )
        
        # Calculate total of all items
        all_items_total = sum(
            item['price'] * item['quantity']
            for item in items
        )
        
        # Calculate proportion
        if all_items_total > 0:
            proportion = selected_total / all_items_total
        else:
            proportion = 0
        
        # Add proportional tax and tip
        proportional_tax = tax * proportion
        proportional_tip = tip * proportion
        
        return selected_total + proportional_tax + proportional_tip
