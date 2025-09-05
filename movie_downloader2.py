import requests
import httpx
import qbittorrentapi
import json
import os
import time
import sys
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import quote

def load_config(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Failed to load config: {e}", flush=True)
        sys.exit(1)

def ensure_download_path(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"[+] Created download folder: {path}", flush=True)
        except Exception as e:
            print(f"[!] Failed to create download folder: {path} -- {e}", flush=True)
            sys.exit(1)

def safe_get(url, headers=None, timeout=20, use_proxy=False):
    headers = headers or {}
    if "User-Agent" not in headers:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, verify=True)
        resp.raise_for_status()
        return resp
    except requests.HTTPError as e:
        print(f"[!] Requests status error: {e.response.status_code} for url '{url}'", flush=True)
        return None
    except Exception as e:
        print(f"[!] Requests error: {e}", flush=True)
        if use_proxy and not url.startswith("https://corsproxy.io/?"):
            proxy_url = f"https://corsproxy.io/?{url}"
            proxy_headers = headers.copy()
            proxy_headers["x-cors-api-key"] = "575a97a2"
            try:
                resp = requests.get(proxy_url, headers=proxy_headers, timeout=timeout, verify=True)
                resp.raise_for_status()
                return resp
            except Exception as e2:
                print(f"[!] Proxy fallback failed: {e2}", flush=True)
        return None

# ... all your search_xxx and helper functions unchanged ...

def select_best(results):
    qualities = ["2160p", "1080p", "720p"]
    yts_results = [r for r in results if r.get("engine") == "YTS"]
    for q in qualities:
        for r in yts_results:
            if r.get("quality") == q:
                return r
    if results:
        return results[0]
    return None

def add_to_qbittorrent(link, client, save_path, is_magnet=True):
    ensure_download_path(save_path)  # Make sure path exists before adding
    try:
        if is_magnet:
            client.torrents_add(urls=link, save_path=save_path)
        else:
            print(f"[!] Direct downloads not implemented - skipping (URL: {link})", flush=True)
            return False
        print(f"[+] Added magnet: {link}", flush=True)
        return True
    except Exception as e:
        print(f"[!] Failed to add magnet: {e}", flush=True)
        return False

def main():
    print("movie_downloader.py started!", flush=True)
    config_path = os.path.join(os.path.dirname(__file__), "api_sites_config.json")
    config = load_config(config_path)

    qbit_cfg = None
    for engine in config:
        if "qBittorrent" in engine:
            qbit_cfg = engine["qBittorrent"]
            break
    if not qbit_cfg:
        print("[!] qBittorrent config missing!", flush=True)
        sys.exit(1)

    # --- FIX: Use correct download path ---
    save_path = os.environ.get("DOWNLOAD_PATH", qbit_cfg.get("save_path", "downloads"))
    # Hardcode here for your system for testing:
    save_path = r"C:\Users\Leo_G\OneDrive\Desktop\MOVIES (SSD)"
    ensure_download_path(save_path)

    qb_client = qbittorrentapi.Client(
        host=qbit_cfg.get("host", "http://127.0.0.1:8080"),
        username=qbit_cfg.get("username", "admin"),
        password=qbit_cfg.get("password", "adminadmin")
    )
    try:
        qb_client.auth_log_in()
        print("Logged into qBittorrent!", flush=True)
    except Exception as e:
        print(f"[!] Failed to login to qBittorrent: {e}", flush=True)
        sys.exit(1)

    print(f"Save path: {save_path}", flush=True)

    movie_list_path = os.environ.get("DOWNLOAD_LIST_FILE", os.path.join(os.path.dirname(__file__), "movie_list.txt"))
    if not os.path.exists(movie_list_path):
        print(f"Missing file: {movie_list_path}", flush=True)
        return

    def print_progress(downloaded, total, title, dest):
        percent = int(downloaded / total * 100) if total else 0
        print(f"  Direct Download Progress: {title}: {percent}% ({downloaded}/{total} bytes)", flush=True)

    process_movie_list(movie_list_path, config, qb_client, save_path, direct_progress_callback=print_progress)

if __name__ == "__main__":
    main()