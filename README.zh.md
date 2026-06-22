# ar-book-labels

**[English](README.md)** | 简体中文

从 Excel 表格自动生成可打印的 [Accelerated Reader](https://www.renaissance.com/accelerated-reader/) 书籍标签。标签包含书名、作者、AR 等级（标准颜色编码）、积分和测验编号，适用于打印后贴在书本上。

## 功能特点

- **AR 标准颜色编码**：12 个颜色区间，从黄色（0.1–1.5）到棕色（6.6+）
- **打印就绪 HTML 输出**：每页 4 列 x 11 行 = 44 个标签，内置 `@page` CSS 可直接打印
- **智能文本截断**：书名支持 2 行换行 + 省略号；作者名单行显示
- **作者优先布局**：作者名在书名上方，方便按作者排序整理书籍
- **屏幕预览**：SVG viewBox 缩放，浏览器中清晰预览
- **内置模板**：附带参考 Excel 模板，包含示例数据和字段说明

## 安装

```bash
pip install ar-book-labels
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

## 命令行用法

```
ar-book-labels <excel文件> [选项]
```

### 参数

| 参数 | 说明 |
|------|------|
| `excel` | Excel 文件路径（.xlsx） |

### 选项

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `-o, --output` | `AR_Book_Labels.html` | 输出 HTML 文件路径 |
| `-s, --sheet` | `Merged` | 要读取的工作表名称 |
| `--col-title` | `AR Title` | Excel 中书名对应的列名 |
| `--col-author` | `AR Author` | Excel 中作者对应的列名 |
| `--col-level` | `Book Level` | Excel 中等级对应的列名 |
| `--col-points` | `AR Points` | Excel 中积分对应的列名 |
| `--col-quiz` | `Quiz Number` | Excel 中测验编号对应的列名 |
| `--start-row` | `2` | 数据开始的行号（1 = 表头行） |
| `--scale` | `3` | 屏幕预览的缩放倍数 |
| `--template` | — | 将参考 Excel 模板复制到当前目录并退出 |
| `-V, --version` | — | 显示版本号并退出 |

### 示例

```bash
# 基本用法
ar-book-labels my_books.xlsx

# 自定义输出路径和工作表名
ar-book-labels my_books.xlsx -o output/labels.html -s "图书数据"

# 自定义列名（如果你的 Excel 使用不同的表头）
ar-book-labels my_books.xlsx --col-title "书名" --col-author "作者" --col-level "等级"

# 自定义起始行（如数据从第 3 行开始）
ar-book-labels my_books.xlsx --start-row 3

# 复制参考模板
ar-book-labels --template
```

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

## 开发指南

### 环境搭建

```bash
git clone https://github.com/TonyBlur/ar-book-labels.git
cd ar-book-labels
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 项目结构

```
ar-book-labels/
  ar_book_labels/
    __init__.py        # 包元数据和公共 API
    generator.py       # 核心标签生成逻辑
    cli.py             # 命令行入口（argparse）
    __main__.py        # python -m ar_book_labels 支持
    templates/
      ar_template.xlsx # 参考 Excel 模板
  tests/
    test_generator.py  # 单元测试
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
- 除 `openpyxl` 外无其他外部依赖
- 保持生成逻辑自包含且可测试

## 许可证

MIT — 详见 [LICENSE](LICENSE)。
