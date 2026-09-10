---
title: yt-dlp 音视频下载从入门到实战
aliases: [yt-dlp使用教程, 音视频下载指南]
type: 工具实战
project: 通用
status: 部分实测
updated: 2026-09-09
version: 2026.8.19
tags: [Python, yt-dlp, 音视频, FFmpeg, 工具实战]
---

# yt-dlp 音视频下载从入门到实战

返回：[[07-工具与工作流/00-工具与工作流导航|工具与工作流导航]]

关联：[[07-工具与工作流/网页采集/Scrapling 从入门到实战|Scrapling 从入门到实战]]

## 1. 它能做什么，与 Scrapling 怎么分工

yt-dlp 是命令行音视频下载工具。一般输入**媒体页面地址**，它调用对应站点的提取器获取媒体信息、可用格式及下载地址，再下载文件并调用 FFmpeg 做必要的后处理。

| 需求 | 优先工具 |
| --- | --- |
| 收集文章、视频列表、作者、详情页地址 | Scrapling |
| 下载支持站点的视频或音频 | yt-dlp |
| 选择清晰度、下载字幕、批量处理播放列表 | yt-dlp |
| 合并独立音视频流、转成 MP3、重新编码 | FFmpeg，通常由 yt-dlp 调用 |

可以组合使用：Scrapling 收集详情页 URL → 写入 `urls.txt` → yt-dlp 下载 → 验证文件。优先传媒体页面地址，直接媒体地址可能过期或依赖 Cookie、请求头和来源 IP。

“支持的网站列表”不是当前一定可用的承诺，站点接口会变化。工具也不保证下载 DRM 内容或取得原本没有的访问权限。以下用法适用于你有权保存的媒体；无需为了入门先配置账号或 Cookie。

## 2. 版本与学习路线

本文命令基线为 **yt-dlp 2026.8.19、Windows PowerShell**。安装包来自 PyPI。官方源码补充核对提交：`bbc809a1161d3bfca51fa36f59dda35556ee85a0`；源码主分支可能领先发行包，所以以本机 `--help` 和实际结果为准。

**新环境建议 Python 3.11+。** 本次用 Python 3.10 完成本地验证，但程序明确输出弃用提示，不建议再把 3.10 当作新项目首选。

学习顺序：安装 → 查看信息和格式 → 下载单个媒体 → 音频/字幕 → 批量与归档 → Python 集成 → 排错。初次不要直接尝试整个频道或大型播放列表。

同目录 `yt-dlp示例` 包含：

| 文件 | 用途 |
| --- | --- |
| `requirements.txt` | 固定 yt-dlp 版本与默认依赖 |
| `inspect_media.py` | 接收单个 URL，提取精简元数据，不下载媒体 |
| `verify_local.py` | 自动生成测试 WAV，经本地 HTTP 验证下载和归档 |
| `.gitignore` | 排除输出、虚拟环境和 Cookie 文件 |

## 3. Windows 安装与检查

### 3.1 推荐：独立 Python 环境

