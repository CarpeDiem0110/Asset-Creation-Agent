from openai import OpenAI
import os
from dotenv import load_dotenv
from objectQuality_control import ObjectCompatibility


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

print("Client Connection is done")


background_image_path = "../cyberpunkImage.png"

object_image_paths = ["generated_images/image_1Crop.png","generated_images/image_2Crop.png","generated_images/image_3Crop.png"]


# BUNLARIN RESIMLERI URETMEK ICIN OLUSTURULAN PROMPTLAR

object_prompt1 = "Whimsical, hand-painted, cartoonish style, gently curved edges A small carved wooden bookmark shaped like a leaf, with subtle green and warm brown tones in a soft gradient, isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."

object_prompt2 =  "Whimsical, hand-painted, cartoonish style, rounded edges A tiny snail figurine formed from earthy-toned clay, featuring a warm golden-brown shell with delicate leaf-inspired accents, isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."

object_prompt3 = "Whimsical, hand-painted, cartoonish style, softly contoured edges A miniature artist’s palette with pastel paint spots in greens, blues, and soft yellows, adorned with a small wooden handle, isolated object on pure white background, no shadows, no reflections, no additional elements, no lighting."


qualityControl = ObjectCompatibility(client)

print("Quality is connected")

print("PROCESS IS STARTING ...")

qualityControl.process_objectRequirements(background_image_path,object_image_paths[0],object_prompt1)


