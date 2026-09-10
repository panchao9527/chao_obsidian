---
title: Playwright网页自动化基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - playwright
  - web-testing
  - beginner
aliases:
  - Playwright Python小白教程
status: active
level: beginner
---

# Playwright网页自动化基础

上一步：[[01-技术基础/Python/测试自动化基础/04-Selenium网页自动化基础|04-Selenium网页自动化基础]]

下一步：[[01-技术基础/Python/测试自动化基础/06-Allure测试报告基础|06-Allure测试报告基础]]

## 1. Playwright 是什么

Playwright 是现代浏览器自动化框架，支持 Chromium、Firefox 和 WebKit。Python 可以使用同步或异步 API；初学者配合 pytest 时建议先使用同步 API 和官方 `pytest-playwright` 插件。

它的核心优势包括：

- Locator 自动等待；
- Web-first 断言；
- 每条测试可使用隔离的 BrowserContext；
- 支持截图、视频、网络监听和 Trace；
- 支持多浏览器和设备模拟。

## 2. 安装

```powershell
python -m pip install -U pytest-playwright
python -m playwright install chromium
```

安装全部默认浏览器：

```powershell
python -m playwright install
```

Playwright 升级后可能需要重新安装匹配的浏览器二进制。

## 3. 第一个 pytest 用例

`tests/web/test_example.py`：

```python
import re
from playwright.sync_api import Page, expect


def test_has_title(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))
```

运行：

```powershell
python -m pytest
```

默认无头运行 Chromium。显示浏览器：

```powershell
python -m pytest --headed
```

指定浏览器：

```powershell
python -m pytest --browser chromium
python -m pytest --browser firefox
python -m pytest --browser webkit
```

## 4. Page、BrowserContext 和 Browser

```text
Browser：浏览器进程
└─ BrowserContext：隔离会话，类似独立无痕窗口
   └─ Page：标签页
```

官方 pytest 插件提供 `page` fixture。通常每条测试使用隔离上下文，减少 Cookie 和 LocalStorage 污染。

## 5. Locator

推荐按用户可感知的语义定位：

```python
page.get_by_role("button", name="登录")
page.get_by_label("用户名")
page.get_by_placeholder("请输入用户名")
page.get_by_text("提交成功")
page.get_by_test_id("login-submit")
page.locator("input[name='username']")
```

优先级建议：

1. `get_by_role`；
2. `get_by_label`；
3. `get_by_placeholder`；
4. `get_by_text`；
5. `get_by_test_id`；
6. CSS Locator；
7. 最后才考虑复杂 XPath。

Locator 可以链式缩小范围：

```python
row = page.get_by_role("row").filter(has_text="alice")
row.get_by_role("button", name="编辑").click()
```

## 6. 常用操作

```python
page.goto("https://example.com")
page.get_by_label("用户名").fill("alice")
page.get_by_label("密码").fill("test-password")
page.get_by_role("button", name="登录").click()
page.get_by_label("同意协议").check()
page.get_by_label("城市").select_option("shanghai")
page.get_by_role("button", name="上传").set_input_files("sample.txt")
```

`fill()` 会先清空输入框再输入；`type()` 更接近逐字符输入，但多数测试使用 `fill()` 更稳定。

## 7. Web-first 断言

```python
from playwright.sync_api import expect

expect(page).to_have_url("https://example.com/home")
expect(page).to_have_title("Home")
expect(page.get_by_role("heading", name="欢迎")).to_be_visible()
expect(page.get_by_test_id("status")).to_have_text("成功")
expect(page.get_by_role("row")).to_have_count(10)
expect(page.get_by_label("用户名")).to_have_value("alice")
expect(page.get_by_role("button", name="提交")).to_be_enabled()
```

这些断言会在超时前反复检查条件，比立即读取文本后普通 `assert` 更适合动态网页。

不推荐：

```python
assert page.locator("#status").text_content() == "成功"
```

推荐：

```python
expect(page.locator("#status")).to_have_text("成功")
```

## 8. 自动等待和显式等待

Playwright 在执行点击、填写和断言前会自动检查元素是否存在、可见、稳定并可交互。

不要使用：

```python
page.wait_for_timeout(5000)
```

优先等待业务条件：

```python
expect(page.get_by_text("处理完成")).to_be_visible(timeout=10_000)
page.wait_for_url("**/dashboard")
page.wait_for_load_state("domcontentloaded")
```

`networkidle` 不适合所有现代页面，因为长连接和持续请求可能永远不空闲。

## 9. 弹窗、新页面和下载

Dialog：

```python
page.on("dialog", lambda dialog: dialog.accept())
page.get_by_role("button", name="删除").click()
```

新页面：

```python
with page.expect_popup() as popup_info:
    page.get_by_role("link", name="打开详情").click()

detail_page = popup_info.value
detail_page.wait_for_load_state()
```

下载：

