# 文脉 · PaperThread

**把论文讲清楚，把知识连起来。**

文脉是一套由 **本地阅读网站 + 两个 Agent Skills** 组成的论文精读工具。把论文链接或 PDF 交给 Agent，它会阅读原文、查找相关资料，生成中文 HTML 报告，并把需要展开的背景知识整理成可复用的教程。

它的目标是让尚未读过原文、甚至刚接触这个领域的人，也能理解论文为什么提出这个问题、方法怎样工作，以及证据支持什么结论。熟悉的知识可以跳过，不熟悉的知识在用到时点击展开。

> 仓库不附带论文、报告或个人知识库，首次启动看到空书架是正常现象。生成的内容和阅读笔记保存在本地。

## 你能读到什么

- **连贯的论文讲解**：从具体困难引出方法选择，再解释完整机制、实验和结论，而不是把论文压缩成几个摘要段落。
- **能跟着算的例子**：关键公式交代符号与含义，用小例子展示中间计算、更新过程及结果如何被使用。
- **有依据的分析**：区分【文中有据】【推断】【猜测】，分析设计取舍、可能的失效和诊断办法；不把推测写成作者的真实经历。
- **必要的交互与清晰的颜色**：适合时用可操作的图形展示参数、过程和结果的关系；简单内容仍用文字、表格或静态图说明。
- **随文知识教程**：知识介绍从可靠的原始工作与教材出发，详细解释原理、推导、应用和变体；必要的基础还可以继续沿链接展开。
- **对原文的核查**：检查论文的主张、公式、数值和结论，明确指出有证据的错误，以及尚无法确认的部分。

论文报告会经过整体组织、读者理解、原文覆盖与正确性检查；知识教程也有单独的审核流程。来源标记不代表正确性保证，阅读核查也不能替代完整实验复现，报告会说明实际检查范围。

## 开始使用

整个流程是：**下载项目 → 安装 skills → 让 Agent 阅读论文 → 在网站查看结果**。

### 1. 准备环境与下载项目

需要：

- **Python 3.10 或以上**，用于启动网站和安装 skills。
- 一个现代浏览器。
- 一个支持本地 skills、文件操作、命令执行和联网检索的 Agent。下面以 Codex 为例。

网站本身不需要安装 Node.js、数据库或本地模型。报告由你使用的 Agent 生成，网站负责阅读和管理，目前没有网页上传生成按钮，也不在网站里配置模型 API Key。

