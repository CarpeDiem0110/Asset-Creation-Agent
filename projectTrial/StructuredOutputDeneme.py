import base64
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import json



load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
image_path = "groceries.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

# Instead of sending base64 directly, let's encode it into a URL if needed.

# systemContent
systemContent = """
Analyze this image and provide a response with the following details:

Objects: List the main objects detected in the image along with their approximate positions.
Scene Description: Give a short description of what is happening in the image.
Colors: Identify the dominant colors in the image.
Other Notable Elements: Mention any unusual or interesting aspects of the image.
"""

messages = [
    {"role": "system", "content": systemContent},
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "Analyze this image and describe its contents in detail."},
            # Use the image URL here if available
            {"type": "image_url", 
             "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}" # You may want to upload this image first for a URL if needed
             }
            }
        ]
    }
]


class CalendarEvent(BaseModel):
    objects: list[str]
    scene_decsription: str
    colors: list[str]

completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=messages,
    response_format= CalendarEvent
  #  response_format= CalendarEvent
)

response = completion.choices[0].message.content

print(response)






