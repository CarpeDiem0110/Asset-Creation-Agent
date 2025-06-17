import base64
from openai import OpenAI
import json
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from autocrop import remove_background
from objectQuality_controlNewFinal import FinalChecker



# From quality_control => Burada fromdan sonra gelen isim python dosyasının ismini göstermektedir. 
# import BackgroundQualityCheck = > Bu kısım ise class ismini belirtmektedir.

load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

print("Client Connection is done")


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "../images/ArtistsLoftBg.png"


# Getting the Base64 string
base64_image = encode_image(image_path)


## BURADAKI PROMPT NASIL GELISTIRILEBILIR UZERINE BI ARA DUSUN

system_content = """
    "You are a specialist in designing high-quality hidden object game items. "
    "Your task is to generate exactly 3 distinct hidden objects that blend seamlessly into the provided scene image. "
    "These objects must be small, tactile, and able to be placed within the environment as hidden objects for the game."
    
    
        ### **IMPORTANT STYLE REQUIREMENT**
    - **The objects MUST match the art style of the given image.**
    - **If the given image has a cartoon style, the objects MUST also be in cartoon style.**
    - **If the given image is realistic, the objects MUST also be realistic.**
    - **No object should have a different style than the image. This is a strict requirement.*

        ### **IMPORTANT COLOR PALETTE REQUIREMENT**
    - **The objects MUST match the color palette of the given image.
    - **The dominant and secondary colors of the image MUST be reflected in the objects.
    - **If the image has warm tones, the objects MUST also use warm tones.
    - **If the image has a muted or pastel palette, the objects MUST follow the same scheme.
    - **No object should introduce colors that clash with the scene. This is a strict requirement.
    
    
    "### Requirements:"
    "1. **Distinct Objects Only (No Environment Descriptions)**"
    "   - ONLY return small, distinct objects that can be picked up or interacted with."
    "   - SPECIFY IN THE OBJECT_PROMPTS : ALL OBJECTS BACKGROUND IS NOT GOING TO INCLUDE ANOTHER OBJECT OR ANOTHER ENVIRONMENT. "
    "2. **Detailed Object Descriptions**"
    "   - Object prompts includes the material, texture, color, style and any unique details for each object that fits the given input image."
    "3. **Placement Integration**"
    "   - Specify exactly where each object should be placed within the scene for seamless blending."
    "4. **Output Format**"
     "Your response should conform to the 'TestGameObjectList' Pydantic model, containing the following fields:"
    "- 'object_names': A list of three suggested object names that can blend naturally in the environment."
    "- 'object_prompts': A list of three descriptions for each object, describing their appearance and purpose."
    "- 'object_locations': A list of three locations specifying where each object should be placed within the scene."
    "   ```"

    "***Example Object PROMPTS:***"
    "Whimsical, hand-painted, cartoonish style, round edges A spiral-shaped sailor’s horn with a thick mouthpiece, designed in a cartoonish style on a white background, and gentle rounded edges., isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."
    "Whimsical, hand-painted, cartoonish style, round edges A solid wooden doorstop shaped like a seagull with subtle cartoonish features, posed on a plain white background,  and no reflections., isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."

"""


'''
"Whimsical, hand-painted, cartoonish style, round edges A carved wooden sea turtle with a patterned shell, shown in soft cartoon style on a white background, highlighting its rounded, solid form., isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."
'''

user_content = """
Generate exactly 3 distinct hidden objects that blend seamlessly into the provided scene image. 

Each object must be small, tactile, and designed to be naturally hidden within the environment. 

Ensure that the objects match the art style and color palette of the background image. 

"""


messages = [
    {"role": "system", "content": system_content},
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": user_content},
            # Use the image URL here if available
            {"type": "image_url", 
             "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}" # You may want to upload this image first for a URL if needed
             }
            }
        ]
    }
]


class GameObject(BaseModel):
    name: str
    location: str 
    prompt: str

class GameObjectList(BaseModel):
    objects: list[GameObject]

class testGameObjectList(BaseModel):
    object_names: list[str]
    object_prompts: list[str]
    object_locations: list[str]



completion = client.beta.chat.completions.parse(
            model="o1",
            messages=messages,
            response_format=testGameObjectList  
        )

        # Get the response in the new format
test_response = completion.choices[0].message.parsed

print("TEXT RESPONSE IS TAKEN")

print("************")




## GERI KALAN LIST SEKLINDE DONEN object_names ve object_locations kısmınıda bu şekilde çekebilirsin.
object_prompts = test_response.object_prompts  # Bu bir liste
object_locations = test_response.object_locations
object_names = test_response.object_names       # Bu bir liste


## LIST OBJECT NAME 
for objectName in object_names:
    print(objectName)

print("*************")

# LIST OBJECT PROMPTS
for objectPrompt in object_prompts:
    print(objectPrompt)


print("*************")

for locations in object_locations:
    print(locations)


    # Step 3: Generate images using DALL-E for each of the   prompts
for i,object in enumerate(object_prompts):
    response = client.images.generate(
        model="dall-e-3",
        prompt=object,  # Use the 'description' field of each prompt
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    # Get the URL of the generated image
    image_url = response.data[0].url
    
    
    
    # Step 4: Download and save the image locally
    image_response = requests.get(image_url)

    print(image_response)
    
    if image_response.status_code == 200:
        # Save the image with a unique name in the 'generated_images' folder
        directory = "generated_images1"
        if not os.path.exists(directory):
            os.makedirs(directory)
        image_path = os.path.join(directory, f"image_{i+1}.png")
        with open(image_path, 'wb') as file:
            file.write(image_response.content)
        print(f"Image {i+1} saved to {image_path}")
    else:
        print(f"Failed to download image {i+1}")





# Crop images.

inputPaths = ["generated_images1/image_1.png","generated_images1/image_2.png","generated_images1/image_3.png"]

outputPaths = ["generated_images1/image_1Crop.png","generated_images1/image_2Crop.png","generated_images1/image_3Crop.png"]


for i in range(3):
    remove_background(inputPaths[i],outputPaths[i])

    ## Resimleri cropla ve generated images içerisinde aynı yere gönder. 
print("IMAGE CROPPING IS COMPLETED")


print("********")

'''
object_prompts = test_response.object_prompts  # Bu bir liste
object_locations = test_response.object_locations
object_names = test_response.object_names
'''

qualityAgent = FinalChecker(client)

print("QUALITY AGENT IS CONNECTED ... ")

qualityAgent.process_objectRequirements(image_path,outputPaths[0],object_prompts[0])




