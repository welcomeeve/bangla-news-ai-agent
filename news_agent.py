
import os
import json
import html
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

RSS_URL = (
    "https://news.google.com/rss/search"
    "?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn"
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def get_json(url, data=None, headers=None):
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {},
        method="POST" if data else "GET"
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def telegram_request(method, fields, photo_url=None):
    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/{method}"
    )

    if photo_url:
        fields["photo"] = photo_url

    data = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(str(result))

    return result


def make_news(title, description, link):
    prompt = f"""
তুমি একজন দায়িত্বশীল বাংলা নিউজ সম্পাদক।
তথ্য বানাবে না, অনিশ্চিত তথ্যকে নিশ্চিত বলে লিখবে না।
একটি আকর্ষণীয় কিন্তু সত্যনিষ্ঠ বাংলা শিরোনাম দাও।
এরপর ২-৪টি বাক্যে খবরটি সংক্ষেপে লেখো।
শেষে সূত্রের লিংক দাও।
নিচের RSS তথ্যের বাইরে অযাচাইকৃত দাবি যোগ করবে না।

মূল শিরোনাম: {title}
উৎসের বিবরণ: {description[:1500]}
মূল লিংক: {link}

শুধু পোস্টের লেখা দাও।
"""

    endpoint = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-2.5-flash:generateContent?key="
        + urllib.parse.quote(GEMINI_API_KEY, safe="")
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    result = get_json(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    return result["candidates"][0]["content"]["parts"][0]["text"]


def find_image(item):
    # RSS-এ সরাসরি ছবি থাকলে সেটি খোঁজার চেষ্টা।
    for element in item.iter():
        tag = element.tag.lower()

        if tag.endswith("thumbnail") or tag.endswith("content"):
            url = element.attrib.get("url", "")
            if url.startswith("https://") or url.startswith("http://"):
                image_type = element.attrib.get("type", "")
                if not image_type or image_type.startswith("image/"):
                    return url

    # ছবি না থাকলে কোনো অনুমানভিত্তিক URL তৈরি করা হবে না।
    return None


def send_telegram(text, photo_url=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Telegram secrets পাওয়া যায়নি")

    # Telegram caption-এর সীমা এড়াতে লেখা আলাদা মেসেজে পাঠানো।
    if photo_url:
        try:
            telegram_request(
                "sendPhoto",
                {
                    "chat_id": TELEGRAM_CHAT_ID,
                    "caption": "নিউজের ছবি"
                },
                photo_url=photo_url
            )
        except Exception as error:
            print(f"ছবি পাঠানো যায়নি: {error}")

    telegram_request(
        "sendMessage",
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text[:4000],
            "disable_web_page_preview": "false"
        }
    )


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
        description = html.unescape(
            item.findtext("description", default="").strip()
        )

        if not title or not link or link in seen:
            continue

        seen.add(link)
        print(f"নিউজ: {title}")

        if not GEMINI_API_KEY:
            print("GEMINI_API_KEY পাওয়া যায়নি")
            continue

        try:
            news_text = make_news(title, description, link)
            photo_url = find_image(item)

            send_telegram(news_text, photo_url)
            print("Telegram-এ নিউজ পাঠানো হয়েছে")

        except Exception as error:
            print(f"সমস্যা হয়েছে: {error}")


if __name__ == "__main__":
    collect_news()
