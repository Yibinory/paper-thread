# 文脉 · PaperThread

**把论文讲清楚，把知识连起来。**

文脉（PaperThread）是一套基于 Agent Skills 的论文精读与知识管理工具，包含一个本地阅读网站和两个协作的 skill。它希望让尚未读过原文、甚至刚接触这个领域的读者，也能顺着报告理解论文的问题、方法、推理和证据；遇到不熟悉的背景知识时，再沿链接进入详细教程。

论文报告围绕当前论文展开，通用知识则逐渐积累成可复用的知识库。阅读越多，已有知识就越能被后续报告复用。

> **仓库不附带个人阅读数据。** 首次启动看到空书架是正常现象。论文 PDF、报告、知识介绍、笔记、审计记录和导出文件均在使用过程中保存在本地，不随仓库发布。

## 目录

- [项目包含什么](#项目包含什么)
- [准备环境与下载项目](#准备环境与下载项目)
- [启动网站](#启动网站)
- [安装两个 skill](#安装两个-skill)
- [生成第一篇报告](#生成第一篇报告)
- [报告与知识介绍如何生成](#报告与知识介绍如何生成)
- [网站里的阅读方式](#网站里的阅读方式)
- [数据保存、备份与更新](#数据保存备份与更新)
- [命令行与开发](#命令行与开发)
- [常见问题](#常见问题)

## 项目包含什么

| 组成 | 负责什么 |
| --- | --- |
| 本地网站 | 浏览论文和知识，随文打开知识侧栏，搜索、记录笔记、标记阅读状态、打印报告 |
| `paper-reader` skill | 阅读论文及相关一手材料，重建整篇论证，编写可独立理解的报告，完成理解、覆盖与正确性审核 |
| `knowledge-curator` skill | 检索知识的原始工作和权威资料，编写从原理到应用的详细教程，补齐必要依赖，维护概念与别名 |
| 本地存储与命令行 | 保存内容、查询知识目录、校验链接、检查写入冲突、建立审阅包和导出阅读副本 |

**生成由调用 skill 的 Agent 完成。** 网站是阅读和管理界面，目前没有“点击生成论文报告”的按钮，也没有内置模型、模型下载或 API Key 配置。你需要一个能读取本地文件、执行命令并检索网络的 Agent；下文以 Codex 为例。

网站启动只需要 Python。生成时，Agent 会读取论文并访问需要核实的公开来源；这部分使用你自己的 Agent 环境与模型服务，数据处理方式由该环境决定。

## 准备环境与下载项目

### 必需环境

- **Python 3.10 或以上**，用于运行网站、命令行和 skill 安装脚本。
- 一个现代浏览器。
- 如需生成内容：支持本地 skills、文件操作、命令执行和联网检索的 Agent。

网站和核心工具使用 Python 标准库，**不需要先安装 Node.js、数据库服务或 Python 第三方依赖**。PDF 提取工具的依赖在后面的可选步骤安装。

Python 可从 [Python 官网](https://www.python.org/downloads/) 安装。Windows 安装时勾选 **Add Python to PATH**；安装后重新打开终端。

检查版本：

```powershell
# Windows：PowerShell 或命令提示符
py -3 --version
```

```bash
# macOS / Linux：终端
python3 --version
```

如果 Windows 上没有 `py`，但 `python --version` 返回 Python 3.10 或以上，下文的 `py -3` 均可替换为 `python`。

### 获取项目

使用 Git：

```bash
git clone https://github.com/Yibinory/paper-thread.git
cd paper-thread
```

也可以在 [仓库页面](https://github.com/Yibinory/paper-thread) 选择 **Code → Download ZIP**，将压缩包**完整解压**到一个可写文件夹。后续操作都在解压后的项目根目录进行，也就是包含 `paper.py`、`run.bat` 和 `README.md` 的目录。

## 启动网站

### Windows

双击根目录下的 **`run.bat`**。看到如下地址后，在浏览器打开：

[http://127.0.0.1:8765](http://127.0.0.1:8765)

也可以在项目目录打开 PowerShell：

```powershell
.\run.bat
```

脚本依次寻找项目虚拟环境 `.venv\Scripts\python.exe`、`py -3` 和 `python`。出现错误时会停留在窗口中，便于查看原因。

### macOS

在 Finder 中双击根目录下的 **`run.command`**，再打开同一个本地地址。也可以在终端运行：

```bash
sh run.command
```

如果双击时提示没有执行权限：

```bash
chmod +x run.command
./run.command
```

### Linux

在项目目录运行：

```bash
sh run.command
```

macOS / Linux 启动脚本优先使用 `.venv/bin/python`，没有虚拟环境则使用 `python3`。

### 通用启动方式与端口

不使用启动脚本也可以：

```powershell
# Windows
py -3 -X utf8 paper.py serve
```

```bash
# macOS / Linux
python3 paper.py serve
```

默认端口是 `8765`。如果已被其他程序占用，换一个端口：

```powershell
# Windows
.\run.bat --port 8766
```

```bash
# macOS / Linux
sh run.command --port 8766
```

此时打开 [http://127.0.0.1:8766](http://127.0.0.1:8766)。服务只监听本机 `127.0.0.1`，不是公网网站。运行期间保留终端窗口，按 **Ctrl+C** 停止；停止服务不会删除内容。

正常使用请通过这个地址访问，**不要直接双击 `web/index.html`**。首次运行会自动创建空的数据目录。

## 安装两个 skill

两个 skill 的源文件分别位于：

- [`skills/paper-reader/SKILL.md`](skills/paper-reader/SKILL.md)
- [`skills/knowledge-curator/SKILL.md`](skills/knowledge-curator/SKILL.md)

它们会相互引用，**请一起安装**，并保留各自的 `references/` 和 `agents/` 子目录。

### 方式一：安装到当前项目（推荐）

在项目根目录执行一次：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py
```

```bash
# macOS / Linux
python3 scripts/install_skills.py
```

脚本会将两个 skill 完整复制到：

```text
paper-thread/
└── .agents/
    └── skills/
        ├── paper-reader/
        │   ├── SKILL.md
        │   ├── references/
        │   └── agents/
        └── knowledge-curator/
            ├── SKILL.md
            ├── references/
            └── agents/
```

这种安装方式不需要符号链接，也不需要 Windows 管理员权限。已存在且内容一致时可以重复运行；内容不一致时默认停止，避免覆盖你的修改。

然后：

1. 在 Codex 中打开 **`paper-thread` 项目文件夹**，让 Agent 可以读取和修改这个项目。
2. 在该项目中开始会话，查看可用 skills。CLI / IDE 可通过 `/skills` 或输入 `$` 查找；桌面端也可从 skill 选择入口查找。
3. 确认可以找到 `paper-reader` 和 `knowledge-curator`。若没有出现，重新打开会话或重启 Codex。

Codex 的项目级 skill 发现目录是 `.agents/skills`，用户级目录是 `~/.agents/skills`。这些发现与调用方式可参照 [OpenAI 官方 skill 文档](https://learn.chatgpt.com/docs/build-skills)。

### 方式二：安装到用户目录（可选）

如果希望在其他工作区中也能找到这两个 skill：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py --user
```

```bash
# macOS / Linux
python3 scripts/install_skills.py --user
```

安装目标是用户主目录下的 `.agents/skills`，例如 Windows 的 `%USERPROFILE%\.agents\skills`，或 macOS / Linux 的 `~/.agents/skills`。

**只需选择一种安装范围。** 同时安装到项目和用户目录，可能会在选择器中出现同名的两个 skill。用户级安装只复制工作流说明，**不会复制网站程序或知识库**；调用时仍需要让 Agent 打开 PaperThread 项目，或明确告诉它项目所在路径。

### 更新或手动安装

拉取仓库更新后，更新项目内已安装的副本：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py --update
```

```bash
# macOS / Linux
python3 scripts/install_skills.py --update
```

用户级安装则追加 `--user --update`。被替换的副本会保存在对应 `.agents/paperthread-skill-backups/` 下，脚本会打印备份位置。若你修改过 skill，可以先比对备份，再决定是否合并。

也可以手动将 `skills/` 内的两个完整目录复制到目标 `.agents/skills/`。其他 Agent 如支持 `SKILL.md`，可以使用其自己的安装目录；目录发现、调用语法和工具权限以对应客户端为准。本仓库的安装脚本按 Codex 的目录约定配置。

## 生成第一篇报告

### 1. 放入论文

将 PDF 放进项目根目录下的 **`test_paper/`**。如果尚未启动过网站，手动新建这个文件夹即可。

```text
paper-thread/
└── test_paper/
    └── example.pdf
```

这里使用 `example.pdf` 作为文件名示例，仓库不提供这篇论文。文件名可以包含中文和空格，在终端命令中引用时加引号。

### 2. 可选：安装本地 PDF 提取工具

如果 Agent 自己已有可用的 PDF 读取能力，可以使用它。使用仓库的 `scripts/extract_pdf.py` 时，需要安装 `requirements.txt` 中的 `pypdf` 和 `pdfplumber`。

Windows：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/extract_pdf.py "test_paper/example.pdf" --out ".local/extracted/example" --render 1 2
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/extract_pdf.py "test_paper/example.pdf" --out ".local/extracted/example" --render 1 2
```

`--render 1 2` 表示额外渲染第 1、2 页，不需要图片时可以省略。提取文本不能替代对公式、图表和版面的检查。以上命令直接使用虚拟环境解释器，不要求先激活环境。

### 3. 在 Agent 会话中调用 skill

把下面这段发给已经打开本项目的 Agent，**不是粘贴到系统终端**：

```text
请使用 $paper-reader 阅读 test_paper/example.pdf，生成一份中文论文报告。
面向没有读过这篇论文、也可能第一次接触该领域的读者。
按需复用知识库；缺少的知识请使用 $knowledge-curator 检索、编写并审核。
完成整篇论证组织、读者理解、原文覆盖和正确性检查后，发布到当前论文库。
```

也可以请求处理多篇论文：

```text
请使用 $paper-reader 依次阅读 test_paper 中的所有 PDF。
为每篇论文生成报告，复用已有知识，按需补充知识教程。
同一论文只保留一个当前报告入口，完成审核后再发布。
```

知识教程也可以独立生成或完善：

```text
请使用 $knowledge-curator 介绍最优传输。
先检查知识库中是否已有对应概念，再检索原始工作与权威教材，
详细讲清问题、原理、推导、完整应用示例、适用条件及有用的变体。
遇到需要单独展开的基础知识，请按需补齐并审核，再提供链接。
```

### 4. 在网站中阅读

Agent 完成保存、校验与构建后，启动网站或刷新已打开的页面，就能看到报告和知识页。网页不要求在生成时一直运行，Agent 可以直接调用本地命令行工具。

每篇论文只有一份当前报告。重新生成时沿用原来的文档 ID 和阅读链接，不建立版本对比页；已有笔记与阅读状态单独保存。

## 报告与知识介绍如何生成

### 论文报告：让整篇解释成立

报告先还原研究的具体困难、已有路线为什么不足、作者选择这条路线的理由，再建立完整的方法图景，解释关键细节和证据。章节顺序由这条推理和读者需要的前提决定，不要求每篇论文套用固定目录。

论文的贡献、特定符号、设计动机和关键推导保留在报告里。通用背景在实际使用处提供知识链接；链接前仍解释它在当前步骤中的作用，避免把论文自身的推理也移出正文。

生成过程中分开进行三类审核：

- **读者理解与整体组织**：只凭报告及可达知识，检查能否重建整篇解释，指出理解断点及章节之间缺失的推理。
- **原文覆盖**：对照正文、图表及可取得的附录，记录哪些内容已解释、简述、链接、主动省略或尚未核实。
- **主张、公式与结论的正确性**：逐项检查前提、推导、数值与证据范围；已确认的论文错误在正文相关位置说明，未核实事项保留明确边界。

独立读者审核需要独立上下文及相应授权。同一会话中的自查会按实际方式标注，不能称为独立盲读。自动格式检查通过也不意味着论文已经被科学地证实。

### 知识介绍：可反复引用的详细教程

知识教程从提出或奠定该知识的原始工作、权威教材和后续发展出发，解释直觉、数学对象、推导、完整算例、实际应用、条件与变体。当前论文只是触发知识需求的场景。

教程中的必要基础会按需迭代补齐。例如解释 A 需要 B，而 B 又需要 C，就分别检查是否已有合适教程，补充缺口并审核，然后逐层返回检查是否讲通。简单定义仍放在当前页，不为每个术语新建页面。

知识页直接教授核实和纠正后的内容；原始错误、修正依据与复算过程留在审计记录中。无法确认的核心内容需要继续查证，不能把未解决的错误当成教学内容。

### 如何识别同一知识

概念身份由调用 skill 的 Agent 根据定义、适用条件、粒度和当前用法判断。它先阅读精简知识目录，再核对候选页面，决定复用、完善、添加别名或新建。名称搜索只提供候选，搜索不到不能证明知识不存在。

本项目不下载本地语义模型，也不靠精确字符串匹配自动判定同义词。具体规范见两个 [`skills/`](skills/) 目录及 [内容格式说明](CONTENT_SCHEMA.md)。

## 网站里的阅读方式

- **论文 / 知识**：分别浏览报告和知识教程，可按领域及文字筛选。
- **随文知识侧栏**：点击正文中的知识链接，在侧栏阅读，继续保留原文位置；遇到嵌套知识可继续打开并返回。
- **搜索**：搜索名称、别名、关键词；快捷键为 macOS 的 `⌘ K` 或 Windows / Linux 的 `Ctrl+K`。
- **笔记与标记**：正文底部记录想法；阅读状态由你主动标记，不会因为打开页面就认定已经掌握。
- **阅读呈现**：支持明暗主题、章节目录、公式、表格、来源链接和打印；层级颜色帮助区分内容。
- **必要的交互**：仅在操作有助于理解关系或计算过程时使用。没有交互也可以是一份完整报告。

## 数据保存、备份与更新

### 文件保存在哪里

| 路径 | 内容 | 提交到 GitHub？ |
| --- | --- | --- |
| `data/reports/` | 当前论文报告 | 否 |
| `data/concepts/` | 当前知识教程 | 否 |
| `data/figures/` | 本地配图 | 否 |
| `data/reviews/` | 来源、覆盖、正确性和理解审核记录 | 否 |
| `data/revisions/` | 内部内容快照、引用依据 | 否 |
| `test_paper/` | 原始论文 PDF | 否 |
| `.local/reader.sqlite3` | 笔记与阅读状态 | 否 |
| `.local/` 其余内容 | 草稿、提取文本、审阅包、缓存等 | 否 |
| `web/bundle.js` | 构建得到的阅读数据，包含笔记 | 否 |
| `output/` | 导出包、截图等 | 否 |
| `.agents/` | 本机安装的 skills 及备份 | 否 |
| `skills/`、`web/` 其余代码、Python 程序与文档 | 项目程序和工作流 | 是 |

这些本地目录已经写入 `.gitignore`。不要用 `git add -f` 强行加入个人内容；忽略规则也不能移除曾经被你主动提交的文件。

网站只展示每篇论文的当前报告。内部快照用于保存引用依据和检测更新冲突，不是多版报告入口。报告可以保留它引用时的知识版本，更新某个知识页不会悄悄改写旧报告的解释依据；知识库入口展示当前知识。

### 备份与换电脑

1. 停止本地服务，避免复制过程中笔记仍被写入。
2. 备份 `data/`、`test_paper/` 和 `.local/`。如只要已发布内容与笔记，至少保留前两个目录和 `.local/reader.sqlite3`。
3. 在新电脑下载项目，将这些目录放回相同位置，再启动网站。
4. `.venv/` 不必复制，按新电脑系统重新建立。需要继续用 Agent 时，也重新运行 skill 安装脚本。

“阅读笔记”页面还可单独导出和导入笔记 JSON。导入时保留已有笔记，不覆盖现有记录；它不能代替报告、知识和 PDF 的完整备份。主题等界面偏好保存在浏览器中。

### 导出便携阅读副本（可选）

```powershell
# Windows
py -3 -X utf8 paper.py export
```

```bash
# macOS / Linux
python3 paper.py export
```

默认输出 `output/offline-reader/index.html` 和 `output/offline-reader.zip`。完整解压后可直接打开其中的 `index.html` 阅读。

**导出包会包含当前报告、知识、笔记、图像及 `test_paper/` 下的 PDF**，分享前应检查内容；它不属于 GitHub 发布文件。副本中新写的笔记保存在当前浏览器，不会自动回写到原服务，可通过笔记导出 / 导入迁移。便携副本用于阅读，不用于执行联网生成流程。

### 更新程序

使用 Git 下载的项目可以在停止服务后执行：

```bash
git pull --ff-only
```

然后按前面的说明运行 `scripts/install_skills.py --update`，并重新启动网站。代码更新与本地阅读数据分开；有自行修改的代码或 skill 时，先保留自己的修改再合并。使用 ZIP 时，建议下载到新目录，按备份说明迁移个人数据。

## 命令行与开发

### 常用命令

下面以 `python3` 为例。Windows 可替换为 `py -3 -X utf8`，或直接使用 `.venv\Scripts\python.exe`。

```bash
# 显示完整命令列表
python3 paper.py --help

# 查看论文目录与知识摘要目录
python3 paper.py inventory --kind report
python3 paper.py inventory --kind concept

# 名称和关键词搜索；概念身份仍需阅读正文判断
python3 paper.py search "最优传输" --kind concept

# 校验当前内容与引用，构建阅读数据
python3 paper.py check
python3 paper.py build
```

Agent 编写内容时还会使用：

| 命令 | 用途 |
| --- | --- |
| `get ID` | 读取文档及当前 revision |
| `save FILE` | 保存新文档 |
| `save FILE --expected-revision REV` | 更新文档，防止覆盖已变化的内容 |
| `review-pack ID --draft FILE --to DIR` | 导出只含草稿、可达知识及配图的理解审核包 |
| `alias ID NAME --expected-revision REV` | 为已确认的同一概念添加别名 |
| `merge SOURCE TARGET --expected-source REV1 --expected-target REV2` | 内容与身份核对后合并重复概念 |
| `export --to DIR` | 导出便携阅读副本 |

`ID`、`FILE` 和 `REV` 是占位符，需使用真实文档标识、文件路径和工具返回的版本值。通常由 Agent 按 skill 调用，无需手工编写 JSON。

`build` 会校验内容并固定新增知识引用。`pin --refresh` 会更新引用，应先检查相关知识变化，不需要在每次启动或构建时执行。

### 仓库结构

```text
paper-thread/
├── README.md                 使用与安装说明
├── CONTENT_SCHEMA.md         报告、知识、来源和交互的数据约定
├── run.bat                   Windows 启动入口
├── run.command               macOS / Linux 启动入口
├── paper.py                  命令行与本地 HTTP 服务
├── library.py                文档存储、引用、搜索与笔记
├── interactions.py           交互配置校验
├── skills/
│   ├── paper-reader/         论文阅读与审核工作流
│   └── knowledge-curator/    知识教程与审核工作流
├── scripts/
│   ├── start.py              两个平台入口共用的启动逻辑
│   ├── install_skills.py     复制、更新及备份 skills
│   ├── extract_pdf.py        PDF 文本提取与页面渲染
│   └── check_math.cjs        公式语法检查
├── web/                      网页、样式、交互及 KaTeX
├── tests/                    存储、安装、启动与交互测试
└── .github/workflows/        多系统自动测试
```

`data/`、`test_paper/`、`.local/` 等个人目录在首次运行时创建，不存在于仓库中。

### 验证

Python 测试无需安装额外依赖：

```bash
python3 -m unittest discover -s tests -v
python3 paper.py check
```

如已安装 Node.js，还可检查公式语法和交互计算，无需 `npm install`：

```bash
node scripts/check_math.cjs
node tests/test_interactions.cjs
```

GitHub Actions 配置了 Windows、macOS 和 Linux 的测试，包括不携带任何本地数据的启动流程、中文与空格路径、skill 安装和空库导出。自动测试检查程序行为；公式解析检查语法，不替代推导、原文核查或读者审核。

## 常见问题

**启动后没有任何报告，是不是安装失败？**

不是。公开仓库不带个人内容。先安装 skills，再让 Agent 阅读放入 `test_paper/` 的论文；完成发布后刷新页面。

**出现“Python 未找到”，或者双击 Windows 脚本报错？**

先在新终端执行 `py -3 --version` 或 `python --version`。安装 Python 3.10+ 并启用 PATH；如果 `.venv/` 来自另一台电脑或另一种系统，重新创建虚拟环境。不要在 ZIP 压缩包内部直接运行。

**出现 `Address already in use` 或端口占用错误？**

可能已经运行了一个网站实例。可以继续打开它的本地地址，或关闭对应窗口；也可以使用 `--port 8766`，并在浏览器访问新端口。

**安装后 Agent 找不到 skill？**

确认它打开的是项目根目录，且 `.agents/skills/两个技能名称/SKILL.md` 实际存在。尝试新会话或重启客户端。也可以直接告诉 Agent 读取项目中 `skills/paper-reader/SKILL.md`，并按其中流程执行；只是复制 `SKILL.md` 而遗漏引用文件并不构成完整安装。

**安装脚本提示已有不同内容？**

这是为了保留现有修改。确认要更新后加 `--update`；脚本会备份再替换，打印备份位置。日常修改应优先编辑 `skills/` 中的源文件，再更新安装副本。

**为什么报告生成需要网络，网站却可以本地运行？**

这是两个阶段。Agent 需要检索论文相关材料和知识的可靠来源；本地网站负责阅读已经保存的结果。知识引用的来源页面仍可能需要联网打开。

**能否在网站直接上传 PDF 并自动生成？**

当前没有这个流程。请将 PDF 放入 `test_paper/`，通过 Agent 调用 skill；网站用于阅读和管理生成结果。

**如何改进一份读不懂的报告？**

把具体理解断点反馈给 Agent，让它先诊断并修改对应 skill，再从论文和来源重新组织报告、完成审核并更新同一文档。只替换几个句子无法验证工作流是否真正改善。

## 参考与第三方资源

- 写作设计参考 [paper-xray](https://github.com/Wang-auspicious/paper-xray)。
- 公式渲染使用本地分发的 KaTeX 0.16.22，许可证见 [`web/vendor/katex/LICENSE`](web/vendor/katex/LICENSE)。
- PDF、报告和知识教程由使用者在本地准备或生成，来源应记录在各自内容中；本仓库不分发这些阅读材料。
