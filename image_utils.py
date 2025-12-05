import mimetypes
import pytesseract
import requests
from PIL import Image, ImageEnhance

SPIKE_CHART_KEYWORDS = {'glucose', 'spike', 'baseline'}

# Constants for enhancement factors
CONTRAST_ENHANCEMENT_FACTOR = 2.0
SHARPNESS_ENHANCEMENT_FACTOR = 2.0


def extract_text_from_glucose_chart_image(image_path):
    try:
        image = Image.open(image_path)
        image = image.convert("L") # Converting to grayscale to improve OCR
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    # Try OCR with different enhancement techniques
    for enhance_func in [None, enhance_contrast, enhance_sharpness]:
        image = enhance_func(image) if enhance_func else image
        text = pytesseract.image_to_string(image, lang='eng')
        print(f"Testing enhance function {enhance_func}...")
        if contains_spike_chart_keywords(text):
            print(f"Found glucose chart through enhance function {enhance_func}!")
            return text

    print("This image is not a glucose chart!")
    print(text)
    return None


def enhance_contrast(image):
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(CONTRAST_ENHANCEMENT_FACTOR)


def enhance_sharpness(image):
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(SHARPNESS_ENHANCEMENT_FACTOR)


def contains_spike_chart_keywords(text):
    return all(keyword in text.lower() for keyword in SPIKE_CHART_KEYWORDS)


def trim_white_space_vertical(image_path, tolerance=10, margin=20):
    image = Image.open(image_path)

    # Convert image to grayscale
    image_gray = image.convert("L")

    width, height = image_gray.size
    pixels = image_gray.load()

    # Find the first non-white row from the top
    top = 0
    for y in range(height):
        is_white_row = all(pixels[x, y] > 255 - tolerance for x in range(width))
        if not is_white_row:
            top = y
            break

    # Find the first non-white row from the bottom
    bottom = height
    for y in range(height - 1, top - 1, -1):
        is_white_row = all(pixels[x, y] > 255 - tolerance for x in range(width))
        if not is_white_row:
            bottom = y + 1
            break

    top = max(top - margin, 0)
    bottom = min(bottom + margin, height)

    if top < bottom:
        image_cropped = image.crop((0, top, width, bottom))
        image_cropped.save(image_path)
        print(f"Image cropped: top={top}, bottom={bottom}, with margin={margin}")
    else:
        print("No cropping needed or invalid bounds.")


def download_image(url, filepath):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        extension = mimetypes.guess_extension(content_type) if content_type else None

        if extension:
            filepath_with_extension = f"{filepath}{extension}"
        else:
            filepath_with_extension = filepath

        with open(filepath_with_extension, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filepath_with_extension
    else:
        print(f"Failed to download image from {url}")
        return None
