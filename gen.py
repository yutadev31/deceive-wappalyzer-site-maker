#!/usr/bin/env python3
import json
import os
import re

INPUT_DIR = "wappalyzer/src/technologies/"

data = []

input_files = os.listdir(INPUT_DIR)
for file in input_files:
  with open(INPUT_DIR + file, "r") as f:
    f_data = json.load(f)
    keys = f_data.keys()
    for key in keys:
      data.append(f_data[key])

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

  if (s.find("\n") != -1):
    print(s)
    exit(1)

  return s

def proc_dom(s: str):
  return

html = ""
err = ""

cookies = []

for item in data:
  if "scriptSrc" in item:
    try:
      scriptSrc: str = item["scriptSrc"]

      if type(scriptSrc) == str:
        html += "<script src=\"" + replace_chars(scriptSrc) + "\"></script>\n"
      else:
        for src in x["scriptSrc"]:
          html += "<script src=\"" + replace_chars(scriptSrc) + "\"></script>\n"
    except:
      err += "scriptSrc: " + key + "\n"
  if "meta" in item:
    try:
      meta = item["meta"]

      meta_keys = meta.keys()
      for meta_key in meta_keys:
        html += "<meta name=\"" + meta_key + "\" content=\"" + replace_chars(meta[meta_key]) + "\" />\n"
    except:
      err += "meta: " + key + "\n"
  if "cookies" in item:
    try:
      i_cookies = item["cookies"]
      cookies_keys = i_cookies.keys()
      for cookies_key in cookies_keys:
        c = i_cookies[cookies_key]
        if c == "":
          cookies.append(cookies_key + "=" + "cookies")
        else:
          cookies.append(cookies_key + "=" + replace_chars(c))
    except:
      err += "cookies: " + key + "\n"
  if "dom" in item:
    try:
      dom = item["dom"]
      if type(dom) == str:
        doms = x["dom"].split(",")
        for dom in doms:
          dom = dom.strip()
      elif type(dom) == list:
        for dom_item in dom:
          doms = dom_item.split(",")
          for dom in doms:
            dom = dom.strip()
    except:
      err += "dom: " + key + "\n"

cookies_js = "; ".join(cookies)

html += "<script>document.cookie = \"" + cookies_js + "\"</script>"

with open("out/index.html", "w") as f:
  f.write(html)