以下在 `yt-dlp示例` 目录执行。如果电脑只有较老的 Python，先安装新版本并确认 `python --version` 指向预期解释器。

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\yt-dlp.exe --version
```

`requirements.txt` 内容是 `yt-dlp[default]==2026.8.19`。使用默认依赖包便于获得推荐的 Python 依赖；它不会替你安装 FFmpeg 或外部 JavaScript 运行时。无需激活虚拟环境，也无需修改 PowerShell 全局执行策略。

后文为了缩短命令，先定义路径和目标 URL。**每个新 PowerShell 窗口都要重新定义**：

```powershell
$Ytdlp = (Resolve-Path '.\.venv\Scripts\yt-dlp.exe').Path
$MediaUrl = '替换为你有权下载的单个媒体页面地址'
& $Ytdlp --version
```

`$MediaUrl` 是待替换占位值，不可直接拿它运行下载。实际调用通过 `&` 执行程序路径，适用于路径带空格的情形。

### 3.2 另一种方式：独立 EXE

不需要 Python 编程时，可以从 [官方 Releases](https://github.com/yt-dlp/yt-dlp/releases) 下载适合 Windows 架构的独立可执行文件，再从所在目录运行 `./yt-dlp.exe --version`。这与 Python 虚拟环境是两种独立安装方式，不要混淆更新入口。

### 3.3 FFmpeg 与 ffprobe

FFmpeg 用来处理媒体，ffprobe 用来探测流信息。独立视频流与音频流合并、音频转码等功能需要它们。**`pip install ffmpeg` 不能代替安装这两个可执行程序。**

从 [FFmpeg 下载入口](https://ffmpeg.org/download.html) 或 [yt-dlp 的 FFmpeg 构建仓库](https://github.com/yt-dlp/FFmpeg-Builds) 获取对应系统的构建，解压后找到包含 `ffmpeg.exe` 和 `ffprobe.exe` 的目录。示例位置可以是 `D:\tools\ffmpeg\bin`，按实际路径替换：

```powershell
& 'D:\tools\ffmpeg\bin\ffmpeg.exe' -version
& 'D:\tools\ffmpeg\bin\ffprobe.exe' -version
& $Ytdlp --ignore-config --ffmpeg-location 'D:\tools\ffmpeg\bin' --simulate $MediaUrl
```

可将目录加入 PATH，也可在每条需要后处理的命令中添加 `--ffmpeg-location`。后文 FFmpeg 相关命令假设它们已在 PATH，或者你已补充此参数。模拟成功不代表转码成功。

### 3.4 JavaScript 运行时：部分平台需要

当前官方文档建议完整 YouTube 支持同时具备 `yt-dlp-ejs` 和受支持的 JavaScript 运行时。默认 extra 安装了 Python 侧组件，但不等于运行时也存在。

先查看本机帮助：

```powershell
& $Ytdlp --help
node --version
```

例如启用本机已安装且版本符合要求的 Node：

```powershell
& $Ytdlp --ignore-config --js-runtimes node --simulate $MediaUrl
```

该版本默认启用的运行时是 Deno，安装了 Node 不代表自动选用。版本要求和平台变化以 [EJS 官方说明](https://github.com/yt-dlp/yt-dlp/wiki/EJS) 为准。本文未验证真实平台的 JavaScript 挑战处理，不承诺安装运行时就能解决所有下载失败。

## 4. 先看信息，再下载

### 查看格式列表

```powershell
& $Ytdlp --ignore-config --no-playlist -F $MediaUrl
```

`-F` 是列出可用格式，`-f` 才是选择格式；大小写含义不同。输出中关注格式 ID、扩展名、分辨率、音视频编码以及 `audio only` / `video only`。

### 只提取信息

```powershell
& $Ytdlp --ignore-config --no-playlist --simulate --print '%(id)s | %(title)s | %(duration)s' $MediaUrl
```

`--simulate` 不下载媒体，不写常规输出文件，但会发网络请求读取信息。时长字段可能未知，不能把空值当成零秒。

如果要保存元数据文件：

```powershell
& $Ytdlp --ignore-config --no-playlist --skip-download --write-info-json -P output -o '%(id)s.%(ext)s' $MediaUrl
```

这里使用 `--skip-download`，允许写元数据。不要误以为它与 `--simulate` 完全等价。完整 info JSON 可能包含媒体地址或其他敏感信息，分享前检查；精简信息优先使用配套 Python 脚本。

## 5. 下载第一个视频

```powershell
& $Ytdlp --ignore-config --no-playlist -P output -o '%(title).100B [%(id)s].%(ext)s' $MediaUrl
```

参数解释：

- `--ignore-config` 避免本机已有配置悄悄改变行为，方便复现。
- `--no-playlist` 用于视频地址同时包含播放列表上下文的场景；不要把纯播放列表 URL 当作“只下载一个视频”的可靠输入。
- `-P output` 指定输出目录。
- `-o` 指定文件名模板；保留 ID 防止同名标题冲突。
- `.100B` 限制标题部分的字节长度；最终文件名长度还包含 ID 和扩展名。

不要直接写死 `video.mp4`，应保留 `%(ext)s`。不同来源可能得到 WebM、MP4 或其他格式。PowerShell 中模板可用单引号；如果移植到 Windows `.bat`，百分号通常需要写成 `%%`。

下载后检查真实文件大小、播放和音轨。独立音画流常见于高质量格式，若缺 FFmpeg，可能无法完成合并；临时文件存在不等于最终产物成功。

## 6. 选择清晰度和编码

### 严格限制不高于 1080p

```powershell
& $Ytdlp --ignore-config --no-playlist -f 'bv*[height<=1080]+ba/b[height<=1080]' -P output $MediaUrl
```

表达式含义：优先选符合高度限制的最佳视频格式并配音频；斜杠后面是找不到前者时的备用组合格式。**备用分支也限制高度**，避免不小心回退到高于 1080p 的视频。格式高度未知或没有符合条件的格式时可能失败，应先看 `-F`。

### 按格式 ID 精确选

先从本次 `-F` 输出选择格式 ID，再用 `-f '视频ID+音频ID'`。示例中的中文是占位符，不能直接执行，也不能把某个站点的视频 ID 套用到另一个站点。

### MP4 不等于 H.264，也不等于重新编码

| 参数 | 作用 | 不能保证什么 |
| --- | --- | --- |
| `--merge-output-format mp4` | 需要合并时指定容器 | 不保证编码变成 H.264，也不影响无需合并的情况 |
| `--remux-video mp4` | 尝试重新封装 | 不重新编码，编码不兼容时可能失败 |
| `--recode-video mp4` | 按需要转换输出格式 | 不能只靠扩展名保证指定的视频编码；已有同格式可能跳过 |

若播放器明确要求 H.264/AAC，需要选择兼容流或另行设置 FFmpeg 编码参数，并用 ffprobe 验证。优先确认兼容性需求，不要无理由反复转码。

## 7. 下载音乐或从视频提取音频

### 优先保留音频原格式

```powershell
& $Ytdlp --ignore-config --no-playlist -f 'ba/b' -P output $MediaUrl
```

`ba` 是最佳纯音频格式；`/b` 是兼容回退，可能返回包含视频的文件。因此这条命令不是“任何站点都输出纯音频”。

### 需要通用 MP3 文件

```powershell
& $Ytdlp --ignore-config --no-playlist -f 'ba/b' -x --audio-format mp3 --audio-quality 0 -P output -o '%(title).100B [%(id)s].%(ext)s' $MediaUrl
```

`-x` 提取音频，`--audio-format mp3` 转换为 MP3，需要 FFmpeg/ffprobe。质量参数 `0` 是高质量 VBR 设置，不代表恢复成无损原始音质，也不保证固定码率。

如果源音频已经是合适格式，保留原格式可以避免再次有损转码。音乐平台可能只提供试听片段；“成功生成 MP3”不代表取得完整曲目，应核对时长和内容。

## 8. 字幕、封面和元数据

先查看可用字幕：

```powershell
& $Ytdlp --ignore-config --list-subs $MediaUrl
```

下载指定语言字幕但不下载视频：

```powershell
& $Ytdlp --ignore-config --skip-download --write-subs --sub-langs 'en,zh.*' --sub-format 'srt/best' -P output $MediaUrl
```

`zh.*` 是语言代码匹配模式，实际有哪些语言以列表为准。`--write-subs` 和 `--write-auto-subs` 分别控制普通字幕和自动生成字幕；自动字幕可能含识别错误，也不等于翻译功能。

希望将下载的字幕转换为 SRT，可增加 `--convert-subs srt`，需要 FFmpeg。`--embed-subs` 是嵌入字幕轨，不是把文字烧录进画面，具体支持取决于容器。

封面和元数据示例：

```powershell
& $Ytdlp --ignore-config --no-playlist --write-thumbnail --write-info-json --embed-metadata -P output $MediaUrl
```

封面写入独立文件，`--embed-thumbnail` 才尝试嵌入媒体。不同容器和后处理依赖支持不同，不应默认所有格式都能嵌入。

## 9. 批量下载、播放列表与归档

### URL 清单

创建 UTF-8 `urls.txt`，每行一个媒体页面地址。先用少量已知链接试跑：

```powershell
& $Ytdlp --ignore-config --no-playlist --simulate -a urls.txt
& $Ytdlp --ignore-config --no-playlist -a urls.txt --download-archive output/downloaded.txt -P output -o '%(extractor_key)s/%(title).100B [%(id)s].%(ext)s'
```

`--download-archive` 记录已下载媒体，后续运行跳过。它不是磁盘文件目录，也不是断点文件。**删除媒体文件但保留归档后，重新运行仍可能跳过。** 不要为了重下一个文件就删除整个长期归档；可以为明确的重下任务使用独立归档路径。

### 播放列表前 3 项

```powershell
$PlaylistUrl = '替换为播放列表地址'
& $Ytdlp --ignore-config --yes-playlist --playlist-items '1:3' --simulate $PlaylistUrl
& $Ytdlp --ignore-config --yes-playlist --playlist-items '1:3' --download-archive output/playlist-archive.txt -P output -o '%(playlist_title)s/%(playlist_index)03d - %(title).100B [%(id)s].%(ext)s' $PlaylistUrl
```

列表序号随来源变化可能改变，因此文件名仍保留媒体 ID。首次限定少量条目，不要直接对整个频道执行大规模下载。需要审计失败时记录每项结果，不能只看最后一行提示。

## 10. 断点、限速和失败处理

```powershell
& $Ytdlp --ignore-config --no-playlist --continue --limit-rate 2M --retries 3 --fragment-retries 3 --sleep-interval 2 --max-sleep-interval 5 -P output $MediaUrl
```

- `--continue` 尝试续传；能否恢复取决于源站、协议和临时文件，不能保证所有下载都可续传。
- `--limit-rate 2M` 是字节速率限制，别把它等同于 2 Mbps。
- `--retries` 与 `--fragment-retries` 分别限制一般下载和分片重试。
- 下载间隔不等于限制每一个元数据请求的频率。

遇到 429 应降低频率并检查服务限制；持续 403 则先检查是否链接过期、需要授权或站点发生变化。不要把无限重试当作恢复策略。

长期任务建议分开管理：输入清单、媒体目录、归档文件、运行日志和验证报告。下载完成后再整理文件，避免在程序合并或转码期间移动临时文件。

## 11. 登录 Cookie 和调试日志

公开内容通常先不带 Cookie。对于确实需要登录且你有权访问的内容，可以参考以下方式：

```powershell
& $Ytdlp --ignore-config --cookies-from-browser chrome --simulate $MediaUrl
```

它读取本机浏览器登录状态，可能受浏览器锁、加密机制或系统权限影响。仅在确认账号和目标站点后使用；不要分享导出的 Cookie 文件，不把它提交到知识库。登录成功也不等于 DRM 内容可下载。

诊断命令：

```powershell
& $Ytdlp --ignore-config --verbose --simulate $MediaUrl
```

先用它检查版本、FFmpeg、运行时和提取器信息。分享日志前检查 URL 查询参数、Token、Cookie 和私人内容标题；`--verbose` 不代表日志已脱敏。

## 12. Python API：把结果接入自动化

运行配套脚本：

```powershell
.\.venv\Scripts\python.exe -X utf8 inspect_media.py $MediaUrl --output output/summary.json
```

核心模式是 `with yt_dlp.YoutubeDL(options) as ydl:`，通过 `ydl.extract_info(url, download=False)` 只提取信息。脚本筛选 ID、标题、时长、作者和格式摘要，避免默认保存整份复杂对象；结果仍可能含私人标题/页面 URL，分享前需要检查。

需要下载时可调用 `ydl.download([url])` 并检查返回值，或 `extract_info(..., download=True)`。不要依赖终端输出格式解析业务结果，也不要认为下载 progress hook 的 `finished` 表示所有后处理已经结束。

与 Scrapling 组合时，先清洗、去重并核对详情页地址，再传入 yt-dlp。不要把网页中的任意文本拼接成 shell 命令；Python 调用 API 或用参数列表执行子进程更容易控制。

## 13. 无第三方平台依赖的本地验收

运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 verify_local.py
```

