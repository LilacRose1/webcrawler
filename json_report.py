import json

def write_json_report(page_data, filename="report.json"):
    pages = sorted(page_data.values(), key=lambda p: p["url"])
    f = open(filename, "w", encoding="utf-8")
    json.dump(pages, f, indent=2)
    f.close()
