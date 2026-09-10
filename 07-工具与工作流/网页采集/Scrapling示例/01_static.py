"""单页采集；运行目录为本示例目录。"""
import json
from pathlib import Path
from scrapling.fetchers import Fetcher


def main():
    page = Fetcher.get("https://quotes.toscrape.com/", timeout=30, retries=1)
    if page.status != 200:
        raise RuntimeError(f"HTTP {page.status}")
    records = []
    for card in page.css(".quote"):
        text = card.css(".text::text").get("").strip()
        author = card.css(".author::text").get("").strip()
        if not text or not author:
            raise ValueError("名言正文或作者为空，请检查页面和选择器")
        records.append({"text": text, "author": author,
                        "tags": card.css(".tag::text").getall(), "source_url": page.url})
    if not records:
        raise ValueError("没有采集到记录：不能把空结果当作成功")
    Path("output").mkdir(exist_ok=True)
    Path("output/quotes-page1.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"HTTP={page.status}, records={len(records)}, output/quotes-page1.json")


if __name__ == "__main__":
    main()
