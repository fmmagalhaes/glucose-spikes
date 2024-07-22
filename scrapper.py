import time
import instaloader
import os
import hashlib
import requests
from PIL import Image
import pytesseract
import json
from datetime import datetime, timedelta

L = instaloader.Instaloader()

images_dir = 'images'
if not os.path.exists(images_dir):
    os.makedirs(images_dir)


def get_short_filename(url):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    file_extension = os.path.splitext(url.split('?')[0])[1]
    return url_hash + file_extension


def download_image(url, filepath):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filepath
    else:
        print(f"Failed to download image from {url}")
        return None


def trim_white_space_vertical(image_path, tolerance=10, margin=20):
    img = Image.open(image_path)

    # Convert image to grayscale
    img_gray = img.convert("L")

    width, height = img_gray.size
    pixels = img_gray.load()

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
        img_cropped = img.crop((0, top, width, bottom))
        img_cropped.save(image_path)
        print(f"Image cropped: top={top}, bottom={bottom}, with margin={margin}")
    else:
        print("No cropping needed or invalid bounds.")


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def load_existing_posts(filename='posts.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    return []


def save_posts_to_json(posts, filename='posts.json'):
    with open(filename, 'w') as json_file:
        json.dump(posts, json_file, indent=2)


def scrape_instagram_posts(username, existing_post_ids):
    profile = instaloader.Profile.from_username(L.context, username)
    posts = []

    try:
        i = 0
        for post in profile.get_posts():
            i = i+1
            time.sleep(5)

            if i >= 9:
                print("Finished getting latest posts")
                break

            post_url = f"https://www.instagram.com/p/{post.shortcode}/"
            image_url = post.url

            print(f"Processing post: {post_url}")

            if post.mediaid in existing_post_ids:
                print(f"Post {post.mediaid} already processed. Skipping.")
                continue

            short_filename = get_short_filename(image_url)
            image_filename = os.path.join(images_dir, short_filename)

            downloaded_path = download_image(image_url, image_filename)

            if downloaded_path:
                # Perform OCR on the image
                extracted_text = extract_text_from_image(downloaded_path)

                # Check if the extracted text contains any of the keywords
                extracted_text_lower = extracted_text.lower()
                if 'glucose' in extracted_text_lower and \
                    'spike' in extracted_text_lower and \
                        'baseline' in extracted_text_lower:

                    print("Found spike chart!")

                    trim_white_space_vertical(downloaded_path)

                    post_data = {
                        'id': post.mediaid,
                        'postUrl': post_url,
                        'imgOriginalSrc': image_url,
                        'imgSrc': downloaded_path,
                        'imgText': extracted_text,
                        'description': post.caption,
                        'date': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    posts.append(post_data)

                else:
                    os.remove(downloaded_path)
    except Exception as e:
        print("Failed getting posts", e)

    return posts


def main():
    username = 'glucosegoddess'
    existing_posts = load_existing_posts()
    existing_post_ids = {post['id'] for post in existing_posts}

    new_posts = scrape_instagram_posts(username, existing_post_ids)

    if new_posts:
        existing_posts.extend(new_posts)
        save_posts_to_json(existing_posts)
        print("New posts have been saved to posts.json")
    else:
        print("No new posts found")


if __name__ == "__main__":
    main()
