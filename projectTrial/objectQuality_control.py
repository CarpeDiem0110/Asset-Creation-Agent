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


class ObjectCompatibility: 
    # Connect to the client 
    def __init__(self, client: OpenAI, max_attempts: int = 4):
        self.client = client
        self.max_attempts = max_attempts
        self.attempts = []

    def encode_image(self,image_path):
     with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

    
    # Compatibility skorun nasıl düzenlenmesi gerektiği ile ilgili düzeltmeler yap .  

    def checkCompatibility (self,backgroundImageURL, objectImageURL) -> CompatibilityFeedback :

        system_content = """
        You are an expert in evaluating the compatibility of game objects with background images.
        Your task is to evaluate how well the following object blends with the given background image.

        EVALUATION PROCESS:
        1. Start with the BASELINE score for each category (this is a middle score, not a maximum)
        2. For each category, identify BOTH positive aspects (to add points) AND negative aspects (to deduct points)
        3. In your explanations, clearly list both additions and deductions with specific values
        4. Calculate final scores by applying all modifications to the baseline
        5. Final scores must mathematically match: baseline + additions - deductions
        
        
        You must provide your evaluation in a structured format that can be parsed into the following fields:
        {
            "compatibility_explanation": string (MUST be provided first, lists all additions/deductions),
            "compatibility_score": int (0-5) (MUST match explanation's math),
            "issues": list of strings describing specific problems found,
            "suggestions": list of strings with specific improvements for the prompt    
        }

        

        
        1. Compatibility Score (BASELINE: 0/5 points):
           Start with 0 point as your true baseline, then:
           
           ADDITIONS (when justified):
           - (+3) Style consistency (if the background is cartoon-style, the object should also be cartoon-style)
           - (+2) Color harmony between object and background
           
           
           DEDUCTIONS (mandatory when issues exist):
           - (-3) Inconsistent art style between object and background
           - (-2) No color harmony between object and background
         
           
           
           
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

        user_prompt = """Evaluate the compatibility of this object with the given background:
        
        Remember:
        1. Start with BASELINE score 
        2. Add points ONLY for genuinely good qualities
        3. Deduct points for ALL issues found
        4. Show your math clearly: baseline + additions - deductions = final score
        5. Be objective and realistic in your assessment
        
        Provide your evaluation in the required JSON format."""


        #ENCODE IMAGES IN ORDER TO PASS TO THE MESSAGE
        base64_backgroundImage = self.encode_image(backgroundImageURL)

        base64_objectImage = self.encode_image(objectImageURL)
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
                    },
                    {
                        "type": "image_url",
                        "image_url": {  
                            "url": f"data:image/jpeg;base64,{base64_backgroundImage}"
                        }
                    },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_objectImage}"
                        }
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
            print("EXPLANATION ", newEvaluation.compatibility_explanation)
            print("SCORE: ", newEvaluation.compatibility_score)
            print("SUGGESTION : ", newEvaluation.suggestions )
            currentScoreObject = int(newEvaluation.compatibility_score)
            print("***************** LOOP FINISHED ***************** ")
    
        print("PROCESS IS COMPLETED")

    
    