它完成以下工作：

1. 用 Python 标准库生成 1 秒静音 WAV，16,044 字节。
2. 在随机回环端口启动临时 HTTP 服务，只提供测试目录。
3. 模拟提取元数据，再通过 `-a` 清单真实下载。
4. 比较下载前后 SHA-256，确认内容一致。
5. 在临时目录删除刚下载的测试文件，再次运行并确认归档阻止重下。
6. 调用 `inspect_media.py` 验证 Python API，写出 `output/verification.json`。
7. 关闭服务器、清理临时目录，保留精简验证报告。

脚本中的回环地址是可控测试环境，不应据此推导任意外部 URL 都可以安全交给下载器。测试仅覆盖直链音频，不覆盖站点提取器、HLS/DASH、DRM 或 FFmpeg。

## 14. 常见问题速查

| 现象 | 检查与处理 |
| --- | --- |
| 找不到 yt-dlp | 检查 `.venv` 路径和 `$Ytdlp` 是否在当前窗口定义 |
| Python 3.10 弃用提示 | 新建 Python 3.11+ 环境，再安装依赖 |
| ffmpeg/ffprobe not found | 安装实际可执行程序，配置 PATH 或 `--ffmpeg-location` |
| 视频没有声音 | 检查是否只有视频流、音画合并是否完成 |
| MP4 无法播放 | 查真实编码，容器后缀不保证播放器兼容 |
| Requested format is not available | 重跑 `-F`，不要沿用其他视频的格式 ID |
| 找不到字幕 | `--list-subs` 看语言与普通/自动字幕来源 |
| 生成文件很短 | 核对试听/预览、源时长和下载结果 |
| 已删除文件却不重新下载 | 检查 download archive 是否仍记录该媒体 |
| 403/429 | 检查授权、限流、链接时效和提取器更新 |
| YouTube JavaScript 提示 | 按 EJS 文档核对组件、运行时和版本 |
| 改参数似乎无效 | 用 `--ignore-config` 排除已有配置影响 |
| 文件名过长 | 限制标题长度、缩短输出目录、保留媒体 ID |
| 进度到 100% 但没有最终文件 | 看后续 FFmpeg 合并/转码日志和退出码 |

