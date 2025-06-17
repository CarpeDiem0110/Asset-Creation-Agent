# prompt_image_validator.py
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

class ExtractBgAttributes:
    def __init__(self,client:OpenAI):
        self.client = client


    def encode_image(self,image_path):
     with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_attributes(self,image_path):
        """Validate if the generated image matches the given prompt."""
        # Encode the image  
        base64_image = self.encode_image(image_path)


        systemPrompt =  """
        You are an advanced image analyst, capable of detecting **all artistic styles present ** in an image.
        You are an advanced image analyst, capable of detecting ** color harmony ** in an image.

        ** IMPORTANT REQUIREMENTS **  
        1) You will describe the **art styles** present in the image. An image can have **multiple styles** (e.g., Cartoonish, Cyberpunk, Realistic, Impressionistic, etc.).  
        - If multiple styles are detected, list them all.  
        2) You will analyze the color harmony of the image. Identify whether the colors follow a specific scheme such as:  
        - **Monochromatic** (shades of a single color)  
        - **Analogous** (colors next to each other on the color wheel)  
        - **Complementary** (high contrast, opposite colors on the wheel)  
        - **Triadic** (three evenly spaced colors)  
        - **Muted / Pastel / Vibrant** (describe color intensity)  

        ** RESPONSE EXAMPLE **  
        Your image style is: Cartoonish, Cyberpunk  
        Your color harmony is: Complementary, with strong contrasts between blue and orange.  

        Your image style is: Realistic, Impressionistic
        Your color harmony is: Monochromatic, dominated by shades of gray and black.  

        Your image style is: Cartoonish, Whimsical, Illustrative 
        Your color harmony is: Complementary, with strong contrasts between blue and orange.  

        Your image style is: Realistic, Impressionistic, Illustrative 
        Your color harmony is: Monochromatic, dominated by shades of gray and black.  
        """


        userPrompt  = """
        Can you describe the style and harmony of my image ? 
        
        """

        messages = [

            {
                "role":"system", "content": systemPrompt
            },
                
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": userPrompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

        # Send image to OpenAI Vision API for description
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Use a vision-capable model
            messages=messages,
            max_tokens=1000,
            temperature= 0
        )
        
        # Get the AI's description of the image
        image_description = response.choices[0].message.content

        # Display prompt and description for reference
        return image_description

        # Check key elements with keyword matching
        