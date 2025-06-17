from openai import OpenAI
import os
from dotenv import load_dotenv
import base64


load_dotenv()

key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=key)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "../ArtistsLoftBg.png"


systemPrompt = """
You are an expert in generating highly detailed prompts for DALL·E to create visually rich images.

Given an input image, your task is to generate a precise, structured, and descriptive prompt that can be used to recreate the image with DALL·E.

The prompt should:
1. Clearly describe the setting, perspective, and style.
2. Mention key objects, colors, lighting, and mood.
3. Be structured and natural-sounding, as if written for DALL·E.    

Analyze the provided image and generate a DALL·E-compatible prompt that accurately represents it.
"""

detailedSystemPrompt = """

You are an expert in analyzing images  and generating highly detailed prompts for DALL·E to create visually rich images.

Your task is to analyze a given image and generate a structured and descriptive prompt that accurately represents it. The generated prompt should be:
1. **Detailed**: Clearly describe the setting, perspective, and style.
2. **Structured**: Mention key objects, colors, lighting, and mood.
3. **Coherent**: Written naturally, as if intended for DALL·E.

### Example:

**Generated Prompt For Dalle:**  
A brightly colored, cartoon-style illustration of a vintage diner-style kitchen.  
The scene features a sunny, outdoor view through a large window showing palm trees and a street with a classic car.  
Shelves laden with colorful dishes, decorative items, and framed paintings line the walls.  
Plants and bouquets of flowers are placed strategically throughout.  
The kitchen's seating includes booths with light beige quilted upholstery and a small table in the foreground.  
A red vintage-style microwave and radio are prominently displayed.  
The lighting is warm, with sunlight streaming into the room, creating soft shadows and highlighting the details of the various objects.  
The perspective is from a slightly elevated vantage point looking into the interior, focusing on the comfortable and inviting atmosphere.  
The color palette is pastel with shades of pink, light blue, and peach.  
The overall style is reminiscent of retro American diner illustrations, with a playful and cheerful mood.  
The composition is balanced, with a clear focal point being the window and view outside.  
The image is rendered with bold outlines and flat, solid colors, giving it a distinctive cartoonish aesthetic.


---

Now, analyze the provided image and generate a **DALL·E-compatible prompt** in the same format.
"""

userPrompt = """
"If you are going to produce this image by using Dalle model, What should be the prompt of this image?"
"""

# Getting the Base64 string
base64_image = encode_image(image_path)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role" : "system", "content":detailedSystemPrompt },
        
        {
            "role": "user",
            "content": [
                { "type": "text", "text": userPrompt  },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ],
)

print(completion.choices[0].message.content)