import os
import requests
import json
import time
from bs4 import BeautifulSoup

# --- 設定 ---
# GitHub Actionsの環境変数からユーザーIDを取得
USER_ID = os.getenv('ATCODER_USER_ID')
# 最後に取得した提出のエポック秒を保存するファイル
TIMESTAMP_FILE = "last_timestamp.txt"
# AtCoderのセッションCookieを環境変数から取得
SESSION_COOKIE = os.getenv('ATCODER_SESSION')
# ----------------

def get_last_timestamp():
    """最後に取得したタイムスタンプをファイルから読み込む"""
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as f:
            return int(f.read())
    return 0  # ファイルがなければ最初から

def save_last_timestamp(timestamp):
    """最新のタイムスタンプをファイルに保存する"""
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(timestamp))

def fetch_submissions(user, from_second):
    """AtCoderProblems APIから提出履歴を取得する"""
    api_url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={user}&from_second={from_second}"
    print(f"Fetching submissions from: {api_url}")
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: Failed to fetch submissions. Status code: {response.status_code}")
        return []

def scrape_source_code(contest_id, submission_id):
    """AtCoderの提出ページからソースコードをスクレイプする"""
    submission_url = f"https://atcoder.jp/contests/{contest_id}/submissions/{submission_id}"
    print(f"Scraping source code from: {submission_url}")

    cookies = {'REVEL_SESSION': SESSION_COOKIE} if SESSION_COOKIE else {}

    try:
        response = requests.get(submission_url, cookies=cookies)
        response.raise_for_status() # エラーがあれば例外を発生
        soup = BeautifulSoup(response.text, 'html.parser')
        code_element = soup.find(id="submission-code")
        if code_element:
            return code_element.get_text()
        else:
            print("Error: Could not find submission code element.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {submission_url}: {e}")
        return None

def main():
    if not USER_ID:
        print("Error: ATCODER_USER_ID is not set.")
        return

    last_timestamp = get_last_timestamp()
    submissions = fetch_submissions(USER_ID, last_timestamp + 1)

    if not submissions:
        print("No new submissions found.")
        return

    # ACした提出のみをフィルタリング
    ac_submissions = [s for s in submissions if s.get("result") == "AC"]

    # 古い順に処理
    ac_submissions.sort(key=lambda s: s["epoch_second"])

    if not ac_submissions:
        print("No new AC submissions found.")
        # AC以外の提出があった場合でもタイムスタンプは更新
        latest_timestamp = max(s["epoch_second"] for s in submissions)
        save_last_timestamp(latest_timestamp)
        return

    for sub in ac_submissions:
        contest_id = sub["contest_id"]
        problem_id = sub["problem_id"]
        sub_id = sub["id"]
        language = sub["language"]

        # ファイル拡張子を決定
        ext = ".py" # デフォルトはPython
        if "C++" in language:
            ext = ".cpp"
        elif "Java" in language:
            ext = ".java"
        elif "Rust" in language:
            ext = ".rs"
        elif "Go" in language:
            ext = ".go"

        # ディレクトリを作成
        dir_path = os.path.join(contest_id, problem_id)
        os.makedirs(dir_path, exist_ok=True)

        # ソースコードを取得してファイルに保存
        source_code = scrape_source_code(contest_id, sub_id)
        if source_code:
            file_path = os.path.join(dir_path, f"{sub_id}{ext}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(source_code)
            print(f"Successfully saved: {file_path}")

        # AtCoderサーバーへの負荷を考慮して少し待つ
        time.sleep(1)

    # 最後に処理した提出のタイムスタンプを保存
    latest_timestamp = max(s["epoch_second"] for s in submissions)
    save_last_timestamp(latest_timestamp)
    print("Process finished.")

if __name__ == "__main__":
    main()
