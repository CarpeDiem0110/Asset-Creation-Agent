from openai import OpenAI
import os
from dotenv import load_dotenv
from extractImageAttributes import ExtractBgAttributes
from extractObjectAttributes import ExtractObjectAttributes
from objectQuality_controlNewFinal import FinalChecker


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

print("Client Connection is done")

'''
Realistic, hand-painted, lightly worn, carved wooden bird figurine featuring smooth edges and subtle grain texture, colored in soft browns and muted greens to match the botanical setting, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting.
Realistic, hand-painted, rectangular miniature watercolor paint tin made of metal, with a slightly weathered finish, featuring soft earth-toned paint cakes inside 
and a small hinged lid, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting.
Realistic, hand-painted, antique brass key with a decorative bow and slight tarnish, reflecting gentle warm tones to blend with the wooden and golden accents in the room, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting.


'''



background_image_path = "../pixelArt.png"

object_image_paths = ["generated_images2/image_1Crop.png","generated_images2/image_2Crop.png","generated_images2/image_3Crop.png"]


# BUNLARIN RESIMLERI URETMEK ICIN OLUSTURULAN PROMPTLAR

object_prompt1 = "Realistic, hand-painted, lightly worn, carved wooden bird figurine featuring smooth edges and subtle grain texture, colored in soft browns and muted greens to match the botanical setting, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting."

object_prompt2 =  "Realistic, hand-painted, rectangular miniature watercolor paint tin made of metal, with a slightly weathered finish, featuring soft earth-toned paint cakes inside and a small hinged lid, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting."

object_prompt3 = "Realistic, hand-painted, antique brass key with a decorative bow and slight tarnish, reflecting gentle warm tones to blend with the wooden and golden accents in the room, isolated object on a plain white background, no shadows, no reflections, no additional elements, no lighting."


finalValidator = FinalChecker(client)

print("Quality is connected")

print("PROCESS IS STARTING ...")

finalValidator.process_objectRequirements(background_image_path,object_image_paths[2],object_prompt3)


