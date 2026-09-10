---
title: Allure测试报告基础
date: 2026-09-10
updated: 2026-09-10
tags:
  - python
  - pytest
  - allure
  - reporting
  - beginner
aliases:
  - Allure小白教程
status: active
level: beginner
---

# Allure测试报告基础

上一步：[[01-技术基础/Python/测试自动化基础/05-Playwright网页自动化基础|05-Playwright网页自动化基础]]

下一步：[[01-技术基础/Python/测试自动化基础/07-测试自动化综合实战|07-测试自动化综合实战]]

## 1. Allure 是什么

Allure 把测试运行产生的结果转换成可浏览的 HTML 报告，展示通过、失败、步骤、参数、附件、耗时、分类和历史趋势。

Allure Pytest 包含两个不同部分：

```text
allure-pytest：Python 插件，pytest 运行时写出原始结果
Allure CLI：读取原始结果并生成/打开 HTML 报告
```

只安装 `allure-pytest`，可以产生 `allure-results`，但没有 Allure CLI 就不能本地生成完整 HTML 报告。

## 2. 安装 Python 插件

```powershell
python -m pip install -U allure-pytest
python -m pytest --help | Select-String allure
```

## 3. 安装 Java

Allure Report CLI 需要 Java。检查：

```powershell
java -version
```

如果未安装，安装受支持的 JDK，并重新打开 PowerShell。企业电脑建议使用公司批准的软件源和 JDK 发行版。

## 4. 安装 Allure CLI

Windows 可选择项目官方说明支持的包管理方式。安装后验证：

```powershell
allure --version
```

如果 `allure` 找不到：

1. 关闭并重新打开 PowerShell；
2. 检查 Allure 的 `bin` 是否在 PATH；
3. 检查 Java 是否可用；
4. 执行 `Get-Command allure` 查看命令来源。

