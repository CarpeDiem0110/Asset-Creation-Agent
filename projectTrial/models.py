from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

print("Client Connection is done")


client = OpenAI()

models = client.models.list()

# Print the models in a readable format
for model in models.data:
    print(f"Model ID: {model.id}, Created: {model.created}, Owned By: {model.owned_by}")