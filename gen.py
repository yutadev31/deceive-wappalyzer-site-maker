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

def convert_selector_to_html(selector: str):
  # 不要な文字を削除
  selector = selector.replace("*", "").replace("^", "").replace("'", "").replace("\\","")

  # タグ名だけの場合
  if re.match(r'^[a-zA-Z-]+$', selector):  # 単一のタグ名
    return f'<{selector}></{selector}>'

  # IDが指定された場合 (例: #id)
  if re.match(r'^#[a-zA-Z0-9-_]+$', selector):  # ID形式
    id_ = selector[1:]  # 先頭の#を削除
    return f'<div id="{id_}"></div>'

  # タグ名とIDが指定された場合 (例: div#id)
  if re.match(r'^[a-zA-Z0-9-]+#[a-zA-Z0-9-_]+$', selector):  # div#id形式
    tag, id_ = selector.split('#')
    return f'<{tag} id="{id_}"></{tag}>'

  # クラスが指定された場合 (例: .class)
  if re.match(r'^\.[a-zA-Z0-9\-\_]+$', selector):  # .class形式
    class_ = selector[1:]  # 先頭の.を削除
    return f'<div class="{class_}"></div>'

  # タグ名とクラスが指定された場合 (例: div.class)
  if re.match(r'^[a-zA-Z0-9\-]+\.[a-zA-Z0-9-_]+$', selector):  # div.class形式
    tag, class_ = selector.split('.')
    return f'<{tag} class="{class_}"></{tag}>'

  # 属性が指定された場合 (例: div[attr=value])
  if re.match(r'^[a-zA-Z0-9\-]*\[[^\]]*\](\[[^\]]*\])*$', selector):  # div[attr=value]形式
    # タグ名と属性部分を分ける

    tag = selector.split('[')[0].strip()
    if selector[0] == '[':
      tag = "div"
    # 属性部分を抽出
    attrs = re.findall(r'\[([^\]]+)\]', selector)
    # 属性を処理
    attributes = ' '.join([f'{attr.split("=")[0]}="{attr.split("=")[1]}"' if '=' in attr else f'{attr}' for attr in attrs])
    return f'<{tag} {attributes}></{tag}>'

  print(selector)

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
            html += f"{convert_selector_to_html(dom_item.strip())}\n"
        elif isinstance(dom, list):
          for dom_item in dom:
            doms = dom_item.split(",")
            for dom_item in doms:
              html += f"{convert_selector_to_html(dom_item.strip())}\n"
      except Exception:
        err += f"dom: {key}\n"

cookies_js = "; ".join(cookies)

html += f"<script>document.cookie = \"{cookies_js}\"</script>"

with open("index.html", "w") as f:
  f.write(html)

with open("err.log", "w") as f:
  f.write(err)

print("HTMLファイルを生成しました。")
