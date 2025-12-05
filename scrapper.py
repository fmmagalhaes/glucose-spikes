import hashlib
import instaloader
import json
import os
import sys
import time
from image_utils import download_image, extract_text_from_glucose_chart_image, trim_white_space_vertical

L = instaloader.Instaloader()
BASE_DIR = sys.path[0]
USERNAME = 'glucosegoddess'

# Instagram gives us 12 posts in a first call. That's a 3x4 grid. In case this changes to 3x3, we're only iterating through the first 9, to avoid extra calls.
MAX_POSTS = 9

images_dir = os.path.join(BASE_DIR, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)


def get_short_filename(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def load_existing_posts(filename='posts.json'):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as json_file:
            return json.load(json_file)
    return []


def save_posts_to_json(posts, filename='posts.json'):
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, 'w') as json_file:
        json.dump(posts, json_file, indent=2)


def process_post(post, existing_post_ids):
    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
    print(f"\nProcessing post: {post_url}")

    if post.mediaid in existing_post_ids:
        print(f"Post {post.mediaid} already processed. Skipping.")
        return

    image_url = post.url
    print(f"Image url: {image_url}")

    short_filename = get_short_filename(post_url)
    image_local_path = download_image(image_url, os.path.join(images_dir, short_filename))

    if image_local_path:
        extracted_text = extract_text_from_glucose_chart_image(image_local_path)
        if extracted_text:
            trim_white_space_vertical(image_local_path)

            post_data = {
                'id': post.mediaid,
                'postUrl': post_url,
                'imgOriginalSrc': image_url,
                'imgSrc': os.path.relpath(image_local_path, BASE_DIR),
                'imgText': extracted_text,
                'description': post.caption,
                'date': post.date_utc.strftime('%Y-%m-%d %H:%M:%S'),
            }
            return post_data

        else:
            os.remove(image_local_path)


def scrape_instagram_posts(username, existing_post_ids):
    profile = instaloader.Profile.from_username(L.context, username)
    posts = []

    try:
        i = 0
        for post in profile.get_posts():
            i = i+1
            time.sleep(5)

            if i >= MAX_POSTS:
                print("Finished getting latest posts")
                break

            post_data = process_post(post, existing_post_ids)
            if post_data:
                posts.append(post_data)
    except Exception as e:
        print("Failed getting posts", e)

    return posts


def main():
    existing_posts = load_existing_posts()
    existing_post_ids = {post['id'] for post in existing_posts}

    new_posts = scrape_instagram_posts(USERNAME, existing_post_ids)

    if new_posts:
        existing_posts = new_posts + existing_posts
        save_posts_to_json(existing_posts)
        print("New posts have been saved to posts.json")
    else:
        print("No new posts found")


if __name__ == "__main__":
    main()
