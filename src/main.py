"""
学术会议论文爬取工具
网址：https://papers.cool
功能：爬取 papers.cool 网站的指定会议论文信息，支持导出为 CSV 文件
支持会议：NeurIPS、ACL、AAAI、EMNLP、NAACL、ICML、CVPR、ICLR 等
"""

import argparse
import re
import csv
from typing import Optional, Dict, Any, Union, List

import requests
from bs4 import BeautifulSoup  # 保留导入（如需扩展DOM解析可直接使用）
from lxml import etree
from requests.exceptions import (
    RequestException,
    ConnectTimeout,
    ReadTimeout,
    SSLError
)
from config import (
    SUPPORTED_VENUES,
    DEFAULT_USER_AGENT,
    DEFAULT_TIMEOUT,
    DEFAULT_CSV_PATH,
    MAX_PAPER_COUNT,
    PAPER_FIELDS
)


def parse_papers_info(html_str: str) -> List[Dict[str, str]]:
    """
    解析HTML字符串中的论文信息
    Args:
        html_str: 包含论文列表的HTML字符串
    Returns:
        论文信息列表，每个元素为包含论文详情的字典
    """
    # 用lxml解析HTML（自动修复不规范标签）
    html = etree.HTML(html_str)

    # 提取论文总数
    total_text_list = html.xpath('//*[@id="venue"]/p/text()')
    total_count = "未知"
    if total_text_list:
        total_text = total_text_list[-1]
        pattern = re.compile(r'(\d+)')
        match_result = pattern.findall(total_text)
        if match_result:
            total_count = match_result[0]
    print(f"📊 此板块共 {total_count} 篇论文")

    # 定位核心论文列表容器（class="papers"）
    papers_elements = html.xpath('//*[@class="papers"]')
    if not papers_elements:
        print("⚠️  未找到class='papers'的论文列表容器")
        return []

    # 解析每篇论文的详细信息
    target_element = papers_elements[0]
    papers_list = []

    for tag in target_element:
        paper_info = {field: "" for field in PAPER_FIELDS if field != "ID"}

        # 关键词：外层div的keywords属性
        keywords = tag.xpath('./@keywords')
        if keywords:
            paper_info["Keywords"] = keywords[0].strip()

        # 标题：h2.title下的a标签文本
        title_list = tag.xpath('.//h2[@class="title"]/a/text()')
        if title_list:
            paper_info["Title"] = title_list[0].strip()

        # 作者：p.metainfo.authors下所有a.author的文本（逗号拼接）
        authors_list = tag.xpath('.//p[@class="metainfo authors notranslate"]/a/text()')
        if authors_list:
            paper_info["Authors"] = ", ".join(author.strip() for author in authors_list)

        # 摘要：p.summary的文本
        abstract_list = tag.xpath('.//p[contains(@class, "summary")]/text()')
        if abstract_list:
            paper_info["Abstract"] = abstract_list[0].strip()

        # PDF链接：a.title-pdf的data属性
        pdf_link_list = tag.xpath('.//h2[@class="title"]/a[@class="title-pdf notranslate"]/@data')
        if pdf_link_list:
            paper_info["PDF_Link"] = pdf_link_list[0].strip()

        # 论文类型：p.metainfo.subjects的文本
        type_list = tag.xpath('.//p[@class="metainfo subjects"]/a/text()')
        if type_list:
            paper_info["Type"] = type_list[0].strip()

        # 过滤空数据（标题为空则跳过）
        if paper_info["Title"]:
            papers_list.append(paper_info)

    return papers_list


def crawl_website(
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[Dict[str, Any], str]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    proxies: Optional[Dict[str, str]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    verify_ssl: bool = True,
    allow_redirects: bool = True,
    encoding: Optional[str] = None
) -> Dict[str, Any]:
    """
    通用网站爬取函数，支持GET/POST请求，包含完善的异常处理

    Args:
        url: 目标网站URL
        method: 请求方法（GET/POST），默认GET
        params: GET请求查询参数（字典）
        data: POST请求数据（字典/字符串）
        headers: 请求头字典（默认添加基础User-Agent）
        cookies: Cookie字典（维持登录状态等）
        proxies: 代理配置字典（格式：{"http": "http://IP:端口", "https": "..."}）
        timeout: 请求超时时间（秒），默认10秒
        verify_ssl: 是否验证SSL证书，默认True
        allow_redirects: 是否允许重定向，默认True
        encoding: 响应编码（默认自动识别）

    Returns:
        爬取结果字典：
        - success: 爬取是否成功（bool）
        - status_code: 响应状态码（None表示失败）
        - content: 响应文本（失败时为错误信息）
        - headers: 响应头（字典，失败时为None）
        - encoding: 实际使用的编码（失败时为None）
    """
    # 合并默认请求头与用户自定义请求头
    final_headers = {
        "User-Agent": DEFAULT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": url
    }
    if headers:
        final_headers.update(headers)

    # 初始化返回结果
    result = {
        "success": False,
        "status_code": None,
        "content": "",
        "headers": None,
        "encoding": None
    }

    try:
        # 发送HTTP请求
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            headers=final_headers,
            cookies=cookies,
            proxies=proxies,
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=allow_redirects
        )

        # 验证响应状态（2xx为成功）
        response.raise_for_status()

        # 处理编码（优先用户指定，其次自动识别）
        if encoding:
            response.encoding = encoding
        else:
            response.encoding = response.apparent_encoding or response.encoding

        # 填充成功结果
        result.update({
            "success": True,
            "status_code": response.status_code,
            "content": response.text,
            "headers": dict(response.headers),
            "encoding": response.encoding
        })

    except ConnectTimeout:
        result["content"] = f"连接超时（超时时间：{timeout}秒）"
    except ReadTimeout:
        result["content"] = f"读取超时（超时时间：{timeout}秒）"
    except SSLError:
        result["content"] = "SSL证书验证失败（可尝试添加 --verify-ssl=False 参数）"
    except RequestException as e:
        # 捕获requests相关异常（4xx/5xx状态码、URL错误等）
        result["content"] = f"请求失败：{str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            result["status_code"] = e.response.status_code
    except Exception as e:
        # 捕获其他未预期异常
        result["content"] = f"未知错误：{str(e)}"

    return result