```python
with page.expect_download() as download_info:
    page.get_by_role("button", name="下载").click()

download = download_info.value
download.save_as("artifacts/report.xlsx")
```

## 10. iframe

```python
frame = page.frame_locator("iframe[name='payment']")
frame.get_by_label("卡号").fill("4111111111111111")
```

优先 `frame_locator`，不要手工切换后忘记切回来。

## 11. 截图、视频和 Trace

截图：

```python
page.screenshot(path="artifacts/page.png", full_page=True)
page.get_by_test_id("result").screenshot(path="artifacts/result.png")
```

pytest 插件保留 Trace：

```powershell
python -m pytest --tracing retain-on-failure
```

其他模式：

```powershell
python -m pytest --tracing on
python -m pytest --tracing off
```

打开 Trace：

```powershell
python -m playwright show-trace '绝对路径\trace.zip'
```

Trace 可能包含页面文本、网络请求、Cookie、源码片段和输入内容，不能当作无敏感信息的普通附件公开上传。

视频和截图选项可通过 pytest 插件参数配置：

```powershell
python -m pytest --video retain-on-failure --screenshot only-on-failure
```

## 12. Codegen

录制操作生成初始代码：

```powershell
python -m playwright codegen https://example.com
```

Codegen 适合探索 Locator 和快速生成草稿。生成代码仍需人工整理：

- 删除重复步骤；
- 替换硬编码测试数据；
- 补充业务断言；
- 抽取 Page Object；
- 增加清理逻辑；
- 避免记录真实密码。

## 13. 网络监听和接口配合

等待响应：

```python
with page.expect_response(lambda response: "/api/orders" in response.url) as response_info:
    page.get_by_role("button", name="提交订单").click()

response = response_info.value
assert response.status == 200
```

模拟响应：

```python
def handle_route(route):
    route.fulfill(
        status=200,
        content_type="application/json",
        body='{"code": 0, "data": []}',
    )


page.route("**/api/items", handle_route)
```

Mock 测试只能证明前端在模拟响应下的行为，不能证明真实后端集成成功。

## 14. 登录状态复用

可以保存测试账号的登录状态：

```python
browser_context.storage_state(path="playwright/.auth/user.json")
```

加载：

```python
context = browser.new_context(storage_state="playwright/.auth/user.json")
```

登录状态文件可能包含 Cookie 和 Token，必须加入 `.gitignore`：

```gitignore
playwright/.auth/
```

## 15. Page Object

```python
from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_label("用户名")
        self.password = page.get_by_label("密码")
        self.submit = page.get_by_role("button", name="登录")

    def open(self, base_url: str):
        self.page.goto(f"{base_url.rstrip('/')}/login")

    def login(self, username: str, password: str):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()

    def assert_login_success(self):
        expect(self.page).to_have_url("**/home")
```

Page Object 封装页面行为，不要把所有业务断言都塞进页面类。

## 16. 配置 pytest

`pytest.ini`：

```ini
[pytest]
testpaths = tests
addopts = -ra
markers =
    web: Web UI 测试
    smoke: 冒烟测试
```

`conftest.py` 设置 base URL：

```python
import os
import pytest


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("TEST_BASE_URL", "https://example.com")
```

## 17. Selenium 还是 Playwright

| 场景 | 推荐 |
|---|---|
| 新建现代 Web 自动化项目 | 优先 Playwright |
| 已有大量 Selenium 用例 | 继续维护并渐进改造 |
| 必须使用成熟 Grid 生态 | Selenium |
| 需要 Chromium、Firefox、WebKit | Playwright |
| 需要强大的 Trace 和网络控制 | Playwright |
| 团队已有稳定 Selenium 技术栈 | 根据迁移成本决定 |

不要为了追求新工具重写所有稳定用例。先比较维护成本、浏览器范围、团队能力和 CI 条件。

## 18. 常见错误

- `Executable doesn't exist`：运行 `python -m playwright install chromium`；
- 严格模式错误：Locator 匹配多个元素，需要缩小范围；
- 元素超时：定位错误、页面状态不对或业务失败；
- CI 失败：缺少浏览器依赖、环境变量、字体或网络权限；
- 测试偶发失败：固定数据、跨用例状态、动画、错误等待方式；
- Trace 无法公开：其中可能含敏感页面和网络数据。

## 19. 练习

- [ ] 安装 Chromium
- [ ] 使用 `page` fixture 打开网页
- [ ] 用 Role 和 Label 定位元素
- [ ] 使用 Web-first 断言
- [ ] 运行 headed 模式
- [ ] 失败时保留 Trace
- [ ] 使用 Codegen 生成草稿并人工整理

## 20. 官方资料

- [Playwright Python 安装](https://playwright.dev/python/docs/intro)
- [Locator](https://playwright.dev/python/docs/locators)
- [断言](https://playwright.dev/python/docs/test-assertions)
- [Trace Viewer](https://playwright.dev/python/docs/trace-viewer)
- [浏览器管理](https://playwright.dev/python/docs/browsers)
