# prompt_image_validator.py
from openai import OpenAI
import os
from dotenv import load_dotenv
import base64

class ExtractObjectAttributes:
    def __init__(self, client: OpenAI):
        self.client = client

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def extract_object_attribute(self, objectPrompt, image_path):
        """Extract artistic styles and color details from the given object image."""
        # Encode the image  
        base64_image = self.encode_image(image_path)

        systemPrompt = """
        You are an advanced image analyst, capable of detecting **all artistic styles** and **dominant colors** present in an object image.

        **IMPORTANT REQUIREMENTS**
        1) You will describe the **art styles** present in the image. An image can have **multiple styles** (e.g., Cartoonish, Cyberpunk, Realistic, Impressionistic, etc.).
           - If multiple styles are detected, list them all.
        2) You will describe the **dominant colors** present in the image (e.g., blue, red, teal, yellow, etc.).
           - List the primary colors or color palette observed.

        **RESPONSE FORMAT**
        Your image style is: [list of styles]
        Dominant colors: [list of colors]

        **RESPONSE EXAMPLES**
        Your image style is: Cartoonish, Cyberpunk
        Dominant colors: teal, purple, black

        Your image style is: Realistic, Impressionistic
        Dominant colors: blue, green, brown

        Your image style is: Whimsical, Illustrative
        Dominant colors: pastel pink, yellow, light blue
        """

        userPrompt = """
        Can you describe the style and dominant colors of my object image?
        """

        messages = [
            {
                "role": "system",
                "content": systemPrompt
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
            temperature=0
        )
        
        # Get the AI's description of the image
        image_description = response.choices[0].message.content

        return image_description
