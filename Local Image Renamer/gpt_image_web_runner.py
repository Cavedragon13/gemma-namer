import openai
import os

# Setup
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
output_folder = "/Users/edq/Library/Mobile Documents/com~apple~CloudDocs/Downloads/Images/API_Output"
os.makedirs(output_folder, exist_ok=True)

# Load prompts
with open("planetfall_image_prompts.md", "r") as f:
    prompts = [line.strip() for line in f if line.strip()]

# Call DALL·E or GPT-Image-1 API (text-to-image)
for i, prompt in enumerate(prompts):
    response = openai.images.generate(
        model="dall-e-3",  # Change if using another model like GPT-Image-1
        prompt=prompt,
        n=1,
        size="1024x1024"  # or whatever size you're targeting
    )

    # Save result
    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    with open(f"{output_folder}/img_{i+1:03}.png", "wb") as f:
        f.write(image_data)