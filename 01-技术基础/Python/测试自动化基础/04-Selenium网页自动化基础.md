---
title: Selenium网页自动化基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - selenium
  - web-testing
  - beginner
aliases:
  - Selenium小白教程
status: active
level: beginner
---

# Selenium网页自动化基础

上一步：[[01-技术基础/Python/测试自动化基础/03-requests接口测试基础|03-requests接口测试基础]]

下一步：[[01-技术基础/Python/测试自动化基础/05-Playwright网页自动化基础|05-Playwright网页自动化基础]]

## 1. Selenium 是什么

Selenium WebDriver 通过标准协议控制真实浏览器，支持 Chrome、Edge、Firefox、Safari 等。适合跨浏览器 UI 自动化、遗留系统和已有 Selenium 生态的项目。

现代 Selenium 通常由 Selenium Manager 自动管理浏览器 Driver，不必像旧教程那样手工下载 `chromedriver.exe`。企业网络受限时仍可能需要手工配置。

## 2. 安装

```powershell
python -m pip install -U selenium pytest
python -c "import selenium; print(selenium.__version__)"
```

确保本机已安装 Chrome 或 Edge。

## 3. 第一个脚本

```python
from selenium import webdriver

driver = webdriver.Chrome()

try:
    driver.get("https://www.selenium.dev")
    print(driver.title)
finally:
    driver.quit()
```

必须使用 `quit()` 关闭整个浏览器会话。`close()` 只关闭当前窗口。

## 4. 第一个 pytest 用例

```python
import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    yield browser
    browser.quit()


def test_page_title(driver):
    driver.get("https://www.selenium.dev")
    assert "Selenium" in driver.title
```

运行：

```powershell
python -m pytest -v
```

## 5. 元素定位

```python
from selenium.webdriver.common.by import By

driver.find_element(By.ID, "username")
driver.find_element(By.NAME, "password")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
driver.find_element(By.XPATH, "//button[normalize-space()='登录']")
driver.find_element(By.LINK_TEXT, "忘记密码")
driver.find_elements(By.CSS_SELECTOR, ".table-row")
```

优先级建议：

1. 稳定且唯一的 `id`；
2. 专为测试提供的 `data-testid`；
3. 稳定的 `name`；
4. 语义清晰的 CSS；
5. 简短、相对的 XPath；
6. 避免绝对 XPath 和动态 class。

推荐：

```python
driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']")
```

不推荐：

```python
driver.find_element(By.XPATH, "/html/body/div[2]/div/div/form/button")
```

## 6. 常用操作

```python
element.click()
element.send_keys("hello")
element.clear()
element.text
element.get_attribute("value")
element.is_displayed()
element.is_enabled()
element.is_selected()
```

完整表单示例：

```python
from selenium.webdriver.common.by import By

driver.get("https://www.selenium.dev/selenium/web/web-form.html")

text_box = driver.find_element(By.NAME, "my-text")
submit_button = driver.find_element(By.CSS_SELECTOR, "button")

text_box.send_keys("Selenium")
submit_button.click()

message = driver.find_element(By.ID, "message")
assert message.text == "Received!"
```

## 7. 等待：UI 自动化的核心

不要使用大量固定 `time.sleep()`。页面速度变化时，固定等待要么太短导致失败，要么太长浪费时间。

显式等待：

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)

login_button = wait.until(
    EC.element_to_be_clickable((By.ID, "login-button"))
)
login_button.click()

message = wait.until(
    EC.visibility_of_element_located((By.ID, "message"))
)
assert message.text == "Received!"
```

常用条件：

```python
EC.presence_of_element_located(locator)
EC.visibility_of_element_located(locator)
EC.element_to_be_clickable(locator)
EC.invisibility_of_element_located(locator)
EC.url_contains("dashboard")
EC.title_contains("Home")
EC.alert_is_present()
```

隐式等待：

```python
driver.implicitly_wait(5)
```

不要混用较大的隐式等待和显式等待，否则超时时间可能变得难以理解。项目中建议以显式等待为主。

## 8. 下拉框、复选框和键盘

```python
from selenium.webdriver.support.ui import Select

