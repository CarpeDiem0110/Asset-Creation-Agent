from openai import OpenAI
import base64
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import os 

load_dotenv()


class CompatibilityFeedback(BaseModel):
    compatibility_explanation: str
    compatibility_score: str
    issues: list[str]
    suggestions: list[str]


class FinalChecker: 
    # Connect to the client 
    def __init__(self, client: OpenAI, max_attempts: int = 4):
        self.client = client
        self.max_attempts = max_attempts
        self.attempts = []

    def encode_image(self,image_path):
     with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

      
    # Skor düzenlemesini yeniden yapılandır. => Örneğin imageAttribute kısmında ve objectAttribute kısmında stillerin tamamen aynı olması lazım 
    # Eğer bu şekilde olursa +3 puan alsın. 

    def checkCompatibility (self,backgroundImageAttributes, objectImageAttributes) -> CompatibilityFeedback :

        
        system_content = """
        You are an expert in evaluating the compatibility of game objects with given background image attributes.
        Your task is to evaluate how well the object blends with the background image based on both style and color harmony.

        You must provide your evaluation in a structured format that can be parsed into:
        {
            "compatibility_explanation": string (lists all additions/deductions),
            "compatibility_score": int (0-5) (MUST match explanation's math),
            "issues": list of strings describing specific problems,
            "suggestions": list of strings with specific improvements    
        }

        1. Compatibility Score (BASELINE: 0/10 points):
        Start with 0 point baseline, then:
        
        ADDITIONS:
        - (+3) Style consistency (e.g., cartoon-style background with cartoon-style object)
        - (+2) Color harmony (if object's colors complement background's color scheme)
        
        DEDUCTIONS (mandatory when issues exist):
        - (-3) Inconsistent art style
        - (-2) No color harmony (if colors of object clash or don't complement with background image)

        2.Style Consistency Rules:
        - FULL MATCH REQUIRED: All style attributes must be identical for +3 (e.g., 'Cyberpunk, Realistic' vs 'Cyberpunk, Realistic')
        - ANY MISMATCH: If even one style attribute differs, deduct -3 (e.g., 'Illustrative, Cartoonish' vs 'Illustrative, Realistic')

        3. Color Harmony Rules:
        - Analogous colors (adjacent on color wheel, e.g., green-blue) = Good harmony (+2)
        - Complementary colors (opposite on color wheel, e.g., red-green) = Good harmony (+2)
        - Clashing colors (unrelated hues with no scheme) = Poor harmony (-2)
        - Monochromatic mismatch (different intensity of same hue) = Poor harmony (-2)

        4. Issues Examples:
        **Style Issues:**
        - Scenario 1: Background: Cyberpunk, Realistic / Object: Illustrative, Cartoonish
            "Your object style is not compatible with background image style."
        - Scenario 2: Background: Cyberpunk, Cartoonish / Object: Whimsical, Cartoonish
            "Your object style is partly compatible with background image style."
        Scenario 3: Background: Cyberpunk, Cartoonish / Object: Cyberpunk, Cartoonish
            "Your object style is totaly compatible with background image style."

        **Color Issues:**
        - Background: Analogous (green-blue) / Object: Red tones
            "Object colors clash with background's analogous green-blue scheme."
        - Background: Analogous (green-blue) / Object: Greenish-blue tones
            "Object colors complement background's analogous green-blue scheme."

        5. Suggestions Examples:
        **Style Suggestions:**
        - Background: Cyberpunk, Realistic / Object: Illustrative, Cartoonish
            "Add cyberpunk, realistic elements to your prompt and remove illustrative, cartoonish references."

        - Background: Cyberpunk, Realistic / Object: Realistic, Cyberpunk
            "Your object style and image style is matched."

        - Background: Cyberpunk, Realistic / Object: Cyberpunk, Cartoonish
            "Add Realistic style  into your prompt and remove Cartoonish reference."
        
        
        **Color Suggestions:**
        - Background: Analogous (green-blue) / Object: Red tones
            "Adjust object colors to include green and blue tones to match the background's analogous scheme."
        - Background: Analogous (green-blue) / Object: Yellow tones
            "Incorporate green-blue hues into the object to achieve better color harmony."

        TOTAL: Baseline (0) + Additions - Deductions = Score (0-5)

        CRITICAL RULES:
        1. Start with BASELINE score (0)
        2. Only add points when truly deserved
        3. Always deduct points when issues are present
        4. Show math: (baseline + additions - deductions = final score)
        5. Be realistic and specific in color harmony assessment

        Your response must be a valid JSON object with only the required fields.
    """
        
        

        user_prompt = f"""Evaluate the compatibility of object image attributes with the background image attributes:
        
        Object image attribute : {objectImageAttributes} 
        Background image attribute : {backgroundImageAttributes}
        
        Remember:
        1. Start with BASELINE score 
        2. Add points ONLY for genuinely good qualities
        3. Deduct points for ALL issues found
        4. Show your math clearly: baseline + additions - deductions = final score
        5. Be objective and realistic in your assessment
        
        Provide your evaluation in the required JSON format."""


        
        
        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
        
        

        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=messages,
                response_format=CompatibilityFeedback,
                max_tokens=1000
            )
            
            return response.choices[0].message.parsed
            
        except Exception as e:
            print(f"Error in evaluate_image: {str(e)}")
            # Return a default feedback object in case of error
            return CompatibilityFeedback(
                compatibility_score= 0,
                issues=["Error evaluating image"],
                suggestions=["Try regenerating the image"]
            )

    
    # Compatability feedbackine göre objectPromptu üzerinde oynama yapacak ve bize yeniden verecek. 
    def suggest_prompt_improvements(self, feedback: CompatibilityFeedback, original_prompt: str) -> str:
            """Generate improved prompt based on feedback."""
            system_prompt = """You are an expert at improving image generation prompts. 
            Based on the feedback from our quality control evaluation, suggest improvements 
            to the original prompt while maintaining its core elements.
            
            ** IMPORTANT WARNING ** 
            Don't change totaly structure of prompt. Follow the feedback.suggestions command.

            """

            user_prompt = f"""Original prompt: {original_prompt}

            Feedback received:
            - Compatibility Score: {feedback.compatibility_score}
                        
            Issues identified:
            {chr(10).join(feedback.issues)}
            
            Previous suggestions:
            {chr(10).join(feedback.suggestions)}
            
            Please provide an improved version of the prompt that addresses these issues."""

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=1000
                )
                
                improved_prompt = response.choices[0].message.content
                return improved_prompt.strip()
                
            except Exception as e:
                print(f"Error in suggest_prompt_improvements: {str(e)}")
                return original_prompt


    
    def generateNewImage(self,prompt):
        """Generate an image based on the given prompt and return the image URL."""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,  # Use the description field from the prompt
                size="1024x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url
            return image_url

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None

    

    def saveImageFolder(self,imageURL):
        # Step 4: Download and save the image locally
        image_response = requests.get(imageURL)

        # new path belirtilecek
        i = 0
        
        if image_response.status_code == 200:
            # Save the image with a unique name in the 'generated_images' folder
            directory = "deneme"
            if not os.path.exists(directory):
                os.makedirs(directory)
            image_path = os.path.join(directory, f"image_{i+1}.png")
            with open(image_path, 'wb') as file:
                file.write(image_response.content)
            print(f"Image {i+1} saved to {image_path}")
        else:
            print(f"Failed to download image {i+1}")

        return "deneme/image_1.png" # PATH OF NEW IMAGE IS GOING TO GENERATE
    
    

    def savePromptFolder(self,prompt:str,newImageURL):
        folder_path = os.path.dirname(newImageURL)

        # Define a fixed filename for the prompt (overwrite it each time)
        prompt_save_path = os.path.join(folder_path, "prompt.txt")

        # Save the new prompt in the folder (overwriting the previous one)
        with open(prompt_save_path, "w") as f:
            f.write(prompt)
        
        print(f"Prompt  saved at: {prompt_save_path}")
        
    
    def extract_background_attributes(self,image_path):
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




    
    def process_objectRequirements(self,backgroundpath,objectpath,objectPrompt):
        background_attribute = self.extract_background_attributes(backgroundpath)
        object_attribute = self.extract_object_attribute(objectPrompt,objectpath) 
        print("Evaluating compatibility of object ...")
        print("**********")
        response = self.checkCompatibility(background_attribute,object_attribute)
        print("EXPLANATION ", response.compatibility_explanation)
        print("SCORE: ", response.compatibility_score)
        print("SUGGESTION : ", response.suggestions )
        
        print(" --------- OBJECT ATTRIBUTES  ------- ")
        print(object_attribute)

        print(" --------- BACKGROUND ATTRIBUTES  ------- ")
        print(background_attribute)

        current_score = int(response.compatibility_score)

        while current_score != 5:
            newPromptForOurImage = self.suggest_prompt_improvements(response,objectPrompt)
            print("NEW PROMPT FOR OUR IMAGE ",newPromptForOurImage)
            newImageForObject = self.generateNewImage(newPromptForOurImage)  # THIS LINE RETURNS URL OF IMAGE 
            newImageURL = self.saveImageFolder(newImageForObject) # THIS LINE SAVES THE NEW IMAGE INTO THE FOLDER.
            print(newImageURL)
            self.savePromptFolder(newPromptForOurImage,newImageURL)


            new_object_attribute = self.extract_object_attribute(newPromptForOurImage,newImageURL)
            newEvaluation = self.checkCompatibility(background_attribute,new_object_attribute)  # BACKGROUND ATTRIBUTE DEGISMIYOR ZATEN
            print(" --------- NEW OBJECT ATTRIBUTES  ------- ")
            print(new_object_attribute) 
             

            
            print("******* EVALUATION FOR NEW PROMPT AND IMAGE *******")
            print("EXPLANATION ", newEvaluation.compatibility_explanation)
            print("SCORE: ", newEvaluation.compatibility_score)
            print("SUGGESTION : ", newEvaluation.suggestions )
            current_score = int(newEvaluation.compatibility_score)
            print("***************** LOOP FINISHED ***************** ")

        print("FINDING OPTIMAL OBJECT PROMPT AND IMAGE IS FINISHED")
    
    

