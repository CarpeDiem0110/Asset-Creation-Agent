# autocrop.py

from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str):
    """
    Removes the background from an image and saves it.

    :param input_path: Path to the input image
    :param output_path: Path to save the processed image
    """
    # Open the image
    input_image = Image.open(input_path)
    
    # Remove background
    output_image = remove(input_image)
    
    # Save the processed image
    output_image.save(output_path)

    print(f"Processed image saved at: {output_path}")