def save_papers_to_csv(paper_list: List[Dict[str, str]], csv_save_path: str = DEFAULT_CSV_PATH) -> None:
    """
    将论文信息保存到CSV文件（自动添加唯一ID）
    Args:
        paper_list: 论文信息列表（parse_papers_info的返回值）
        csv_save_path: CSV文件保存路径
    """
    if not paper_list:
        print("⚠️  无有效论文数据，跳过CSV保存")
        return

    # 为每篇论文添加唯一ID（从1开始递增）
    papers_with_id = []
    for idx, paper in enumerate(paper_list, 1):
        paper_with_id = paper.copy()
        paper_with_id["ID"] = str(idx)
        papers_with_id.append(paper_with_id)

    # 写入CSV文件
    try:
        with open(csv_save_path, "w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=PAPER_FIELDS)
            writer.writeheader()
            writer.writerows(papers_with_id)

        print(f"✅ 成功保存 {len(papers_with_id)} 篇论文到：{csv_save_path}")
    except PermissionError:
        print(f"❌ 保存CSV失败：无写入权限（路径：{csv_save_path}）")
    except FileNotFoundError:
        print(f"❌ 保存CSV失败：路径不存在（路径：{csv_save_path}）")
    except Exception as e:
        print(f"❌ 保存CSV失败：{str(e)}")


def validate_args(args: argparse.Namespace) -> tuple[bool, str, int]:
    """
    验证命令行参数有效性
    Args:
        args: 解析后的命令行参数
    Returns:
        (是否有效, 会议类型, 论文数量)
    """
    # 验证会议类型
    if args.venue_type not in SUPPORTED_VENUES:
        print(f"❌ 不支持的会议类型：{args.venue_type}")
        print(f"📋 支持的会议类型：{', '.join(SUPPORTED_VENUES[:10])}...（共{len(SUPPORTED_VENUES)}个）")
        return False, "", 0

    # 验证论文数量
    if args.count == "all":
        paper_count = MAX_PAPER_COUNT
    else:
        try:
            paper_count = int(args.count)
            if paper_count <= 0:
                print(f"❌ 论文数量必须为正整数（当前：{args.count}）")
                return False, "", 0
        except ValueError:
            print(f"❌ 无效的论文数量：{args.count}（支持：正整数或'all'）")
            return False, "", 0

    return True, args.venue_type, paper_count


def main():
    """主函数：解析参数 → 爬取 → 解析 → 保存"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='📚 学术会议论文爬取工具（支持 papers.cool）')
    
    parser.add_argument(
        '--venue_type',
        type=str,
        default='ACL.2025',
        help=f'会议类型（默认：ACL.2025，支持{len(SUPPORTED_VENUES)}个会议）'
    )
    
    parser.add_argument(
        '--count',
        type=str,
        default='all',
        help='抓取论文数量（默认：all，支持正整数如50/100）'
    )
    
    parser.add_argument(
        '--save_path',
        type=str,
        default=DEFAULT_CSV_PATH,
        help=f'CSV保存路径（默认：{DEFAULT_CSV_PATH}）'
    )
    
    parser.add_argument(
        '--verify_ssl',
        type=bool,
        default=True,
        help='是否验证SSL证书（默认：True，HTTPS报错时可设为False）'
    )
    
    args = parser.parse_args()

    # 验证参数有效性
    valid, venue_type, paper_count = validate_args(args)
    if not valid:
        return

    # 构建爬取URL
    url = f"https://papers.cool/venue/{venue_type}?show={paper_count}"
    print(f"🚀 开始爬取：{url}")

    # 执行爬取
    crawl_result = crawl_website(url=url, verify_ssl=args.verify_ssl)
    if not crawl_result["success"]:
        print(f"❌ 爬取失败：{crawl_result['content']}")
        return
    print(f"✅ 爬取成功！状态码：{crawl_result['status_code']}")

    # 解析论文信息
    print("🔍 开始解析论文信息...")
    papers = parse_papers_info(crawl_result["content"])
    print(f"✅ 解析完成！共获取 {len(papers)} 篇有效论文")

    # 保存到CSV
    save_papers_to_csv(papers, csv_save_path=args.save_path)
    print("🎉 任务完成！")


if __name__ == "__main__":
    main()