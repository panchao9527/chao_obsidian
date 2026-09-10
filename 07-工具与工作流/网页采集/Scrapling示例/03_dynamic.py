"""浏览器渲染练习站；需要先安装 Chromium。"""
import argparse
from scrapling.fetchers import DynamicFetcher


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chrome', action='store_true', help='使用本机安装的 Chrome')
    args = parser.parse_args()
    page = DynamicFetcher.fetch(
        "https://quotes.toscrape.com/js/", headless=True,
        wait_selector=".quote .text", timeout=30000,
        disable_resources=False, google_search=False,
        real_chrome=args.chrome,
    )
    quotes = page.css(".quote .text::text").getall()
    if page.status != 200 or not quotes:
        raise RuntimeError(f"动态内容未就绪: status={page.status}, count={len(quotes)}")
    print(f"HTTP={page.status}, rendered_quotes={len(quotes)}")


if __name__ == "__main__":
    main()
