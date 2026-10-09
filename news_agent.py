
import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = (
    "https://news.google.com/rss/search"
    "?q=Bangladesh&hl=bn&gl=BD&ceid=BD:bn"
)

def collect_news():
    request = urllib.request.Request(
        RSS_URL,
        headers={"User-Agent": "BanglaNewsAgent/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = root.findall("./channel/item")

    for item in items[:10]:
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()

        if title and link:
            print(f"NEWS: {title}")
            print(f"LINK: {link}")
            print("-" * 50)

if __name__ == "__main__":
    collect_news()
  
