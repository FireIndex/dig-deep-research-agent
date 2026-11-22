import logging
import re
import time
from urllib.parse import urlparse

import streamlit as st

import seo

seo.inject()  # Open Graph tags for link previews

st.set_page_config(
    page_title="Dig — deep research",
    page_icon="◐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ───────────────────────────── design tokens ─────────────────────────────
INK, PAPER, CARD = "#111111", "#F3EEE3", "#FFFFFF"
LIME, PINK, VIOLET, SUN = "#C8F23D", "#FF6FB1", "#7B61FF", "#FFD23F"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&family=JetBrains+Mono:wght@500;700&display=swap');

:root {{ --ink:{INK}; --paper:{PAPER}; --card:{CARD}; --lime:{LIME}; --pink:{PINK}; --violet:{VIOLET}; --sun:{SUN}; }}

html, body, .stApp {{ background: var(--paper); }}
.stApp {{
  background-image: radial-gradient(rgba(17,17,17,.13) 1.1px, transparent 1.1px);
  background-size: 22px 22px;
  font-family: 'Bricolage Grotesque', sans-serif; color: var(--ink);
}}
#MainMenu, footer, header[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {{ display:none !important; }}
.block-container {{ max-width: 880px; padding: 0 1.2rem 5rem !important; }}
::selection {{ background: var(--lime); color: var(--ink); }}

h1,h2,h3,h4 {{ font-family:'Bricolage Grotesque',sans-serif !important; letter-spacing:-.03em; color:var(--ink); }}
.mono {{ font-family:'JetBrains Mono',monospace; }}

/* ── ticker ── */
.ticker {{ margin: 0 calc(50% - 50vw) 2.2rem; width:100vw; background: var(--ink); color: var(--lime); overflow:hidden;
  border-bottom: 3px solid var(--ink); white-space:nowrap; }}
.ticker > div {{ display:inline-block; padding:.55rem 0; animation: tick 28s linear infinite;
  font: 700 .78rem 'JetBrains Mono',monospace; letter-spacing:.18em; }}
.ticker span {{ margin: 0 1.1rem; }} .ticker i {{ color: var(--pink); font-style:normal; }}
@keyframes tick {{ to {{ transform: translateX(-50%); }} }}

/* ── hero ── */
.brand {{ display:flex; align-items:center; gap:.6rem; font:800 1.25rem 'Bricolage Grotesque'; letter-spacing:-.03em; }}
.brand b {{ width:30px; height:30px; border-radius:50%; background: conic-gradient(var(--lime) 0 50%, var(--ink) 0);
  border:3px solid var(--ink); display:inline-block; animation: spin 6s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.hero h1 {{ font-size: clamp(2.8rem, 9vw, 5.4rem); line-height:.92; font-weight:800; margin: 1.6rem 0 .6rem; }}
.hero h1 em {{ font-style:normal; background: var(--lime); padding: 0 .18em; border:3px solid var(--ink);
  display:inline-block; transform: rotate(-2deg); box-shadow: 5px 5px 0 var(--ink); }}
.hero h1 u {{ text-decoration: none; background: linear-gradient(transparent 62%, var(--pink) 62% 92%, transparent 92%); }}
.hero p {{ font: 500 1.05rem 'JetBrains Mono',monospace; opacity:.7; margin: 0 0 1.8rem; }}

/* ── input ── */
.st-key-ask [data-testid="stForm"] {{ border:0; padding:0; background:transparent; }}
.st-key-ask [data-testid="stTextInput"] input {{
  font: 700 1.3rem 'Bricolage Grotesque'; padding: 1.15rem 1.2rem; height:auto; color:var(--ink);
  background: var(--card); border: 3px solid var(--ink); border-radius: 14px; box-shadow: 6px 6px 0 var(--ink);
  transition: transform .12s, box-shadow .12s; }}
.st-key-ask [data-testid="stTextInput"] input:focus {{ transform: translate(-2px,-2px); box-shadow: 9px 9px 0 var(--violet);
  border-color: var(--ink); outline:none; }}
.st-key-ask [data-testid="stTextInput"] input::placeholder {{ color: rgba(17,17,17,.35); }}
.st-key-ask [data-testid="stTextInput"] > div, .st-key-ask [data-baseweb="input"], .st-key-ask [data-baseweb="base-input"]
  {{ background: transparent !important; border:0 !important; box-shadow:none !important; }}
.st-key-ask [data-testid="InputInstructions"] {{ display:none; }}

.st-key-ask [data-testid="stTextInputRootElement"], .st-key-ask [data-baseweb="input"], .st-key-ask [data-baseweb="base-input"]
  {{ height:auto !important; min-height:0 !important; overflow:visible !important; border:0 !important; background:transparent !important; }}
.st-key-ask [data-testid="stTextInput"] {{ padding: 4px 8px 10px 0; }}
.stButton button p, .stFormSubmitButton button p, .stDownloadButton button p {{ font: inherit !important; margin:0; }}
.stFormSubmitButton button p {{ font-size:1.3rem !important; }}
.st-key-chips [data-testid="stColumn"] {{ min-width:0; }}

/* ── buttons ── */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {{
  font: 800 1.05rem 'Bricolage Grotesque'; letter-spacing:-.01em; border: 3px solid var(--ink); border-radius: 12px;
  padding: .75rem 1.4rem; box-shadow: 4px 4px 0 var(--ink); transition: transform .1s, box-shadow .1s; }}
.stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {{
  transform: translate(-2px,-2px); box-shadow: 6px 6px 0 var(--ink); border-color: var(--ink); }}
.stButton button:active, .stFormSubmitButton button:active, .stDownloadButton button:active {{
  transform: translate(3px,3px); box-shadow: 1px 1px 0 var(--ink); }}
.stFormSubmitButton button, .stButton button[kind="primary"] {{ background: var(--lime); color: var(--ink); width:100%; margin-top:.9rem; }}
.stFormSubmitButton button:hover, .stButton button[kind="primary"]:hover {{ background: var(--sun); color:var(--ink); }}
.stDownloadButton button, .stButton button[kind="secondary"] {{ background: var(--card); color: var(--ink); }}

.st-key-chips button {{ font: 700 .86rem 'JetBrains Mono',monospace; padding:.45rem .9rem; border-width:2px; border-radius:999px;
  box-shadow: 3px 3px 0 var(--ink); background: var(--card); width:100%; }}
.st-key-chips button:nth-of-type(1):hover {{ background: var(--pink); }}
.st-key-chips [data-testid="stColumn"]:nth-child(1) button:hover {{ background: var(--pink); }}
.st-key-chips [data-testid="stColumn"]:nth-child(2) button:hover {{ background: var(--sun); }}
.st-key-chips [data-testid="stColumn"]:nth-child(3) button:hover {{ background: var(--lime); }}
.hint {{ font: 700 .72rem 'JetBrains Mono'; letter-spacing:.16em; text-transform:uppercase; opacity:.55; margin: 2rem 0 .6rem; }}

/* ── pipeline cards ── */
.pipe {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 1.2rem 0; }}
@media (max-width: 720px) {{ .pipe {{ grid-template-columns: 1fr 1fr; }} }}
.node {{ position:relative; background: var(--card); border:3px solid var(--ink); border-radius:16px; padding:1rem .95rem 1.05rem;
  box-shadow: 5px 5px 0 var(--ink); overflow:hidden; transition: all .25s; min-height: 150px; }}
.node .n {{ font: 700 .72rem 'JetBrains Mono'; letter-spacing:.14em; opacity:.5; }}
.node svg {{ width:34px; height:34px; margin: .55rem 0 .5rem; display:block; stroke: var(--ink); fill:none; stroke-width:2.4;
  stroke-linecap:round; stroke-linejoin:round; }}
.node h4 {{ font-size:1.25rem; font-weight:800; margin:0; line-height:1; }}
.node p {{ font: 500 .78rem 'JetBrains Mono'; margin:.35rem 0 0; opacity:.7; }}
.node .tag {{ position:absolute; top:.7rem; right:.7rem; font:700 .66rem 'JetBrains Mono'; padding:.15rem .45rem;
  border:2px solid var(--ink); border-radius:999px; background:var(--card); }}
.pipe.idle .node:nth-child(1) {{ transform: rotate(-1.6deg); }} .pipe.idle .node:nth-child(2) {{ transform: rotate(1.2deg) translateY(6px); }}
.pipe.idle .node:nth-child(3) {{ transform: rotate(-.8deg); }}  .pipe.idle .node:nth-child(4) {{ transform: rotate(1.8deg) translateY(4px); }}
.pipe.idle .node:nth-child(1) {{ background: var(--lime); }} .pipe.idle .node:nth-child(2) {{ background: var(--sun); }}
.pipe.idle .node:nth-child(3) {{ background: var(--pink); }} .pipe.idle .node:nth-child(4) {{ background: #B9AEFF; }}
.pipe.idle .node:hover {{ transform: rotate(0) translateY(-5px); box-shadow: 8px 10px 0 var(--ink); }}

.node.wait {{ background: transparent; border-style: dashed; box-shadow:none; opacity:.55; }}
.node.live {{ background: var(--sun); transform: translate(-3px,-3px); box-shadow: 8px 8px 0 var(--ink); animation: bob 1.1s ease-in-out infinite; }}
.node.live::after {{ content:""; position:absolute; left:0; bottom:0; height:7px; width:40%; background: var(--ink);
  animation: slide 1.1s ease-in-out infinite; }}
.node.done {{ background: var(--lime); }}
.node.done .tag {{ background: var(--ink); color: var(--lime); }}
.node.live .tag {{ background: var(--ink); color: var(--sun); animation: blink .8s steps(2) infinite; }}
.node.fail {{ background: var(--pink); }}
@keyframes bob {{ 50% {{ transform: translate(-3px,-7px); }} }}
@keyframes slide {{ 0% {{ left:-40%; }} 100% {{ left:100%; }} }}
@keyframes blink {{ 50% {{ opacity:.25; }} }}

.say {{ font: 800 clamp(1.5rem,5vw,2.2rem) 'Bricolage Grotesque'; letter-spacing:-.03em; margin:.4rem 0 1.4rem; }}
.say .topic {{ background: var(--lime); border:3px solid var(--ink); padding:0 .3em; border-radius:10px; box-decoration-break:clone; -webkit-box-decoration-break:clone; }}
.dots span {{ animation: blink 1.2s infinite; }} .dots span:nth-child(2) {{ animation-delay:.2s; }} .dots span:nth-child(3) {{ animation-delay:.4s; }}

/* ── result ── */
.score {{ width:150px; height:150px; flex:none; display:flex; flex-direction:column; align-items:center; justify-content:center;
  border:4px solid var(--ink); border-radius: 50% 44% 52% 46% / 46% 52% 44% 50%; box-shadow:6px 6px 0 var(--ink);
  transform: rotate(-8deg); animation: pop .6s cubic-bezier(.2,1.6,.4,1); }}
.score b {{ font: 800 3.4rem/1 'Bricolage Grotesque'; letter-spacing:-.06em; }}
.score span {{ font: 700 .7rem 'JetBrains Mono'; letter-spacing:.15em; }}
@keyframes pop {{ from {{ transform: rotate(-30deg) scale(.2); opacity:0; }} }}
.verdict {{ display:flex; gap:1.6rem; align-items:center; margin: .6rem 0 1.8rem; }}
.verdict q {{ font: 800 clamp(1.3rem,4vw,1.9rem)/1.1 'Bricolage Grotesque'; letter-spacing:-.03em; quotes:none; }}
.verdict small {{ display:block; font:700 .72rem 'JetBrains Mono'; letter-spacing:.16em; opacity:.5; margin-bottom:.4rem; }}

.st-key-paper {{ background: var(--card); border:3px solid var(--ink); border-radius: 6px; box-shadow: 8px 8px 0 var(--ink);
  padding: 2rem 2.2rem; margin: .4rem 0 1.6rem; position:relative; }}
.st-key-paper::before {{ content:"REPORT"; position:absolute; top:-15px; left:20px; background:var(--violet); color:#fff;
  font:700 .72rem 'JetBrains Mono'; letter-spacing:.2em; padding:.25rem .7rem; border:3px solid var(--ink); }}
.st-key-paper h1, .st-key-paper h2 {{ font-size:1.7rem; font-weight:800; margin-top:1.4rem; border-bottom:3px solid var(--ink); padding-bottom:.2rem; }}
.st-key-paper h3 {{ font-size:1.2rem; font-weight:800; }}
.st-key-paper p, .st-key-paper li {{ font-size:1.02rem; line-height:1.65; font-family:'Bricolage Grotesque'; }}
.st-key-paper a {{ color: var(--violet); font-weight:700; }}

.two {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:1.6rem; }}
@media (max-width:720px) {{ .two {{ grid-template-columns:1fr; }} }}
.box {{ border:3px solid var(--ink); border-radius:14px; padding:1rem 1.2rem; box-shadow:5px 5px 0 var(--ink); }}
.box h5 {{ font:800 1.1rem 'Bricolage Grotesque'; margin:0 0 .5rem; }}
.box ul {{ margin:0; padding-left:1.1rem; }} .box li {{ margin:.3rem 0; font-size:.95rem; line-height:1.4; }}
.box.good {{ background: var(--lime); }} .box.fix {{ background: var(--pink); }}

.chips {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:1.8rem; }}
.chips a {{ font:700 .8rem 'JetBrains Mono'; color:var(--ink) !important; text-decoration:none; padding:.45rem .8rem; background:var(--card);
  border:2px solid var(--ink); border-radius:999px; box-shadow:3px 3px 0 var(--ink); transition: all .1s; }}
.chips a:hover {{ transform: translate(-2px,-2px); box-shadow:5px 5px 0 var(--ink); background:var(--sun); }}
.chips a::after {{ content:" ↗"; }}
.h {{ font:800 1.5rem 'Bricolage Grotesque'; letter-spacing:-.03em; margin: 1.6rem 0 .8rem; }}

/* ── tabs / expander ── */
[data-testid="stExpander"] {{ border:3px solid var(--ink); border-radius:14px; background:var(--card); box-shadow:5px 5px 0 var(--ink); }}
[data-testid="stExpander"] summary {{ font:800 1rem 'Bricolage Grotesque'; }}
[data-testid="stExpander"] pre, [data-testid="stExpander"] code {{ font-family:'JetBrains Mono' !important; font-size:.78rem !important; }}

/* ── error ── */
.oops {{ background: var(--pink); border:3px solid var(--ink); border-radius:16px; box-shadow:7px 7px 0 var(--ink); padding:1.4rem 1.6rem; margin:1rem 0 1.6rem; }}
.oops h3 {{ font-size:2rem; margin:0 0 .3rem; }} .oops code {{ display:block; background:var(--ink); color:var(--lime); padding:.7rem .9rem;
  border-radius:8px; font:500 .78rem 'JetBrains Mono'; word-break:break-word; margin-top:.8rem; }}
</style>
"""

ICONS = {
    "scout": '<svg viewBox="0 0 24 24"><circle cx="10" cy="10" r="6.5"/><path d="M15 15l6 6"/></svg>',
    "reader": '<svg viewBox="0 0 24 24"><path d="M3 5.5c3-1.5 6-1.5 9 0v14c-3-1.5-6-1.5-9 0zM21 5.5c-3-1.5-6-1.5-9 0v14c3-1.5 6-1.5 9 0z"/></svg>',
    "writer": '<svg viewBox="0 0 24 24"><path d="M4 20l1-5L16.5 3.5a2.1 2.1 0 013 3L8 18z"/><path d="M14 6l3 3"/></svg>',
    "critic": '<svg viewBox="0 0 24 24"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></svg>',
}
STAGES = [
    ("scout", "Scout", "finds sources"),
    ("reader", "Reader", "digs into the best one"),
    ("writer", "Writer", "drafts the report"),
    ("critic", "Critic", "scores it. harshly."),
]
LIVE_LINES = [
    "Scouring the web", "Reading the fine print", "Putting it into words", "Sharpening the red pen",
]
EXAMPLES = [
    "Is nuclear fusion finally close?",
    "How do AI agents actually work?",
    "Future of electric aviation",
]


# ───────────────────────────── helpers ─────────────────────────────
def pipe_html(states: list[str], times: list[float | None], mode: str = "") -> str:
    tags = {"wait": "WAITING", "live": "WORKING", "done": "DONE", "fail": "FAILED"}
    out = [f'<div class="pipe {mode}">']
    for i, ((key, name, desc), s) in enumerate(zip(STAGES, states)):
        tag = tags[s] if not (s == "done" and times[i] is not None) else f"{times[i]:.0f}s ✓"
        tag_html = f'<div class="tag">{tag}</div>' if mode != "idle" else ""
        out.append(
            f'<div class="node {s if mode != "idle" else ""}"><div class="n">0{i+1}</div>{ICONS[key]}'
            f"<h4>{name}</h4><p>{desc}</p>{tag_html}</div>"
        )
    return "".join(out) + "</div>"


def parse_critic(text: str) -> dict:
    score = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", text)
    def block(start, end):
        m = re.search(start + r"\s*:?\s*(.*?)" + end, text, re.S | re.I)
        return re.findall(r"^\s*[-•*]\s*(.+)$", m.group(1), re.M) if m else []
    verdict = re.search(r"One line verdict:?\s*(.+)", text, re.S | re.I)
    return {
        "score": float(score.group(1)) if score else None,
        "good": block("Strengths", r"(?:Areas to Improve|One line verdict|$)"),
        "fix": block("Areas to Improve", r"(?:One line verdict|$)"),
        "verdict": verdict.group(1).strip().strip('"') if verdict else "",
    }


def parse_sources(text: str) -> list[tuple[str, str]]:
    seen, out = set(), []
    for u in re.findall(r"https?://[^\s)\]>\"']+", text):
        u = u.rstrip(".,;:")
        if u not in seen:
            seen.add(u)
            out.append((urlparse(u).netloc.removeprefix("www.") or u, u))
    return out


def start(topic: str):
    topic = (topic or "").strip()
    if topic:
        st.session_state.update(topic=topic, phase="running", result=None, error=None)


def reset():
    st.session_state.update(phase="idle", result=None, error=None, topic="")


def ticker() -> str:
    words = ["SEARCH", "READ", "WRITE", "CRITIQUE"] * 2
    seq = "".join(f"<span>{w}</span><i>●</i>" for w in words) * 2
    return f'<div class="ticker"><div>{seq}{seq}</div></div>'


# ───────────────────────────── state & chrome ─────────────────────────────
st.session_state.setdefault("phase", "idle")
st.session_state.setdefault("topic", "")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown(ticker(), unsafe_allow_html=True)
st.markdown('<div class="brand"><b></b>dig.</div>', unsafe_allow_html=True)
phase = st.session_state.phase

# one root container per run: swapping phases clears the previous screen instantly
with st.empty().container():


    # ───────────────────────────── IDLE ─────────────────────────────
    if phase == "idle":
        st.markdown(
            '<div class="hero"><h1>Ask once.<br>Four agents <em>dig</em>.<br>Get <u>one</u> report.</h1>'
            "<p>// search → read → write → critique</p></div>",
            unsafe_allow_html=True,
        )
        with st.container(key="ask"):
            with st.form("ask_form", border=False):
                t = st.text_input("topic", key="topic_input", placeholder="What do you want to know?", label_visibility="collapsed")
                go = st.form_submit_button("Dig it up  →", use_container_width=True,
                                           on_click=lambda: start(st.session_state.get("topic_input", "")))
            if go and not t.strip():
                if True:
                    st.markdown('<div class="mono" style="margin-top:.6rem;color:#d6246e;font-weight:700">↑ type something first</div>', unsafe_allow_html=True)

        st.markdown('<div class="hint">or try one</div>', unsafe_allow_html=True)
        with st.container(key="chips"):
            cols = st.columns(3)
            for c, ex in zip(cols, EXAMPLES):
                c.button(ex, key=f"ex_{ex}", on_click=start, args=(ex,))

        st.markdown('<div class="hint">how it works</div>', unsafe_allow_html=True)
        st.markdown(pipe_html(["wait"] * 4, [None] * 4, "idle"), unsafe_allow_html=True)


    # ───────────────────────────── RUNNING ─────────────────────────────
    elif phase == "running":
        topic = st.session_state.topic
        st.markdown(
            f'<div class="say">Digging into <span class="topic">{topic.replace("<", "&lt;")}</span>'
            '<span class="dots"><span>.</span><span>.</span><span>.</span></span></div>',
            unsafe_allow_html=True,
        )
        slot, line = st.empty(), st.empty()
        states, times, t0 = ["wait"] * 4, [None] * 4, [0.0]

        def paint(live_idx=None):
            slot.markdown(pipe_html(states, times), unsafe_allow_html=True)
            if live_idx is not None:
                line.markdown(f'<div class="hint">{LIVE_LINES[live_idx]}…</div>', unsafe_allow_html=True)

        def on_stage(i, status):
            if status == "start":
                states[i], t0[0] = "live", time.time()
                paint(i)
            else:
                states[i], times[i] = "done", time.time() - t0[0]
                paint()

        paint(0)
        try:
            from pipeline import run_research_pipeline

            result = run_research_pipeline(topic, on_stage=on_stage)
            st.session_state.update(result=result, times=times, phase="done")
        except Exception as e:  # surfaced in UI, not swallowed
            logging.getLogger("app").exception("Research run failed for topic %r", topic)
            live = states.index("live") if "live" in states else 0
            states[live] = "fail"
            paint()
            st.session_state.update(error=f"{type(e).__name__}: {e}", phase="error")
        line.empty()
        st.rerun()


    # ───────────────────────────── ERROR ─────────────────────────────
    elif phase == "error":
        err = str(st.session_state.error).replace("<", "&lt;")
        st.markdown(
            f'<div class="oops"><h3>Well, that broke.</h3><div class="mono" style="font-size:.9rem">An agent tripped. Check your keys &amp; connection, then retry.</div><code>{err}</code></div>',
            unsafe_allow_html=True,
        )
        a, b = st.columns(2)
        a.button("Retry", type="primary", use_container_width=True, on_click=start, args=(st.session_state.topic,))
        b.button("New topic", use_container_width=True, on_click=reset)


    # ───────────────────────────── DONE ─────────────────────────────
    else:
        r = st.session_state.result
        topic = st.session_state.topic
        crit = parse_critic(r["feedback"])
        sc = crit["score"]
        bg = LIME if sc is None or sc >= 8 else SUN if sc >= 5 else PINK
        total = sum(t or 0 for t in st.session_state.get("times", []))

        st.markdown(
            f'<div class="say">Done. <span class="topic">{topic.replace("<", "&lt;")}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(pipe_html(["done"] * 4, st.session_state.get("times", [None] * 4)), unsafe_allow_html=True)

        if sc is not None or crit["verdict"]:
            badge = (
                f'<div class="score" style="background:{bg}"><b>{sc:g}</b><span>OUT OF 10</span></div>' if sc is not None else ""
            )
            st.markdown(
                f'<div class="verdict">{badge}<div><small>THE CRITIC SAYS · {total:.0f}s TOTAL</small>'
                f'<q>{crit["verdict"].replace("<", "&lt;") or "No verdict given."}</q></div></div>',
                unsafe_allow_html=True,
            )

        with st.container(key="paper"):
            st.markdown(r["report"])

        if crit["good"] or crit["fix"]:
            li = lambda xs: "".join(f"<li>{x.replace('<', '&lt;')}</li>" for x in xs)
            st.markdown(
                f'<div class="two"><div class="box good"><h5>Nailed it</h5><ul>{li(crit["good"])}</ul></div>'
                f'<div class="box fix"><h5>Needs work</h5><ul>{li(crit["fix"])}</ul></div></div>',
                unsafe_allow_html=True,
            )

        srcs = parse_sources(r["report"])
        if srcs:
            st.markdown('<div class="h">Sources</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="chips">' + "".join(f'<a href="{u}" target="_blank" rel="noopener">{d}</a>' for d, u in srcs) + "</div>",
                unsafe_allow_html=True,
            )

        with st.expander("Behind the scenes"):
            st.caption("SCOUT")
            st.code(r["search_results"], language=None)
            st.caption("READER")
            st.code(r["scraped_content"], language=None)

        st.write("")
        a, b = st.columns(2)
        a.download_button(
            "Save as .md",
            data=f"# {topic}\n\n{r['report']}\n\n---\n\n## Critic\n\n{r['feedback']}\n",
            file_name=re.sub(r"\W+", "-", topic.lower()).strip("-")[:50] + ".md",
            mime="text/markdown",
            use_container_width=True,
        )
        b.button("Dig something else", type="primary", use_container_width=True, on_click=reset)
