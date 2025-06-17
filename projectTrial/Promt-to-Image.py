from openai import OpenAI
from dotenv import load_dotenv
import os 



load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

print("Clint Connection is done")


userPrompt = """
A brightly colored, cartoon-style illustration of a vintage diner-style kitchen.  
The scene features a sunny, outdoor view through a large window showing palm trees and a street with a classic car.  
Shelves laden with colorful dishes, decorative items, and framed paintings line the walls.  
Plants and bouquets of flowers are placed strategically throughout.  The kitchen's seating includes booths with light beige quilted upholstery and a small table in the foreground.  
A red vintage-style microwave and radio are prominently displayed.  The lighting is warm, with sunlight streaming into the room, creating soft shadows and highlighting the details of the various objects.  
The perspective is from a slightly elevated vantage point looking into the interior, focusing on the comfortable and inviting atmosphere. The color palette is pastel with shades of pink, light blue, and peach.  
The overall style is reminiscent of retro American diner illustrations, with a playful and cheerful mood.  The composition is balanced, with a clear focal point being the window and view outside.  
The image is rendered with bold outlines and flat, solid colors, giving it a distinctive cartoonish aesthetic.
"""

userPrompt2 = """
A beautifully crafted wooden bird miniature, meticulously carved with warm brown tones and soft brush-strokes that 
enhance its delicate feather detail. The bird is positioned on a rustic wooden shelf, surrounded by earthy accents that harmonize with its color palette. The gentle light pouring in from a nearby window reflects softly off its polished surface, creating a serene atmosphere. Its charming handcrafted eyes invite admiration, embodying the artisanal spirit of the room. The backdrop features subtle textures that echo the warmth of the miniature, ensuring a cohesive and inviting scene.

"""








response = client.images.generate(
    model="dall-e-3",
    prompt=userPrompt2,  # Use the 'description' field of each prompt
    size="1024x1024",
    quality="standard",
    n=1,
 )

print(response.data[0].url)