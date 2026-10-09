
import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html

RSS_URL = (
    "https://news.google.com/rss/search"
    "?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn"
)

API_KEY = os.environ.get("GEMINI_API_KEY", "")


def collect_news():
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "BanglaNewsAgent/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    items = root.findall("./channel/item")
    seen = set()

    for item in items[:10]:
        title = html.unescape(
            item.findtext("title", default="").strip()
        )
        link = item.findtext("link", default="").strip()
        description = item.findtext(
            "description", default=""
        ).strip()

        if not title or not link or link in seen:
            continue

        seen.add(link)
        print(f"\nমূল শিরোনাম: {title}")

        if not API_KEY:
            print("GEMINI_API_KEY পাওয়া যায়নি।")
            continue

        prompt = f"""
তুমি একজন দায়িত্বশীল বাংলা নিউজ সম্পাদক।

নিচের তথ্যের ভিত্তিতে একটি সংক্ষিপ্ত Facebook নিউজ পোস্ট লেখো।
কোনো অজানা তথ্য, উদ্ধৃতি বা ঘটনা বানিয়ে লিখবে না।
তথ্য অসম্পূর্ণ হলে সেটি স্পষ্ট করবে।
আকর্ষণীয় কিন্তু সত্যনিষ্ঠ শিরোনাম দেবে।
মূল খবর ২-৪টি বাক্যে লিখবে।
শেষে 'সূত্রের লিংক' হিসেবে দেওয়া লিংকটি রাখবে।

শিরোনাম: {title}
উৎসের বিবরণ: {description[:1500]}
মূল লিংক: {link}

শুধু বাংলায় পোস্টটি দাও।
"""

        try:
            endpoint = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/gemini-2.5-flash:generateContent?key="
                + urllib.parse.quote(API_KEY, safe="")
            )

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read())

            text = result["candidates"][0]["content"]["parts"][0]["text"]

            print("\nAI তৈরি করা নিউজ:")
            print(text)
            print("\n" + "-" * 50)

        except Exception as error:
            print(f"নিউজ তৈরিতে সমস্যা: {error}")


if __name__ == "__main__":
    collect_news()