Python 可从 [官网](https://www.python.org/downloads/) 安装。Windows 安装时勾选 **Add Python to PATH**，然后重新打开终端检查：

```powershell
# Windows
py -3 --version
```

```bash
# macOS / Linux
python3 --version
```

如果 Windows 没有 `py`，但 `python --version` 返回 3.10 或以上，可以把下文的 `py -3` 替换为 `python`。

使用 Git 下载项目：

```bash
git clone https://github.com/Yibinory/paper-thread.git
cd paper-thread
```

也可以在 [仓库页面](https://github.com/Yibinory/paper-thread) 选择 **Code → Download ZIP**，完整解压到一个可写文件夹。下文的“项目目录”指包含 `paper.py`、`run.bat` 和 `README.md` 的文件夹；命令都从这里执行。

### 2. 安装两个 skills

| Skill | 用途 |
| --- | --- |
| `paper-reader` | 阅读论文、查证相关材料，生成并审核论文报告 |
| `knowledge-curator` | 查找可靠来源，生成、补充和复用详细知识教程 |

**两个一起安装。** 在项目目录执行：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py
```

```bash
# macOS / Linux
python3 scripts/install_skills.py
```

脚本会安装到当前项目的 `.agents/skills/`，不需要管理员权限。然后在 Codex 中打开这个项目文件夹，新建会话并确认可以选择 `paper-reader` 和 `knowledge-curator`。如果没有出现，重新打开会话或重启客户端。

<details>
<summary>希望在其他工作区调用，或使用其他 Agent？</summary>

安装时追加 `--user`，例如：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py --user
```

```bash
# macOS / Linux
python3 scripts/install_skills.py --user
```

这会安装到用户目录的 `.agents/skills/`。项目级和用户级选择一种即可，避免出现同名副本。用户级安装不会复制网站或知识库；调用时仍需告诉 Agent 文脉项目的实际路径，并允许它访问。

其他支持 `SKILL.md` 的 Agent，可以按客户端要求，将 `skills/` 中的两个完整文件夹复制到对应位置，保留其中所有文件。具体发现和调用方式以客户端为准。

</details>

### 3. 把论文交给 Agent

**直接提供论文地址即可，不需要提前下载 PDF、创建目录，或把文件放进 `test_paper/`。** 支持论文网页、arXiv / DOI 链接、PDF 直链，以及 Agent 能读取的本地 PDF 或附件。

将下面这段发给 Agent，替换其中的链接；这不是终端命令：

```text
请使用 $paper-reader 阅读这篇论文：<论文链接>。
生成一份面向未读过原文读者的中文报告，按需使用 $knowledge-curator 补充背景知识。
请自行获取和整理原文，完成审核后保存到文脉阅读库。
```

本地文件或多篇论文也可以直接交给它：

```text
请使用 $paper-reader 阅读这个 PDF：<文件的完整路径>。
```

```text
请使用 $paper-reader 依次阅读以下论文，为每篇生成报告，并复用已有知识：
<论文链接一>
<论文链接二>
```

Agent 会核对论文与版本，自动整理原文副本和所需目录；本地原文件不会被移动。遇到确实无法访问的全文，会说明缺少什么材料。每篇论文只保留一个当前报告入口，后续重新生成会更新同一篇报告。

生成时需要联网查证论文和知识来源，使用的是你的 Agent 环境与模型服务；其数据处理方式由该环境决定。网站不必在生成期间一直运行。

### 4. 启动网站，查看报告

| 系统 | 启动方式 |
| --- | --- |
| Windows | 双击 `run.bat`，或在 PowerShell 执行 `.\run.bat` |
| macOS | 双击 `run.command`，或在终端执行 `sh run.command` |
| Linux | 在终端执行 `sh run.command` |

启动后，在浏览器打开 **[http://127.0.0.1:8765](http://127.0.0.1:8765)**。运行期间保留终端窗口；按 **Ctrl+C** 停止，已有内容不会删除。

如果网站已打开，在 Agent 完成后刷新页面即可。也可以先启动网站再生成，空书架会在生成完成后出现内容。请通过本地地址访问，**不要直接双击项目里的 `web/index.html`**。

网站只监听本机，不会自动发布到公网。

## 阅读与继续积累知识

- **随文展开知识**：点击正文知识链接，在侧栏阅读并保留论文位置；可以继续打开嵌套知识，再逐层返回。
- **独立浏览教程**：在“知识”页面查看积累的教程。Agent 会按概念含义判断是否复用，不要求中英文名称或叫法完全一致。
- **查找内容**：使用搜索框，或按 macOS 的 `⌘ K`、Windows / Linux 的 `Ctrl+K` 搜索名称、别名及关键词。
- **记录阅读**：在正文底部记笔记，主动标记阅读或掌握状态；打开页面不会自动表示“已经学会”。
- **调整阅读方式**：使用章节目录、明暗主题、来源链接，以及“打印 / 保存 PDF”。

也可以单独让 Agent 生成知识教程：

```text
请使用 $knowledge-curator 讲解最优传输。
先检查是否已有对应知识，再查找原始工作与权威教材，
详细解释原理、推导、完整应用示例、适用条件和有用的变体。
需要单独展开的基础知识，请补齐后提供链接。
```

如果报告有跳步或解释不清，可以直接反馈位置和疑问。例如：“第二节还没说明为什么需要增强，就开始讲操作库了。”让 Agent 先检查相应 skill，再按改进后的流程重新生成报告，避免只润色原句。

## 更新、备份与分享

### 更新程序和 skills

先停止网站。使用 Git 下载的项目执行：

```bash
git pull --ff-only
```

然后更新安装的 skills：

```powershell
# Windows
py -3 -X utf8 scripts/install_skills.py --update
```

```bash
# macOS / Linux
python3 scripts/install_skills.py --update
```

如果之前使用了用户级安装，这次也追加 `--user`。脚本会先备份被替换的 skill，并显示备份位置。完成后重新启动网站，刷新浏览器，并在 Agent 中开启新会话。

代码更新不会清空本地阅读库。自己修改过代码或 skill 时，先保留这些修改再合并。使用 ZIP 下载的用户，建议把新版解压到新目录，再按下面的方式迁移数据。

### 备份与换电脑

1. 停止网站。
2. 备份项目中的 **`data/` 和 `.local/` 两个完整文件夹**，它们包含论文、报告、知识、笔记及相关记录。如果沿用了旧阅读库的 `test_paper/`，也一并备份。
3. 在新电脑下载项目，把备份目录放回项目根目录，再启动网站。
4. 若要继续生成内容，重新安装 skills；虚拟环境 `.venv/` 无需跨电脑复制。

“阅读笔记”页面还支持单独导出和导入笔记。它不能替代论文和知识库的完整备份。

这些个人数据已被 Git 忽略，不随正常代码提交上传到 GitHub。不要强制添加个人数据；忽略规则不能移除曾经主动提交过的文件。

### 导出便携阅读副本

在项目目录运行：

```powershell
# Windows
py -3 -X utf8 paper.py export
```

```bash
# macOS / Linux
python3 paper.py export
```

生成的 `output/offline-reader.zip` 完整解压后，打开其中的 `index.html` 即可阅读。

**导出包包含当前报告、知识、笔记、配图和本地归档的 PDF**，分享前请检查内容。副本里新写的笔记不会自动同步回原网站，可以通过笔记导出 / 导入迁移。

## 常见问题

**启动后书架是空的？**

公开仓库不带个人内容。安装 skills 后，把论文链接交给 Agent；它完成生成后刷新网站即可。

**提示 Python 未找到或版本太低？**

安装 Python 3.10+，Windows 勾选 PATH 选项，再重新打开终端。不要在 ZIP 压缩包内部直接运行。若项目中留有另一台电脑的 `.venv/`，请重新建立虚拟环境。

**macOS 双击 `run.command` 提示没有执行权限？**

可直接在项目目录运行 `sh run.command`。需要双击运行时，先执行 `chmod +x run.command`。

**提示端口被占用？**

检查是否已经启动了一个网站窗口。也可以换端口：Windows 用 `.\run.bat --port 8766`，macOS / Linux 用 `sh run.command --port 8766`，然后访问 [http://127.0.0.1:8766](http://127.0.0.1:8766)。

**安装后 Agent 找不到 skill？**

确认 Agent 打开的是项目文件夹，并已运行安装脚本，再尝试新会话或重启客户端。也可以明确让它读取 `skills/paper-reader/SKILL.md` 并执行其中流程。手动安装时须复制完整文件夹，不能只复制一个 `SKILL.md`。

**安装脚本提示已有不同内容？**

这表示已有副本与新版不同。需要更新时使用 `--update`，脚本会先备份再替换。若自行修改过 skill，可根据打印的备份路径找回原副本。

**Agent 提示缺少 PDF 读取依赖？**

如果 Agent 自带 PDF 读取能力，可以直接使用。需要使用项目提供的提取工具时，在项目目录安装可选依赖：

```powershell
# Windows
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

随后让 Agent 使用该虚拟环境。仅启动网站和阅读已有内容不需要这些依赖。

## 参考与致谢

报告中的研究推理、可手算讲解、证据标注和交互设计参考了 [Paper X-Ray](https://github.com/Wang-auspicious/paper-xray)，并结合文脉的知识库、整篇连贯性和错误核查要求进行调整。

公式渲染使用 [KaTeX](https://katex.org/)，许可证见 [`web/vendor/katex/LICENSE`](web/vendor/katex/LICENSE)。论文及教程的资料来源记录在各自阅读页面中。
