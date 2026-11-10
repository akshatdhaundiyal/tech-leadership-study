# Regenerates docs/demo.gif. Needs Google Chrome and Pillow:
#   python3 -m venv /tmp/v && /tmp/v/bin/pip install pillow
#   /tmp/v/bin/python docs/demo/make-gif.py . docs/demo.gif

import html, json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1]
OUT = sys.argv[2]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1000, 720
FR = os.path.join(HERE, "frames"); os.makedirs(FR, exist_ok=True)

diagram = open(os.path.join(HERE, "diagram.txt"), encoding="utf-8").read().splitlines()

PROMPT = [
    "We need in-app and email notifications when a leave request is",
    "approved. 20k employees, 300 companies. PM wants the bell \"instantly\".",
]
DIR = "docs/design/2026-11-05-leave-notifications/"

CSS = f"""
*{{box-sizing:border-box}} html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden}}
body{{background:radial-gradient(1200px 700px at 0% 0%,#3b2a8a 0%,transparent 60%),
 radial-gradient(900px 600px at 100% 100%,#0e5a7a 0%,transparent 60%),#0b0f1e;
 display:flex;align-items:center;justify-content:center;font-family:system-ui,-apple-system,sans-serif}}
.win{{width:{W-48}px;height:{H-44}px;border-radius:12px;overflow:hidden;background:#0d1117;
 box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);display:flex;flex-direction:column}}
.bar{{height:34px;flex:none;display:flex;align-items:center;gap:8px;padding:0 14px;background:#161b22;
 border-bottom:1px solid #21262d;color:#8b949e;font-size:12.5px}}
.dot{{width:12px;height:12px;border-radius:50%}}
.title{{flex:1;text-align:center;margin-right:60px}}
.term{{flex:1;display:flex;flex-direction:column;justify-content:flex-end;overflow:hidden;
 padding:12px 18px 14px;font:14.5px/19px Menlo,'SF Mono',monospace;color:#c9d1d9;white-space:pre}}
.p{{color:#f0f6fc;font-weight:600}} .pc{{color:#d2a8ff}} .ok{{color:#3fb950}} .dim{{color:#8b949e}}
.k{{color:#79c0ff}} .new{{color:#3fb950;font-weight:700}} .chg{{color:#e3b341;font-weight:700}}
.sync{{color:#58a6ff}} .async{{color:#bc8cff}} .h{{color:#f0f6fc;font-weight:700}}
.cur{{background:#c9d1d9;color:#0d1117}}
.url{{flex:1;margin:0 40px 0 20px;background:#0d1117;border:1px solid #30363d;border-radius:6px;
 padding:4px 10px;color:#8b949e;font-size:12.5px;text-align:left}}
iframe{{flex:1;border:0;width:100%;background:#0b1120}}
"""

def chrome_bar(title):
    return ('<div class="bar"><span class="dot" style="background:#ff5f57"></span>'
            '<span class="dot" style="background:#febc2e"></span>'
            '<span class="dot" style="background:#28c840"></span>'
            f'<span class="title">{title}</span></div>')

def color_diagram(line):
    s = html.escape(line)
    if s.strip() in ("AS-IS", "TO-BE"):
        return f'<span class="h">{s}</span>'
    s = re.sub(r"(─+[▶◀]|[▼▲▶◀])", r'<span class="sync">\1</span>', s)
    s = re.sub(r"([◁]?╌+[▷]?|[▽◁▷])", r'<span class="async">\1</span>', s)
    s = re.sub(r"(?<=[ A-Za-z])\+(?=[ │])", '<span class="new">+</span>', s)
    s = re.sub(r"(?<= )~(?=[ │])", '<span class="chg">~</span>', s)
    if "rolls back" in s:
        s = f'<span class="dim">{s}</span>'
    return s

def L(text, cls=None):
    t = html.escape(text)
    return f'<span class="{cls}">{t}</span>' if cls else t

# ---------- timeline: list of (lines_html, duration_ms, kind) ----------
frames = []
lines = []

def push(ms, extra=None):
    frames.append(("term", lines + (extra or []), ms))

# 1. type the prompt
typed = ["", ""]
for i, full in enumerate(PROMPT):
    for n in range(0, len(full) + 1, 7):
        typed[i] = full[:n]
        cur = [f'<span class="pc">&gt; </span><span class="p">{html.escape(typed[0])}</span>'
               + ('<span class="cur"> </span>' if i == 0 else '')]
        if i == 1:
            cur.append(f'  <span class="p">{html.escape(typed[1])}</span><span class="cur"> </span>')
        frames.append(("term", cur, 55))
lines += [f'<span class="pc">&gt; </span><span class="p">{html.escape(PROMPT[0])}</span>',
          f'  <span class="p">{html.escape(PROMPT[1])}</span>', ""]
push(500)

# 2. skill + estimates
for spin in "⠋⠙⠹⠸":
    push(110, [f'<span class="ok">{spin}</span> Skill(<span class="k">system-design-first</span>) <span class="dim">thinking…</span>'])
