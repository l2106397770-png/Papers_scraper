# 学术会议论文爬取工具 📚

一款高效、易用的学术会议论文爬取工具，可爬取 `papers.cool` 网站中学术会议论文，支持批量爬取多个顶级学术会议的论文信息，并导出为结构化 CSV 文件，方便科研人员快速检索和管理文献。新增论文 CSV 合并功能，支持将多个爬取结果文件整合为统一表格。仅作工具使用。[papers.cool](https://papers.cool/)

## 🌟 核心功能
- **广泛支持**：覆盖 NeurIPS、ACL、AAAI、CVPR 等 20+ 系列、数百个年份的学术会议
- **结构化导出**：自动提取论文 ID、标题、作者、关键词、摘要、PDF 链接、论文类型等核心字段
- **灵活配置**：支持自定义爬取会议、论文数量、保存路径，适配不同使用场景
- **稳定可靠**：完善的异常处理（超时、SSL 验证、网络错误），确保爬取过程顺畅
- **简单易用**：命令行参数化操作，无需复杂配置，一键启动爬取
- **数据合并**：支持将多个论文 CSV 文件合并为单个文件，自动去重并保持字段一致性


## 📂 目录结构
```
Papers-cool-scraper
├── src/          # 项目核心目录
    ├── config.py            # 常量配置文件（支持会议、默认参数等）
    ├── main.py              # 主程序（爬取、解析、保存逻辑）
    └── merge.py             # CSV 合并工具（多文件整合、去重功能）
├── papers/                  # 数据输出目录（示例）
    └── papers_info.csv      # 导出的论文数据（示例）
├── requirements.txt         # 依赖包列表
└── README.md                # 项目说明文档
```


## 🚀 快速开始

### 1. 环境准备
- **Python 版本**：3.7 及以上
- **安装依赖**：
  ```bash
  pip install -r requirements.txt
  ```

### 2. 基础使用（默认配置）
无需额外参数，默认爬取 `ACL.2025` 会议的全部论文，保存到 `../papers/papers_info.csv`：
```bash
cd papers_scraper
python src/main.py
```

### 3. 自定义爬取示例
#### 示例 1：爬取 NeurIPS.2024 会议的 100 篇论文
```bash
python src/main.py --venue_type NeurIPS.2024 --count 100
```

#### 示例 2：爬取 CVPR.2023 全部论文，保存到自定义路径
```bash
python src/main.py --venue_type CVPR.2023 --count all --save_path ../data/cvpr2023_papers.csv
```

#### 示例 3：HTTPS 报错时，关闭 SSL 证书验证
```bash
python src/main.py --venue_type ICLR.2025 --verify_ssl False
```

### 4. CSV 合并功能使用示例
#### 示例 1：合并多个论文 CSV 文件到指定路径
```bash
python src/merge.py --input_files ../papers/acl2025.csv ../papers/neurips2024.csv --output_file ../papers/merge/merged_papers.csv
```

#### 示例 2：合并目录下所有 CSV 文件（自动去重）
```bash
python src/merge.py --input_dir ../papers --output_file ../papers/merge/merged_papers.csv
```


## ⚙️ 命令行参数说明

### 爬取功能（main.py）
| 参数名        | 类型    | 默认值                      | 可选值                                                                 | 说明                                                                 |
|---------------|---------|-----------------------------|------------------------------------------------------------------------|----------------------------------------------------------------------|
| `--venue_type` | string  | `ACL.2025`                  | 详见 `config.py` 的 `SUPPORTED_VENUES` 变量（格式：`会议名.年份`，如 `NeurIPS.2024`） | 会议类型，需严格遵循 `会议名.年份` 格式，区分大小写                     |
| `--count`     | string  | `all`                       | "all" 或正整数（如 50/100/200）                                        | 爬取论文数量，"all" 表示全部（最大限制为 `config.py` 中 `MAX_PAPER_COUNT=10000` 篇） |
| `--save_path` | string  | `../papers/papers_info.csv` | 任意合法文件路径（后缀为 .csv）                                        | CSV 文件保存路径（需确保目录存在且有写入权限）                       |
| `--verify_ssl`| bool    | `True`                      | True / False                                                           | 是否验证 SSL 证书（HTTPS 访问报错时可设为 False）                     |

### 合并功能（merge.py）
| 参数名         | 类型    | 默认值                  | 可选值                     | 说明                                                                 |
|----------------|---------|-------------------------|----------------------------|----------------------------------------------------------------------|
| `--input_files` | list    | 无（必填）              | 多个 CSV 文件路径（空格分隔） | 需要合并的论文 CSV 文件，支持任意数量（需保证字段结构一致）           |
| `--input_dir`  | string  | 无                      | 合法目录路径               | 批量合并指定目录下的所有 CSV 文件（与 `--input_files` 二选一）        |
| `--output_file`| string  | `../papers/merge/merged.csv` | 任意合法文件路径（后缀为 .csv） | 合并后的 CSV 保存路径（需确保目录存在且有写入权限）                   |
| `--drop_duplicates` | bool | `True`                 | True / False               | 是否自动去除重复论文（基于标题和作者字段判断重复）                   |


## 📋 支持的会议说明
核心支持的会议系列如下，**完整会议列表及年份请查看 `config.py` 的 `SUPPORTED_VENUES` 变量**：
- **AI/ML 领域**：NeurIPS、ICML、ICLR、UAI、COLT
- **NLP 领域**：ACL、EMNLP、NAACL、COLING、IWSLT、INTERSPEECH
- **CV 领域**：CVPR、ECCV、ICCV
- **多领域综合**：AAAI、IJCAI、CoRL、MLSYS
- **安全/系统领域**：NDSS、USENIX-Sec、OSDI、USENIX-Fast


## ⚠️ 注意事项
1. **合规爬取**：请遵守 `papers.cool` 网站的 `robots.txt` 协议，避免高频次、大规模爬取，防止被限制访问
2. **路径权限**：指定 `--save_path`（爬取）或 `--output_file`（合并）时，需确保目标目录已创建且当前用户有写入权限
3. **数据完整性**：部分论文可能因网站数据缺失，导致 `Abstract` 或 `Keywords` 字段为空，属于正常情况
4. **会议类型格式**：`--venue_type` 必须严格遵循 `会议名.年份` 格式（如 `ACL.2025`，而非 `ACL2025` 或 `acl.2025`），具体可选值以 `config.py` 的 `SUPPORTED_VENUES` 为准
5. **网络环境**：若爬取失败，可检查网络连接、代理配置，或通过 `--verify_ssl False` 解决 SSL 问题
6. **合并兼容性**：合并时需确保所有输入 CSV 文件的字段与 `config.py` 中 `PAPER_FIELDS` 定义一致，否则可能导致字段丢失


## ❌ 常见问题排查
1. **爬取失败提示“不支持的会议类型”**：
   - 检查 `--venue_type` 拼写是否正确（区分大小写）
   - 查看 `config.py` 的 `SUPPORTED_VENUES` 变量，确认会议是否在支持列表中

2. **保存/合并 CSV 失败**：
   - 检查目标路径对应的目录是否存在（如 `../data` 需手动创建）
   - 关闭目标 CSV 文件（避免占用导致权限错误）

3. **网络超时/连接失败**：
   - 检查网络稳定性，或配置代理（需修改 `crawl_website` 函数的 `proxies` 参数）
   - 增大超时时间（修改 `config.py` 的 `DEFAULT_TIMEOUT` 变量，默认 10.0 秒）

4. **参数无效报错**：
   - 爬取时：确认 `--count` 仅输入 "all" 或正整数（如输入 0、负数、字符串会报错）；`--verify_ssl` 仅输入 True 或 False
   - 合并时：`--input_files` 和 `--input_dir` 必须提供其一；`--output_file` 需指定合法 CSV 路径

5. **合并后数据异常**：
   - 检查输入文件是否包含非标准字段（需与 `PAPER_FIELDS` 定义一致）
   - 若需保留重复数据，可添加 `--drop_duplicates False` 参数


## 📄 导出 CSV 字段说明
CSV 字段定义详见 `config.py` 的 `PAPER_FIELDS` 变量，具体说明如下：
| 字段名     | 说明                     |
|------------|--------------------------|
| ID         | 论文唯一标识（自增序号） |
| Title      | 论文标题                 |
| Authors    | 作者列表（逗号分隔）     |
| Keywords   | 关键词（网站标注）       |
| Abstract   | 论文摘要                 |
| PDF_Link   | 论文 PDF 下载链接        |
| Type       | 论文类型（如 Oral/Poster）|


## 📝 免责声明
本工具仅用于**学术研究和个人学习**，请勿用于商业用途或违规爬取网站数据。使用时需遵守目标网站的用户协议和相关法律法规，因违规使用导致的一切后果由使用者自行承担。


## 🛠️ 扩展与维护
- 新增支持会议：修改 `config.py` 的 `SUPPORTED_VENUES` 变量，添加符合 `会议名.年份` 格式的会议
- 调整默认参数：修改 `config.py` 中的 `DEFAULT_USER_AGENT`（默认请求头）、`DEFAULT_TIMEOUT`（超时时间）、`MAX_PAPER_COUNT`（最大爬取数量）等变量
- 新增字段提取：在 `parse_papers_info` 函数中扩展解析逻辑，同步更新 `config.py` 的 `PAPER_FIELDS` 变量
- 优化爬取速度：可在 `crawl_website` 函数中添加多线程/异步请求（需注意网站访问限制）
- 扩展合并功能：在 `merge.py` 中修改去重逻辑（调整 `drop_duplicates` 判断字段）或添加字段筛选、格式转换等功能