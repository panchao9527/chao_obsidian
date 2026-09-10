"""仅采集练习站前两页，验证状态、字段、完成标记后导出。"""
from scrapling.spiders import Spider, Response


class QuotesSpider(Spider):
    name = "quotes_two_pages"
    start_urls = ["https://quotes.toscrape.com/"]
    allowed_domains = {"quotes.toscrape.com"}
    concurrent_requests = 2
    concurrent_requests_per_domain = 1
    download_delay = 1.0
    robots_txt_obey = True

    async def parse(self, response: Response):
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status}: {response.url}")
        cards = response.css(".quote")
        if not cards:
            raise ValueError(f"空页面: {response.url}")
        for card in cards:
            text = card.css(".text::text").get("").strip()
            author = card.css(".author::text").get("").strip()
            if not text or not author:
                raise ValueError(f"字段缺失: {response.url}")
            yield {"text": text, "author": author, "source_url": response.url}
        next_url = response.css("li.next a::attr(href)").get()
        if next_url == "/page/2/":
            yield response.follow(next_url, callback=self.parse)


def main():
    result = QuotesSpider().start()
    records = list(result.items)
    # 这是练习站的预期值，不是所有业务站点通用的成功标准。
    if not result.completed or len(records) != 20:
        raise RuntimeError(f"采集不完整: completed={result.completed}, count={len(records)}")
    if len({(r["text"], r["author"]) for r in records}) != len(records):
        raise ValueError("发现重复记录")
    result.items.to_json("output/quotes-two-pages.json", indent=True)
    result.items.to_csv("output/quotes-two-pages.csv")
    print(f"completed={result.completed}, records={len(records)}, pages="
          f"{len({r['source_url'] for r in records})}")


if __name__ == "__main__":
    main()
