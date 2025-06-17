import base64
from openai import OpenAI
import json
import os
import requests
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Path to your image
image_path = "RetroDinerBg.png"

# Getting the Base64 string
base64_image = encode_image(image_path)

content = (
    "You are a professional level designer for hidden object puzzle games. "
    "Your task is to analyze the given scene and determine which objects can be placed in it. "
     "-'scene_analysis': Describe what is in the given image in detail.\n"
    "-'object_suggestions': Suggest three objects that can be added to the scene, ensuring they blend naturally with the environment.\n"
    "-'placement_locations':Specify where each of the suggested objects should be placed within the scene for optimal design and gameplay."
)
             




prompt_Agent = client.chat.completions.create(
    model="o1",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content             
             },          
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ],
    response_format= "json",

)





responste_text = json.dumps(prompt_Agent, indent=4)  # Pretty-print JSON

# Save to a text file
with open("vision_output.txt", "w", encoding="utf-8") as file:
    file.write(response_text)

print("Response saved to vision_output.txt")


jsonDeneme = json.loads(image_analysis)["object_suggestions"]

sceneAnalysis = json.loads(image_analysis)["scene_analysis"]

placementLocations = json.loads(image_analysis)["placement_locations"]

print("OBJECT SUGGESTION IS LOAD AS JSON FILE")



# Step 2: Create a directory to save the images
directory = "generated_images"
if not os.path.exists(directory):
    os.makedirs(directory)
    
json_file_path = os.path.join(directory, "object_suggestions.json")
with open(json_file_path, 'w') as json_file:
    json.dump(jsonDeneme, json_file, indent=4)

print(f"Object suggestions saved as {json_file_path}")

sceneAnalysis_file_path = os.path.join(directory, "scene_analysis.json")

# Stringi JSON formatına uygun hale getiriyoruz
scene_analysis_dict = {"scene_analysis": sceneAnalysis}

with open(sceneAnalysis_file_path, 'w') as json_file:
    json.dump(scene_analysis_dict, json_file, indent=4)

print(f"Scene analysis saved as {sceneAnalysis_file_path}")


# Create json file and write the content
placementLocations_file_path = os.path.join(directory, "placement_locations.json")
with open(placementLocations_file_path, 'w') as json_file:
    json.dump(placementLocations, json_file, indent=4)

print(f"Object suggestions saved as {placementLocations_file_path}")





# Step 3: Generate images using DALL-E for each of the   prompts
for i, objects in enumerate(jsonDeneme):
    imageAgent = client.images.generate(
        model="dall-e-3",
        prompt=objects,  # Use the 'description' field of each prompt
        size="1024x1024",
        quality="standard",
        n=1,
    )
    
    # Get the URL of the generated image
    image_url = imageAgent.data[0].url
    
    # Step 4: Download and save the image locally
    image_response = requests.get(image_url)

    print(image_response)
    
    if image_response.status_code == 200:
        # Save the image with a unique name in the 'generated_images' folder
        image_path = os.path.join(directory, f"image_{i+1}.png")
        with open(image_path, 'wb') as file:
            file.write(image_response.content)
        print(f"Image {i+1} saved to {image_path}")
    else:
        print(f"Failed to download image {i+1}")

