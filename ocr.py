import easyocr
from PIL import Image

def read_image(image_path: str) -> str:
    """Extract text from image using easyocr."""
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    # Extract text from result tuples
    raw_text = '\n'.join([text[1] for text in result])
    return raw_text
