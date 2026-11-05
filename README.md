# Glucose Spikes

This project is a web application that allows users to view and filter glucose spike posts from the [Glucose Goddess](https://www.instagram.com/glucosegoddess) Instagram account.
The application consists of a scraper and a frontend.

![image](https://github.com/user-attachments/assets/06726223-3408-4bb3-b211-6306f113888e)

## Try it

https://glucosespikes.duckdns.org/

## Run locally

Serve the frontend over HTTP so the browser can fetch `posts.json`:

```sh
python3 -m http.server 41739 --bind 127.0.0.1
```

Open http://127.0.0.1:41739/

## Scrape

Populate `posts.json` with information about the latest glucose spike posts.
`python scraper.py`
