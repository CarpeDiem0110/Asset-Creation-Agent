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


class Checker: 
    # Connect to the client 
    def __init__(self, client: OpenAI, max_attempts: int = 4):
        self.client = client
        self.max_attempts = max_attempts
        self.attempts = []

    def encode_image(self,image_path):
     with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

    # object Image'ın validasyonu sağlanmış olsun . 
    # background Image'ın ise elimizde olan resmi için 
    # Compatibility skorun nasıl düzenlenmesi gerektiği ile ilgili düzeltmeler yap .  
    # Skor düzenlemesini yeniden yapılandır.

    def checkCompatibility (self,backgroundImageAttributes, objectImageAttributes) -> CompatibilityFeedback :

        system_content = """
        You are an expert in evaluating the compatibility of game objects with given background image attributes.
        Your task is to evaluate how well the following object blends with the given background image.



        
        You must provide your evaluation in a structured format that can be parsed into the following fields:
        {
            "compatibility_explanation": string (MUST be provided first, lists all additions/deductions),
            "compatibility_score": int (0-5) (MUST match explanation's math),
            "issues": list of strings describing specific problems found,
            "suggestions": list of strings with specific improvements for the prompt    
        }

                 
        1. Compatibility Score (BASELINE: 0/10 points):
           Start with 0 point as your true baseline, then:
           
           ADDITIONS (when justified):
           - (+3) Style consistency (if the background is cartoon-style, the object should also be cartoon-style)
           - (+2) Color harmony between object and background
           
           
           DEDUCTIONS (mandatory when issues exist):
           - (-3) Inconsistent art style between object and background
           - (-2) No color harmony between object and background
         
        
        2. Issues : 
            Compare object image style with background image attribute. I am going to give you some scenario in order to behave like this scenario. 
            

            ** SCENARIO 1 **
            **Issue EXAMPLES**
            Your image style is : Cartoonish, Illustrative (This is the input came from backgroundImageAttributes)
            Object image style is: Cyberpunk, Realistic  (This is the input came from objectImageAttributes)


            ** Response ** 
            ' Your object style is not compatible with background image style.'


            ** SCENARIO 2 **
            **Issue EXAMPLES**
            Your image style is : Cyberpunk, Cartoonish (This is the input came from backgroundImageAttributes)
            Object image style is:  Whimsical, Cartoonish (This is the input came from objectImageAttributes)

            ** Response ** 
            ' Your object style is partly compatible with background image style.'


            
            ** SCENARIO 3 **
            **Issue EXAMPLES**
            Your image style is : Cyberpunk, Cartoonish (This is the input came from backgroundImageAttributes)
            Object image style is:  as Cyberpunk, Cartoonish (This is the input came from objectImageAttributes)


            ** Response ** 
            ' Your object style is fully compatible with background image style.'


            3. Suggestions : 
            Compare object image style with background image attribute. If there are discrepancies, suggest adjustments based on specific styles.

            ** SCENARIO 1 **
            **Suggestion EXAMPLES**
            Your image style is : Cartoonish, Illustrative (This is the input came from backgroundImageAttributes)
            Object image style is: Realistic (This is the input came from objectImageAttributes)

            ** Response ** 
            ' Add cartoonish, Illustrative expressions into your prompt and remove references to Realistic style.'

            ** SCENARIO 2 **
            **Suggestion EXAMPLES**
            Your image style is : Cyberpunk, Cartoonish (This is the input came from backgroundImageAttributes)
            Object image style is: Whimsical, Cartoonish  (This is the input came from objectImageAttributes)

            ** Response ** 
            ' Add cyberpunk style to your prompt and remove references to Whimsical style.'


            ** SCENARIO 3 **
            **Suggestion EXAMPLES**
            Your image style is : Cyberpunk, Cartoonish (This is the input came from backgroundImageAttributes)
            Object image style is: Cyberpunk, Cartoonish  (This is the input came from objectImageAttributes)

            ** Response ** 
            ' Your object style and image style is matched.'


           TOTAL: Baseline (0) + Additions - Deductions = Art Style Score (0-5)

           CRITICAL RULES:
        1. You MUST start with the BASELINE score (0)
        2. Only add points when truly deserved, the barrier to getting additional points is high.
        3. Always deduct points when issues are present - NO EXCEPTIONS
        4. Show your math: (baseline + additions - deductions = final score)
        5. BE REALISTIC 
       
        Your response must be a valid JSON object containing only the required fields.
        Each explanation must show clear math with baseline, additions, and deductions.
        Issues and suggestions must be clear, specific, and actionable
        
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
            to the original prompt while maintaining its core elements."""

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

    

    def changeFormatImage(self,imageURL):
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
        
        



    # Eğer skor 7 den büyükse verilen object resmini kaydet eğer 7 den küçükse prompt önerisi al yeniden kontrol et 7 den büyük olana kadar bu süreç devam etsin 
    def process_objectRequirements(self,backgroundURL,objectURL,objectPrompt):
        print("Evaluating compatibility of object ...")
        print("**********")
        response = self.checkCompatibility(backgroundURL,objectURL)
        print("EXPLANATION ", response.compatibility_explanation)
        print("SCORE: ", response.compatibility_score)
        print("SUGGESTION : ", response.suggestions )
        
        
        currentScoreObject = int(response.compatibility_score)

        while currentScoreObject != 5:
            newPromptForOurImage = self.suggest_prompt_improvements(response,objectPrompt)
            print("NEW PROMPT FOR OUR IMAGE ",newPromptForOurImage)
            newImageForObject = self.generateNewImage(newPromptForOurImage)
            print("NEW IMAGE URL:  ", newImageForObject)
            newImageURL = self.changeFormatImage(newImageForObject)
            print(newImageURL)
            newEvaluation = self.checkCompatibility(backgroundURL,newImageURL)
            print("******* EVALUATION FOR NEW PROMPT AND IMAGE *******")
            print("EXPLANATION ", response.compatibility_explanation)
            print("SCORE: ", response.compatibility_score)
            print("SUGGESTION : ", response.suggestions )
            currentScoreObject = int(newEvaluation.compatibility_score)
            print("***************** LOOP FINISHED ***************** ")

    
    

