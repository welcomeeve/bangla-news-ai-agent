
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
        "v1beta/models/gemini-3.5-flash-lite:generateContent?key="
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

WISPBYTE_URL = os.environ.get("WISPBYTE_URL", "").rstrip("/")
NEWS_API_SECRET = os.environ.get("NEWS_API_SECRET", "")


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

    fields = dict(fields)
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
প্রথম লাইনে সংক্ষিপ্ত, আকর্ষণীয় ও সত্যনিষ্ঠ বাংলা শিরোনাম দাও।
এরপর ২-৪টি বাক্যে খবরটি সংক্ষেপে লেখো।
শেষে সূত্রের লিংক দাও।
RSS তথ্যের বাইরে অযাচাইকৃত দাবি যোগ করবে না।

মূল শিরোনাম: {title}
উৎসের বিবরণ: {description[:1500]}
মূল লিংক: {link}

শুধু পোস্টের লেখা দাও।
"""

    endpoint = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.5-flash-lite:generateContent?key="
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

    return result["candidates"][0]["content"]["parts"][0]["text"].strip()


def find_image(item):
    for element in item.iter():
        tag = element.tag.lower()

        if tag.endswith("thumbnail") or tag.endswith("content"):
            url = element.attrib.get("url", "")
            image_type = element.attrib.get("type", "")

            if (
                url.startswith("https://")
                and (not image_type or image_type.startswith("image/"))
            ):
                return url

    return None


def send_telegram(text, photo_url=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Telegram secrets পাওয়া যায়নি")

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
            print("Telegram-এ ছবি পাঠানো যায়নি:", repr(error))

    telegram_request(
        "sendMessage",
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text[:4000],
            "disable_web_page_preview": "false"
        }
    )


def send_to_a24(headline, image_url):
    if not WISPBYTE_URL or not NEWS_API_SECRET:
        print("A24 বাদ: WISPBYTE_URL বা NEWS_API_SECRET নেই")
        return

    if not image_url:
        print("A24 বাদ: নিউজের সরাসরি HTTPS ছবি পাওয়া যায়নি")
        return

    if not image_url.startswith("https://"):
        print("A24 বাদ: ছবির URL HTTPS নয়")
        return

    payload = json.dumps({
        "headline": headline[:500],
        "image_url": image_url
    }).encode("utf-8")

    request = urllib.request.Request(
        WISPBYTE_URL + "/news",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-News-Secret": NEWS_API_SECRET
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=90) as response:
        result = response.read().decode("utf-8")
        print("A24 response:", result)


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
        print("নিউজ:", title)

        if not GEMINI_API_KEY:
            print("GEMINI_API_KEY পাওয়া যায়নি")
            continue

        try:
            news_text = make_news(title, description, link)
            photo_url = find_image(item)

            # আগের Telegram নিউজ ব্যবস্থা বজায় থাকবে
            send_telegram(news_text, photo_url)
            print("Telegram-এ নিউজ পাঠানো হয়েছে")

            # প্রথম লাইনের শিরোনাম দিয়ে A24 কার্ড তৈরি
            headline = news_text.splitlines()[0].strip()
            headline = headline.lstrip("#* ").strip()

            try:
                send_to_a24(headline, photo_url)
            except Exception as error:
                print("A24-তে পাঠানো যায়নি:", repr(error))

        except Exception as error:
            print("নিউজ প্রসেসিংয়ে সমস্যা:", repr(error))


if __name__ == "__main__":
    collect_news()
