#!/usr/bin/env python3
"""news.json 검증: 스키마·ID 중복·URL 형식. 문제 있으면 exit 1 (푸시 전 반드시 실행)."""
import json, re, sys
CATS = {"feature", "platform", "agency", "brand", "policy", "data"}
MEDIA = {"naver", "kakao", "meta", "google", "commerce", "tiktok", "etc"}
path = sys.argv[1] if len(sys.argv) > 1 else "news.json"
errs = []
try:
    d = json.load(open(path, encoding="utf-8"))
except Exception as e:
    print("JSON 파싱 실패:", e); sys.exit(1)
if not re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+09:00$", d.get("updated", "")):
    errs.append("updated 형식 오류 (YYYY-MM-DDTHH:MM:SS+09:00)")
seen = set()
for day, v in d.get("days", {}).items():
    if not re.match(r"^\d{4}-\d\d-\d\d$", day): errs.append(f"날짜 키 오류: {day}")
    items = v.get("items", [])
    if not items: errs.append(f"{day}: items 비어 있음")
    for it in items:
        i = it.get("id", "?")
        if i in seen: errs.append(f"ID 중복: {i}")
        seen.add(i)
        if it.get("cat") not in CATS: errs.append(f"{i}: cat 오류 {it.get('cat')}")
        if not it.get("media") or any(m not in MEDIA for m in it["media"]): errs.append(f"{i}: media 오류 {it.get('media')}")
        if not isinstance(it.get("hot"), bool): errs.append(f"{i}: hot은 true/false")
        for k in ("title", "lede"):
            if not isinstance(it.get(k), str) or not it[k].strip(): errs.append(f"{i}: {k} 없음")
        if not isinstance(it.get("points"), list) or not it["points"]: errs.append(f"{i}: points 없음")
        if not isinstance(it.get("action", []), list): errs.append(f"{i}: action은 배열")
        s = it.get("source") or {}
        if not str(s.get("url", "")).startswith("http"): errs.append(f"{i}: source.url 오류")
        if not s.get("name"): errs.append(f"{i}: source.name 없음")
        if not re.match(r"^\d{4}-\d\d-\d\d$", str(s.get("date", ""))): errs.append(f"{i}: source.date 오류")
if errs:
    print("검증 실패:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"OK: {len(d['days'])}일 / {len(seen)}건 / 최신 {max(d['days'])}")
