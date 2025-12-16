import os
import requests
import time
from bs4 import BeautifulSoup

# --- 設定 ---
USER_ID = os.getenv("ATCODER_USER_ID")
SESSION_COOKIE = os.getenv("ATCODER_SESSION")
TIMESTAMP_FILE = "last_timestamp.txt"
# ----------------


def get_last_timestamp():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as f:
            return int(f.read())
    return 0


def save_last_timestamp(timestamp):
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(timestamp))


def fetch_submissions(user, from_second):
    url = (
        "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
        f"?user={user}&from_second={from_second}"
    )
    print(f"Fetching submissions from: {url}")
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return []


def scrape_source_code(contest_id, submission_id):
    url = f"https://atcoder.jp/contests/{contest_id}/submissions/{submission_id}"
    print(f"Scraping: {url}")

    cookies = {"REVEL_SESSION": SESSION_COOKIE} if SESSION_COOKIE else {}

    res = requests.get(url, cookies=cookies, allow_redirects=True)
    if res.status_code != 200:
        print(f"Failed to fetch submission page: {res.status_code}")
        return None

    # login に飛ばされていたら失敗扱い
    if "/login" in res.url:
        print("Redirected to login page (session invalid)")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    code_elem = soup.find(id="submission-code")

    if not code_elem:
        print("submission-code element not found")
        return None

    return code_elem.get_text()


def detect_extension(language):
    if "C++" in language:
        return ".cpp"
    if "Java" in language:
        return ".java"
    if "Rust" in language:
        return ".rs"
    if "Go" in language:
        return ".go"
    return ".py"


def build_dir_path(contest_id, problem_id):
    # ABC だけ abc/ 配下にまとめる
    if contest_id.startswith("abc") and contest_id[3:].isdigit():
        return os.path.join("abc", contest_id, problem_id)
    return os.path.join(contest_id, problem_id)


def main():
    if not USER_ID:
        print("ATCODER_USER_ID not set")
        return

    last_ts = get_last_timestamp()
    print("last_timestamp =", last_ts)

    submissions = fetch_submissions(USER_ID, last_ts)
    if not submissions:
        print("No new submissions found")
        return

    ac_subs = [s for s in submissions if s.get("result") == "AC"]
    ac_subs.sort(key=lambda s: s["epoch_second"])

    latest_success_ts = None

    for sub in ac_subs:
        contest_id = sub["contest_id"]
        problem_id = sub["problem_id"]
        sub_id = sub["id"]
        language = sub["language"]

        ext = detect_extension(language)
        dir_path = build_dir_path(contest_id, problem_id)
        os.makedirs(dir_path, exist_ok=True)

        source = scrape_source_code(contest_id, sub_id)
        if not source:
            print("Scrape failed, stop processing to avoid timestamp skip")
            break

        file_path = os.path.join(dir_path, f"{sub_id}{ext}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(source)

        print(f"Saved: {file_path}")
        latest_success_ts = sub["epoch_second"]
        time.sleep(1)

    # 成功した分だけ timestamp を進める
    if latest_success_ts is not None:
        save_last_timestamp(latest_success_ts)
        print(f"Updated timestamp to {latest_success_ts}")
    else:
        print("No successful saves; timestamp not updated")


if __name__ == "__main__":
    main()

