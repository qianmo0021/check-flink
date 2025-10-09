import requests
import json
import logging
import warnings

# ---------------------------
# 日志与请求头配置
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="😎 %(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made.*")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36 "
        "(check-flink/2.0; +https://github.com/willow-god/check-flink)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "X-Check-Flink": "1.0"
}

RAW_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "X-Check-Flink": "2.0"
}

# ---------------------------
# 配置
# ---------------------------
SOURCE_URL = "https://lxb-blog.pages.dev/projects.json"
RESULT_FILE = "./projects_status.json"  # <-- 输出文件名修改这里

# ---------------------------
# 工具函数
# ---------------------------
def fetch_projects():
    try:
        r = requests.get(SOURCE_URL, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("projects", [])
    except Exception as e:
        logging.error(f"❌ 获取项目数据失败: {e}")
        return []

def check_url(url):
    """检测 URL 并返回详细状态标记"""
    try:
        r = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
        code = r.status_code
        if code == 200:
            return "✅ 200 正常 点击访问进行尝试"
        elif code == 403:
            return "⚠️ 403 禁止访问 点击访问进行尝试"
        elif code == 404:
            return "❌ 404 未找到"
        elif code == 500:
            return "⚠️ 500 服务器错误 点击访问进行尝试"
        elif code == 503:
            return "⚠️ 503 服务不可用 点击访问进行尝试"
        else:
            return f"⚠️ {code} 状态异常 点击访问进行尝试"
    except Exception as e:
        logging.warning(f"❌ 无法访问 {url}，错误: {e}")
        return "❌ 无法访问"

# ---------------------------
# 主程序
# ---------------------------
def main():
    projects = fetch_projects()
    if not projects:
        logging.warning("❌ 没有项目可检测")
        return

    new_projects = []

    for p in projects:
        url = p.get("url")
        name = p.get("name", "")
        remark = p.get("remark", "")
        created = p.get("created", "")
        status = check_url(url)

        new_projects.append({
            "name": name,
            "url": url,
            "status": status,
            "remark": remark,
            "created": created
        })

    result = {"projects": new_projects}

    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logging.info(f"✅ 检测完成，结果已保存至 {RESULT_FILE}")

if __name__ == "__main__":
    main()
