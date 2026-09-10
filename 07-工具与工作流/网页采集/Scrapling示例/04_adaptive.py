"""纯本地 HTML：模拟 ID 改名，校验自适应定位后的业务标识。"""
from pathlib import Path
from scrapling.parser import Selector


def main():
    old_html = '<main><article id="old-card" data-sku="DEMO-001"><h2>测试商品</h2><p>19.90</p></article></main>'
    new_html = '<main><article id="new-card" data-sku="DEMO-001"><h2>测试商品</h2><p>19.90</p></article></main>'
    Path("output").mkdir(exist_ok=True)
    storage_file = str(Path("output/adaptive.db").resolve())
    url = "https://example.com/products"
    settings = {"adaptive": True, "url": url,
                "storage_args": {"storage_file": storage_file}}
    before = Selector(old_html, **settings)
    saved = before.css("#old-card", auto_save=True)
    assert len(saved) == 1
    after = Selector(new_html, **settings)
    assert not after.css("#old-card")
    recovered = after.css("#old-card", adaptive=True)
    assert len(recovered) == 1
    assert recovered[0].attrib["data-sku"] == "DEMO-001"
    assert recovered.css("h2::text").get() == "测试商品"
    print("strict_matches=0, adaptive_matches=1, sku=DEMO-001")


if __name__ == "__main__":
    main()
