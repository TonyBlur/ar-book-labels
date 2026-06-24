# ar-book-labels

**[English](README.md)** | 简体中文

从 Excel 表格自动生成可打印的 [Accelerated Reader](https://www.renaissance.com/accelerated-reader/) 书籍标签。标签包含书名、作者、AR 等级（标准颜色编码）、积分和测验编号，适用于打印后贴在书本上。

## 目录

- [功能特点](#功能特点)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令行用法](#命令行用法)
  - [选项](#选项)
  - [示例](#示例)
- [标签尺寸预设](#标签尺寸预设)
- [配置文件](#配置文件)
- [Excel 格式要求](#excel-格式要求)
- [AR 等级颜色对照表](#ar-等级颜色对照表)
- [自定义颜色方案](#自定义颜色方案)
- [开发指南](#开发指南)
- [许可证](#许可证)

## 功能特点

- **灵活标签尺寸**：4 种内置预设（50x30、70x37、63x38、99x38）或通过 `--label-size` 自定义尺寸
- **自动网格布局**：根据标签尺寸自动计算列数、行数和居中位置
- **可调间距**：列间距（`--col-gap`）、行间距（`--row-gap`）、页边距（`--margin`）
- **AR 标准颜色编码**：12 个颜色区间，从黄色（0.1–1.5）到棕色（6.6+）
- **自定义颜色方案**：通过 `--colors` 覆盖 AR 颜色
- **黑白模式**：`--bw` 节省墨水
- **裁剪边框**：`--with-border` 添加细实线边框，便于手动裁剪
- **排版控制**：自定义字体（`--font`）和圆角半径（`--radius`）
- **YAML/JSON 配置**：通过 `--config` 使用可复用的配置文件
- **智能文本截断**：书名支持 2 行换行 + 省略号；作者名单行显示
- **作者优先布局**：作者名在书名上方，方便按作者排序整理书籍
- **打印就绪 HTML**：内置 `@page` CSS 可直接打印；`--scale` 控制屏幕预览
- **内置模板**：附带参考 Excel 模板，包含示例数据和字段说明

## 安装

```bash
pip install ar-book-labels
```

如需 YAML 配置文件支持：

```bash
pip install ar-book-labels[yaml]
```

或从源码安装：

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
pip install -e .
```

## 快速开始

1. **获取模板**（如果还没有 Excel 文件）：

```bash
ar-book-labels --template
```

这会将 `ar_template.xlsx` 复制到当前目录，填入你的书籍数据即可。

2. **生成标签**：

```bash
ar-book-labels books.xlsx -o labels.html
```

3. **打开** `labels.html` 在浏览器中预览，然后打印（Ctrl/Cmd+P）。

   > **打印提示**：在浏览器打印对话框中，选择**"实际尺寸"**（或页边距选择**"无"**/**"默认"**），避免浏览器自动添加页边距导致标签位置偏移。HTML 已声明 `@page { margin: 0 }`，浏览器在此基础上再加页边距会导致错位。

## 命令行用法

```
ar-book-labels <excel文件> [选项]
```

### 选项

#### 输入与输出

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `excel` | — | Excel 文件路径（.xlsx） |
| `-o, --output` | `AR_Book_Labels.html` | 输出 HTML 文件路径 |
| `-s, --sheet` | 第一个工作表 | 要读取的工作表名称（默认第一个） |
| `--start-row` | `2` | 数据开始的行号（1 = 表头行） |
| `--template` | — | 将参考 Excel 模板复制到当前目录并退出 |
| `-V, --version` | — | 显示版本号并退出 |

#### 列映射

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--col-title` | `AR Title` | Excel 中书名对应的列名 |
| `--col-author` | `AR Author` | Excel 中作者对应的列名 |
| `--col-level` | `Book Level` | Excel 中等级对应的列名 |
| `--col-points` | `AR Points` | Excel 中积分对应的列名 |
| `--col-quiz` | `Quiz Number` | Excel 中测验编号对应的列名 |

#### 布局

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--label-size` | `50x30` | 标签尺寸：预设名（`50x30`、`70x37`、`63x38`、`99x38`）或 `宽x高`（mm） |
| `--col-gap` | `2` | 列间距（mm） |
| `--row-gap` | `0` | 行间距（mm） |
| `--margin` | `13.5` | 页边距（mm，四边统一） |
| `--radius` | `4` | 标签圆角半径（mm） |

#### 外观

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--scale` | `1` | 屏幕预览的缩放倍数 |
| `--bw` | — | 黑白模式：白色圆圈+细黑描边，等级数字黑色 |
| `--with-border` | — | 为每个标签添加细边框（打印可见），便于手动裁剪 |
| `--font` | Segoe UI, system-ui, ... | 标签文字的字体族 |
| `--colors` | AR 标准 12 段 | 自定义颜色方案（见[自定义颜色方案](#自定义颜色方案)） |

#### 配置

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--config` | — | YAML 或 JSON 配置文件路径 |

### 示例

```bash
# 基本用法（默认 50x30mm 标签）
ar-book-labels my_books.xlsx

# 自定义输出路径和工作表名
ar-book-labels my_books.xlsx -o output/labels.html -s "图书数据"

# 更大的标签（70x37mm，每页 21 个）
ar-book-labels my_books.xlsx --label-size 70x37

# Avery 5160 兼容标签
ar-book-labels my_books.xlsx --label-size 63x38

# 自定义尺寸 + 更宽间距
ar-book-labels my_books.xlsx --label-size 60x40 --col-gap 3 --row-gap 2

# 更紧的页边距（10mm）
ar-book-labels my_books.xlsx --margin 10

# 自定义字体（如中文书名）
ar-book-labels my_books.xlsx --font "Noto Sans SC, sans-serif"

# 直角标签
ar-book-labels my_books.xlsx --radius 0

# 自定义颜色方案
ar-book-labels my_books.xlsx --colors "0.1-2.0:#FFD700,2.1-4.0:#2E8B57,4.1-6.0:#DC143C,6.1-99:#8B4513"

# 黑白模式 + 边框
ar-book-labels my_books.xlsx --bw --with-border

# 使用配置文件
ar-book-labels my_books.xlsx --config ar-book-labels.yaml

# 复制参考模板
ar-book-labels --template
```

## 标签尺寸预设

| 预设 | 尺寸 | 每页标签数 | 网格 | 说明 |
|------|------|-----------|------|------|
| `50x30` | 50mm × 30mm | 36 | 4 × 9 | 默认。紧凑标签。 |
| `70x37` | 70mm × 37mm | 21 | 3 × 7 | 中等标签，长书名有更多空间。 |
| `63x38` | 63mm × 38.1mm | 21 | 3 × 7 | Avery 5160/8160 兼容。 |
| `99x38` | 99mm × 38mm | 14 | 2 × 7 | 超大标签。 |

也支持自定义尺寸：`--label-size 宽x高`（单位 mm）。

使用自定义或预设尺寸时，网格（列数、行数）自动计算，标签在页面上水平居中。

## 配置文件

如需复用设置，可创建 YAML 或 JSON 配置文件：

```yaml
# ar-book-labels.yaml
label_size: "50x30"
col_gap: 2
row_gap: 0
margin: 13.5
font: "'Segoe UI', system-ui, sans-serif"
radius: 4
bw: false
with_border: false
# colors: "0.1-1.5:#FFD700,1.6-2.0:#2E8B57,..."
```

```bash
ar-book-labels my_books.xlsx --config ar-book-labels.yaml
```

**优先级**：CLI 参数 > 配置文件 > 默认值。

示例配置文件：[`ar_labels_config.example.yaml`](ar_labels_config.example.yaml)。

YAML 支持需要可选依赖 `pyyaml`：

```bash
pip install ar-book-labels[yaml]
```

JSON 配置文件无需额外依赖即可使用。

## Excel 格式要求

表格必须包含以下列（默认列名如下；可通过 `--col-*` 选项自定义列名映射）：

| 内部字段 | 默认列名 | 类型 | 说明 |
|----------|----------|------|------|
| `title` | `AR Title` | 文本 | 书名 |
| `author` | `AR Author` | 文本 | 作者名 |
| `level` | `Book Level` | 数字 | AR ATOS 等级（如 5.1） |
| `points` | `AR Points` | 数字 | 积分值 |
| `quiz` | `Quiz Number` | 数字/文本 | 测验编号 |

缺少必填字段的行将被跳过，并在终端输出警告信息。

使用 `ar-book-labels --template` 获取预格式化的模板。

## AR 等级颜色对照表

| 等级范围 | 颜色 | 色值 |
|----------|------|------|
| 0.1 – 1.5 | 黄色 | `#FFD700` |
| 1.6 – 2.0 | 绿色 | `#2E8B57` |
| 2.1 – 2.5 | 深蓝色 | `#00008B` |
| 2.6 – 3.0 | 红色 | `#DC143C` |
| 3.1 – 3.5 | 粉色 | `#FF69B4` |
| 3.6 – 4.0 | 紫色 | `#800080` |
| 4.1 – 4.5 | 橙色 | `#FF8C00` |
| 4.6 – 5.0 | 浅蓝色 | `#00BFFF` |
| 5.1 – 5.5 | 霓虹橙 | `#FF6600` |
| 5.6 – 6.0 | 霓虹绿 | `#39FF14` |
| 6.1 – 6.5 | 黑色 | `#1C1C1C` |
| 6.6+ | 棕色 | `#8B4513` |

## 自定义颜色方案

通过 `--colors` 覆盖默认的 AR 颜色方案：

```bash
ar-book-labels my_books.xlsx --colors "0.1-2.0:#FFD700,2.1-4.0:#2E8B57,4.1-6.0:#DC143C,6.1-99:#8B4513"
```

格式：`最小值-最大值:#HEX,最小值-最大值:#HEX,...`

- 每个范围为 `最小值-最大值:#HEX`（等级范围 → 颜色）
- 范围之间用逗号分隔
- 范围应覆盖完整的等级区间（0.1–99）
- 黑白模式（`--bw`）下自定义颜色将被忽略

## 开发指南

### 环境搭建

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[yaml,dev]"
```

### 项目结构

```
ar-book-labels/
  ar_book_labels/
    __init__.py        # 包元数据和公共 API
    layout.py          # Layout 数据类 + 网格计算
    config.py          # 配置加载（YAML/JSON）+ 合并
    generator.py       # 核心标签生成逻辑
    cli.py             # 命令行入口（argparse）
    __main__.py        # python -m ar_book_labels 支持
    templates/
      ar_template.xlsx # 参考 Excel 模板
  tests/
    test_layout.py     # 布局计算测试
    test_config.py     # 配置加载测试
    test_generator.py  # 生成器测试
  ar_labels_config.example.yaml  # 示例配置文件
  pyproject.toml       # 构建配置（setuptools）
  LICENSE              # MIT 许可证
  README.md            # English documentation
  README.zh.md         # 本文档
```

### 运行测试

```bash
python -m pytest tests/ -v
```

### 构建与发布

```bash
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

### 自动发布（GitHub Actions）

本项目使用 GitHub Actions 工作流，在创建新的 Release 时自动发布到 PyPI：

1. 更新 `pyproject.toml` 中的版本号
2. 在 GitHub 上创建新的 Release（通过网页或 `gh release create`）
3. `publish.yml` 工作流将自动构建并发布到 PyPI，使用 [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)（OIDC，无需 API Token）

**前提条件**：在 PyPI 上为 `ar-book-labels` 项目配置 [Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)，关联到 `TonyBlur/ar-book-labels` 仓库和 `pypi` 环境。

### 代码风格

- Python 3.8+
- 最小外部依赖（`openpyxl` 必需，`pyyaml` 可选）
- 保持生成逻辑自包含且可测试

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