更新方式区分安装来源：pip 环境使用 `python -m pip install -U "yt-dlp[default]"`，独立发行 EXE 使用 `yt-dlp -U`。官方主分支文档推荐日常用户考虑 nightly，以获得较新的站点修复；本文为复现固定发行版。需要切换时先在隔离环境试验，不默默改变现有任务的版本。

## 15. 本次验证结果

验证日期：2026-09-09；环境：Windows、Python 3.10、yt-dlp 2026.8.19、yt-dlp-ejs 0.8.0。

| 项目 | 状态 | 证据 |
| --- | --- | --- |
| 安装与依赖检查 | 通过 | `pip check` 无依赖冲突 |
| CLI 元数据提取 | 通过 | 本地 WAV 返回 ID 和格式列表 |
| 清单真实下载 | 通过 | 下载文件 16,044 字节，SHA-256 与源一致 |
| 下载归档 | 通过 | 删除临时下载文件后重跑，归档仍阻止重复下载 |
| Python API | 通过 | 配套脚本成功写出可解析摘要 JSON |
| Python 3.10 | 能运行但已弃用 | 本次运行收到升级到 3.11+ 的提示 |
| FFmpeg 合并、MP3 转码 | 未实测 | 本次 PATH 中没有 ffmpeg/ffprobe |
| 字幕、Cookie、播放列表和真实平台 | 未实测 | 命令依据官方文档；需要目标站点验收 |
| 断点续传 | 未实测 | 归档验证不等于断点续传验证 |
| 文件与参数校验 | 通过 | 2 个脚本语法、36 个 yt-dlp 长参数名、代码块配对通过；37 篇笔记 broken_links=0；参数名存在不等于真实站点验证 |
| Obsidian 阅读视图 | 未实测 | 交付进行文件级代码块与双链校验 |

测试音频 SHA-256：`56d4af65701c26df20bd4021eda95b6e830348ce3a746086079fe89285548dc9`。示例不携带外部歌曲、视频、Cookie 或私人信息；运行产物不提交到仓库。

## 16. 官方资料

- [项目首页与完整参数](https://github.com/yt-dlp/yt-dlp)
- [固定源码参考](https://github.com/yt-dlp/yt-dlp/tree/bbc809a1161d3bfca51fa36f59dda35556ee85a0)
- [安装文档](https://github.com/yt-dlp/yt-dlp/wiki/Installation)
- [发行文件](https://github.com/yt-dlp/yt-dlp/releases)
- [支持站点列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)
- [格式选择说明](https://github.com/yt-dlp/yt-dlp#format-selection)
- [输出模板](https://github.com/yt-dlp/yt-dlp#output-template)
- [Python 集成](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp)
- [EJS 与运行时](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [常见问题](https://github.com/yt-dlp/yt-dlp/wiki/FAQ)
- [FFmpeg 官方下载](https://ffmpeg.org/download.html)
