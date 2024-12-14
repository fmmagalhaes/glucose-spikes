from image_utils import download_image, extract_text_from_glucose_chart_image


def test_image(url):
    image_local_path = download_image(url, "test.jpg")
    print(extract_text_from_glucose_chart_image(image_local_path))


def main():
    while True:
        url = input("Paste the image URL: ")
        test_image(url)


if __name__ == "__main__":
    main()
