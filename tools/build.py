"""Put the dovetail drawing into index.html, between its markers.

    python3 tools/build.py
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dovetail

page = pathlib.Path(__file__).parent.parent / "index.html"
html = page.read_text()
new = re.sub(r"(<!-- dovetail:start -->).*?(<!-- dovetail:end -->)",
             lambda m: m.group(1) + "\n    " + dovetail.svg() + "\n    " + m.group(2), html, flags=re.S)
page.write_text(new)
print("wrote", page.name)
