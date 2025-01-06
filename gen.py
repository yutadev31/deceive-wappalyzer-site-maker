#!/usr/bin/env python3
import re
import requests

base_url = "https://raw.githubusercontent.com/dochne/wappalyzer/main/src/technologies/"

# 不要な文字を置換する関数
def replace_chars(s: str):
  s = s.replace("[0-9]", "1")
  s = s.replace("[0-9.]", "1")
  s = s.replace("[/]*", "")
  s = s.replace("(?:-([\\d.]+))?", "")
  s = s.replace("([\\d\\.]+)", "1.0.0")
  s = s.replace("([\\d.]+)", "1.0.0")
  s = re.sub(r"\(([^()]*)\)\?", lambda m: "", s)
  s = s.replace("\\?", "あ")
  s = s.replace("?", "")
  s = s.replace("\\d", "1")
  s = s.replace("\\s", " ")
  s = s.replace("\\1", "1.0.0")
  s = s.replace("\\w+", "abc")
  s = s.replace(".+", "abc")
  s = s.replace("\\", "")
  s = s.replace("^", "")
  s = s.replace("$", "")
  s = s.replace(".*", "aa")
  s = s.replace("あ", "?")

  return s

def proc_dom(s: str):
  return

data = None
html = ""
cookies = []
err = ""

target_files = list("abcdefghijklmnopqrstuvwxyz_")
for letter in target_files:
  url = f"{base_url}{letter}.json"
  try:
    response = requests.get(url)
    if response.status_code != 200:
      print(f"Failed to fetch: {url}")
      continue
    data = response.json()
  except Exception as e:
    print(f"Error fetching/parsing {url}: {e}")
    continue

  for key, item in data.items():
    if "scriptSrc" in item:
      try:
        scriptSrc = item["scriptSrc"]
        if isinstance(scriptSrc, str):
          html += f"<script src=\"{replace_chars(scriptSrc)}\" type='text/fake'></script>\n"
        elif isinstance(scriptSrc, list):
          for src in scriptSrc:
            html += f"<script src=\"{replace_chars(src)}\"></script>\n"
      except Exception:
        err += f"scriptSrc: {key}\n"
    if "meta" in item:
      try:
        meta = item["meta"]
        for meta_key, meta_value in meta.items():
          if isinstance(meta_value, str):
            html += f"<meta name=\"{meta_key}\" content=\"{replace_chars(meta_value)}\" />\n"
      except Exception:
        err += f"meta: {key}\n"
    if "cookies" in item:
      try:
        cookies_data = item["cookies"]
        for cookie_key, cookie_value in cookies_data.items():
          cookies.append(f"{cookie_key}={replace_chars(cookie_value or 'cookies')}")
      except Exception:
        err += f"cookies: {key}\n"
    if "dom" in item:
      try:
        dom = item["dom"]
        if isinstance(dom, str):
          doms = dom.split(",")
          for dom_item in doms:
            html += f"<div>{dom_item.strip()}</div>\n"
        elif isinstance(dom, list):
          for dom_item in dom:
            doms = dom_item.split(",")
            for dom_item in doms:
              html += f"<div>{dom_item.strip()}</div>\n"
      except Exception:
        err += f"dom: {key}\n"

cookies_js = "; ".join(cookies)

html += f"<script>document.cookie = \"{cookies_js}\"</script>"

with open("index.html", "w") as f:
  f.write(html)

print("HTMLファイルを生成しました。")