select = Select(driver.find_element(By.NAME, "my-select"))
select.select_by_visible_text("Two")
select.select_by_value("2")
```

```python
checkbox = driver.find_element(By.ID, "my-check")
if not checkbox.is_selected():
    checkbox.click()
```

```python
from selenium.webdriver.common.keys import Keys

input_box.send_keys(Keys.CONTROL, "a")
input_box.send_keys("new value")
input_box.send_keys(Keys.ENTER)
```

## 9. Alert、iframe 和窗口

Alert：

```python
alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
assert "确认" in alert.text
alert.accept()
```

iframe：

```python
frame = driver.find_element(By.CSS_SELECTOR, "iframe")
driver.switch_to.frame(frame)
driver.find_element(By.ID, "inside-frame").click()
driver.switch_to.default_content()
```

新窗口：

```python
original = driver.current_window_handle
before = set(driver.window_handles)

driver.find_element(By.ID, "open-window").click()

WebDriverWait(driver, 10).until(
    lambda current_driver: len(current_driver.window_handles) > len(before)
)

new_handle = (set(driver.window_handles) - before).pop()
driver.switch_to.window(new_handle)
driver.close()
driver.switch_to.window(original)
```

## 10. 截图和页面信息

```python
driver.save_screenshot("artifacts/failure.png")
html = driver.page_source
current_url = driver.current_url
title = driver.title
```

失败截图 fixture：

```python
from pathlib import Path
import pytest
from selenium import webdriver


@pytest.fixture
def driver(request):
    browser = webdriver.Chrome()
    yield browser

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        Path("artifacts").mkdir(exist_ok=True)
        browser.save_screenshot(f"artifacts/{request.node.name}.png")

    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
```

## 11. 浏览器配置

无头模式：

```python
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1440,900")

driver = webdriver.Chrome(options=options)
```

下载目录：

```python
from pathlib import Path

download_dir = str(Path("downloads").resolve())
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
    },
)
```

## 12. Page Object

`pages/login_page.py`：

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def open(self, base_url: str):
        self.driver.get(f"{base_url.rstrip('/')}/login")

    def login(self, username: str, password: str):
        self.wait.until(EC.visibility_of_element_located(self.USERNAME)).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
```

测试只描述业务行为：

```python
def test_login(driver):
    page = LoginPage(driver)
    page.open("https://example.test")
    page.login("test-user", "test-password")
    assert "/home" in driver.current_url
```

真实凭据必须来自环境变量或安全凭据系统。

## 13. 常见错误

- `NoSuchElementException`：定位器错误、页面未加载、元素在 iframe；
- `TimeoutException`：等待条件不成立、环境慢、功能异常；
- `StaleElementReferenceException`：页面刷新后旧元素引用失效，重新定位；
- `ElementClickInterceptedException`：遮罩、弹窗或动画挡住元素；
- Driver 下载失败：检查代理、防火墙和浏览器版本；
- 本地成功、CI 失败：检查窗口大小、无头模式、字体、时区和测试数据。

## 14. 稳定性原则

- 每条用例独立创建或清理状态；
- 使用显式等待，不依赖固定睡眠；
- 优先稳定测试属性；
- 不跨用例复用已登录的脏浏览器；
- 失败时保存 URL、截图和关键日志；
- 同时验证页面行为和后端业务结果；
- 不通过执行 JavaScript 强行点击来掩盖真实可用性问题。

## 15. 练习

- [ ] 打开官方 Web Form
- [ ] 填写文本并提交
- [ ] 用显式等待检查成功消息
- [ ] 选择下拉框和复选框
- [ ] 截取失败页面
- [ ] 封装一个 Page Object

## 16. 官方资料

- [Selenium 入门](https://www.selenium.dev/documentation/webdriver/getting_started/)
- [Selenium Python API](https://www.selenium.dev/selenium/docs/api/py/)
- [等待策略](https://www.selenium.dev/documentation/webdriver/waits/)