官方安装入口：[Install Allure Report](https://allurereport.org/docs/install/)

## 5. 生成第一份报告

测试文件：

```python
def test_add():
    assert 1 + 2 == 3
```

产生原始结果：

```powershell
python -m pytest --alluredir allure-results --clean-alluredir
```

临时生成并打开报告：

```powershell
allure serve allure-results
```

生成固定目录：

```powershell
allure generate allure-results -o allure-report --clean
allure open allure-report
```

区别：

- `allure serve`：临时生成并启动本地服务，适合查看；
- `allure generate`：输出固定 HTML 目录，适合归档；
- `allure open`：打开已生成的报告。

## 6. 为什么需要 `--clean-alluredir`

Allure 默认会把新结果追加到已有目录。若不清理，旧用例可能混入新报告。

```powershell
python -m pytest --alluredir allure-results --clean-alluredir
```

如果你有意合并多次运行，就不要清理，但必须在报告中说明合并范围。

## 7. 标题、描述和严重级别

```python
import allure


@allure.title("查询用户列表")
@allure.description("验证正常用户可以查询第一页用户列表")
@allure.severity(allure.severity_level.CRITICAL)
@allure.tag("api", "smoke")
def test_query_users():
    assert True
```

严重级别：

```python
allure.severity_level.BLOCKER
allure.severity_level.CRITICAL
allure.severity_level.NORMAL
allure.severity_level.MINOR
allure.severity_level.TRIVIAL
```

严重级别应根据业务影响定义，不要所有测试都标成 `BLOCKER`。

## 8. 业务层级

```python
import allure


@allure.epic("财务系统")
@allure.feature("用户管理")
@allure.story("查询用户")
def test_query_user():
    assert True
```

套件层级：

```python
@allure.parent_suite("API 自动化")
@allure.suite("用户服务")
@allure.sub_suite("查询接口")
def test_query_user():
    assert True
```

业务层级用于表达需求归属，套件层级用于表达测试组织。团队应统一命名口径。

## 9. Step

上下文方式：

```python
import allure


def test_order_flow():
    with allure.step("准备订单数据"):
        order = {"id": 1001, "amount": 20}

    with allure.step("提交订单"):
        result = {"code": 0, "data": order}

    with allure.step("验证提交结果"):
        assert result["code"] == 0
        assert result["data"]["id"] == order["id"]
```

装饰器方式：

```python
import allure


@allure.step("创建用户：{username}")
def create_user(username: str):
    return {"id": 1, "username": username}
```

Step 应表达业务动作，不要把每一行代码都包装成 Step。

## 10. 参数化标题

```python
import allure
import pytest


@pytest.mark.parametrize("username", ["alice", "bob"])
@allure.title("验证用户 {username} 可以登录")
def test_login(username):
    assert username
```

报告会显示每组参数。敏感参数需要脱敏：

```python
def test_authentication(token):
    allure.dynamic.parameter("token", "***")
    assert token
```

不要认为 Allure 的展示脱敏会自动清除底层结果文件中的所有敏感值，源数据和附件仍需单独检查。

## 11. 附件

文本：

```python
import allure

allure.attach(
    "业务校验通过",
    name="validation",
    attachment_type=allure.attachment_type.TEXT,
)
```

JSON：

```python
import json
import allure

safe_body = {"code": 0, "message": "success"}
allure.attach(
    json.dumps(safe_body, ensure_ascii=False, indent=2),
    name="response.json",
    attachment_type=allure.attachment_type.JSON,
)
```

文件：

```python
allure.attach.file(
    "artifacts/failure.png",
    name="失败截图",
    attachment_type=allure.attachment_type.PNG,
)
```

Playwright 截图 bytes：

```python
png_bytes = page.screenshot(full_page=True)
allure.attach(
    png_bytes,
    name="page",
    attachment_type=allure.attachment_type.PNG,
)
```

Selenium 截图 bytes：

```python
png_bytes = driver.get_screenshot_as_png()
allure.attach(
    png_bytes,
    name="page",
    attachment_type=allure.attachment_type.PNG,
)
```

## 12. 失败时自动截图

Playwright 示例：

```python
import allure
import pytest


@pytest.fixture(autouse=True)
def attach_screenshot_on_failure(request, page):
    yield
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        allure.attach(
            page.screenshot(full_page=True),
            name="failure-page",
            attachment_type=allure.attachment_type.PNG,
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
```

真实框架还要处理：

- 页面或浏览器可能已关闭；
- fixture 准备阶段可能失败；
- 截图动作本身可能异常；
- 多页面时要明确截取哪个页面；
- 清理失败也可能需要证据。

## 13. 链接到缺陷和用例系统

```python
import allure


@allure.issue("BUG-123", "登录失败缺陷")
@allure.testcase("TC-456", "登录测试用例")
def test_login():
    assert True
```

通过 pytest 配置 URL 模板：

```ini
[pytest]
addopts =
    --allure-link-pattern=issue:https://jira.example.test/browse/{}
    --allure-link-pattern=test_case:https://tms.example.test/case/{}
```

公开教程不要写企业真实地址，可使用占位域名。

## 14. 环境信息

在 `allure-results/environment.properties` 中写入非敏感环境信息：

```properties
Environment=UAT
Browser=Chromium
Python=3.x
OS=Windows
```

不要写 Token、数据库密码、内部 IP、Cookie 或用户个人数据。

## 15. pytest.ini 配置

```ini
[pytest]
testpaths = tests
addopts =
    -ra
    --alluredir=allure-results
    --clean-alluredir
markers =
    smoke: 核心冒烟测试
    api: 接口测试
    web: 网页测试
```

本地所有运行都会产生 Allure 结果。如果某些场景不需要报告，可不把参数固化到配置中。

## 16. 报告状态怎么理解

| 状态 | 含义 |
|---|---|
| Passed | 测试执行并通过断言 |
| Failed | 测试断言失败 |
| Broken | 测试代码、fixture 或环境异常 |
| Skipped | 测试被跳过 |
| Unknown | 适配器无法正常识别 |

`Broken` 不等于产品缺陷，常见原因包括浏览器启动失败、环境变量缺失和测试代码异常。

## 17. 历史趋势

Allure 的趋势依赖历史数据。生成新报告前需要把上一份报告的 `history` 放入新结果对应位置，具体目录随 Allure 版本和 CI 集成方式而定。

历史趋势只有在以下条件稳定时才有意义：

- 用例 ID 或全名稳定；
- 参数化规则稳定；
- 报告未混入旧结果；
- 环境和版本有记录；
- 重试和跳过策略透明。

## 18. CI 中使用

典型流程：

```text
安装 Python 依赖
→ 安装浏览器
→ 执行 pytest 并生成 allure-results
→ 生成或发布 Allure 报告
→ 保留失败截图、Trace 和日志
```

CI 产物必须设置访问权限和保留期限。Playwright Trace、截图和接口响应可能包含敏感数据。

## 19. 常见问题

报告为空：确认运行 pytest 时指定了 `--alluredir`，并检查目录里是否有 JSON 文件。

报告混入旧用例：使用 `--clean-alluredir`。

`allure` 命令不存在：CLI 未安装或 PATH 未刷新。

Java 错误：检查 `java -version` 和 JDK 配置。

附件打不开：检查文件是否在测试执行时存在、类型是否正确。

报告中泄露 Token：源头日志或附件未脱敏，删除报告不足以解决已经上传的泄露，需要按安全流程轮换凭据。

## 20. 练习

- [ ] 生成一份 Allure 报告
- [ ] 添加 title、description 和 severity
- [ ] 用 3 个业务 Step 展示测试过程
- [ ] 添加 JSON 和截图附件
- [ ] 故意制造一条 Failed 和一条 Broken
- [ ] 对比两者在报告中的表现
- [ ] 检查 `allure-results` 是否含敏感信息

## 21. 官方资料

- [Allure Pytest 入门](https://allurereport.org/docs/pytest/)
- [Allure Pytest 配置](https://allurereport.org/docs/pytest-configuration/)
- [Allure 安装](https://allurereport.org/docs/install/)