lines.append('<span class="ok">●</span> Skill(<span class="k">system-design-first</span>)')
push(250)
lines.append('<span class="ok">●</span> <span class="h">Depth L2</span> <span class="dim">— fan-out 1 → 2.5k + real-time delivery</span>')
push(450)
lines.append("")
for t, ms in [
    ('  <span class="k">Estimates</span>  ~5k notifications/day · ~2k open tabs at the 9:00 peak', 380),
    ('             polling every 5 s would be <span class="chg">400 rps</span> of empty queries', 380),
    ('  <span class="k">Verdict</span>    no Kafka, no new service — <span class="ok">reuse Celery + Redis</span>', 900),
]:
    lines.append(t); push(ms)
lines.append("")
# 3. diagrams, line by line
for d in diagram:
    lines.append(color_diagram(d))
    ms = 130
    if d.strip() == "TO-BE": ms = 350
    if "rolls back" in d: ms = 900
    push(ms)
push(1400)

# 4. design folder
lines.append("")
for t, ms in [
    (f'<span class="ok">●</span> Wrote <span class="k">{DIR}</span>', 300),
    ('  ├── README.md            <span class="dim">design brief, Mermaid inline</span>', 160),
    ('  ├── as-is.mmd · to-be.mmd', 160),
    ('  ├── flows/approve-to-bell.mmd', 160),
    ('  └── architecture.html    <span class="ok">← open in a browser</span>', 1500),
]:
    lines.append(t); push(ms)

# 5. type open command
lines.append("")
cmd = f"open {DIR}architecture.html"
for n in range(0, len(cmd) + 1, 9):
    push(45, [f'<span class="pc">&gt; </span><span class="p">{html.escape(cmd[:n])}</span><span class="cur"> </span>'])
push(500, [f'<span class="pc">&gt; </span><span class="p">{html.escape(cmd)}</span>'])

# 6. browser
frames.append(("browser:To-be", None, 3800))
frames.append(("browser:Compare", None, 2600))
frames.append(("browser:Flows", None, 3200))

# ---------- render ----------
src = open(os.path.join(REPO, "examples/leave-notifications/architecture.html"), encoding="utf-8").read()
for tab in ("To-be", "Compare", "Flows"):
    open(os.path.join(FR, f"arch-{tab}.html"), "w", encoding="utf-8").write(
        src.replace('localStorage.getItem("sdf-tab")', json.dumps(tab)))

def page(kind, content):
    if kind == "term":
        body = (f'<div class="win">{chrome_bar("~/hr-platform — claude")}'
                f'<div class="term" style="justify-content:{"flex-end" if len(content) > 32 else "flex-start"}"><div>' + "\n".join(content) + '</div></div></div>')
    else:
        tab = kind.split(":")[1]
        body = ('<div class="win"><div class="bar"><span class="dot" style="background:#ff5f57"></span>'
                '<span class="dot" style="background:#febc2e"></span><span class="dot" style="background:#28c840"></span>'
                f'<span class="url">file://…/{DIR}architecture.html</span></div>'
                f'<iframe src="arch-{tab}.html"></iframe></div>')
    return f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><body>{body}</body>'

jobs = []
for i, (kind, content, ms) in enumerate(frames):
    hp = os.path.join(FR, f"f{i:03}.html")
    open(hp, "w", encoding="utf-8").write(page(kind.split(":")[0] if kind == "term" else kind, content))
    jobs.append((i, hp, kind))

def shoot(job):
    i, hp, kind = job
    png = os.path.join(FR, f"f{i:03}.png")
    budget = "12000" if kind.startswith("browser") else "300"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={W},{H}", "--force-device-scale-factor=2",
                    f"--virtual-time-budget={budget}", f"--screenshot={png}", "file://" + hp],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return png

with ThreadPoolExecutor(6) as ex:
    pngs = list(ex.map(shoot, jobs))

from PIL import Image
imgs, durs = [], []
for png, (_, _, ms) in zip(pngs, frames):
    im = Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)
    imgs.append(im); durs.append(ms)

ACCENTS = ["#3fb950", "#e3b341", "#58a6ff", "#bc8cff", "#79c0ff", "#d2a8ff", "#ff5f57", "#febc2e", "#28c840", "#8b949e", "#f0f6fc"]
def quant(im):
    src = Image.new("RGB", (W, H + 60)); src.paste(im, (0, 0))
    for k, c in enumerate(ACCENTS):
        src.paste(Image.new("RGB", (W // len(ACCENTS) + 1, 60), c), (k * (W // len(ACCENTS)), H))
    pal = src.quantize(colors=256, method=Image.MEDIANCUT)
    return im.quantize(palette=pal, dither=Image.Dither.NONE)
q = [quant(im) for im in imgs]
q[0].save(OUT, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
print(len(frames), "frames,", round(os.path.getsize(OUT) / 1e6, 2), "MB,", round(sum(durs) / 1000, 1), "s")
