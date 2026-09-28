import ast
import hashlib
import html
import os
import random
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Reel Mood", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

PAGE = 30
REEL_W, REEL_G = 120, 14
SORTS = ["Top rated", "Most voted", "Newest", "Oldest", "Title A-Z", "Hidden gems"]

MOODS = {
    "cozy": {"emoji": "🕯️", "tag": "blanket, snacks, zero stress.", "genres": ["Family", "Animation", "Romance"]},
    "heavy": {"emoji": "🌧️", "tag": "for when you need to feel something.", "genres": ["Drama"]},
    "hyped": {"emoji": "⚡", "tag": "adrenaline, no brakes.", "genres": ["Action"]},
    "laugh": {"emoji": "😂", "tag": "pure, uncomplicated fun.", "genres": ["Comedy"]},
    "spooked": {"emoji": "🕷️", "tag": "lights off, volume up.", "genres": ["Horror"]},
    "curious": {"emoji": "🪐", "tag": "stories that mess with your head.", "genres": ["Science Fiction", "Mystery"]},
}

LANGS = {
    "en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam",
    "kn": "Kannada", "bn": "Bengali", "mr": "Marathi", "pa": "Punjabi", "ko": "Korean",
    "ja": "Japanese", "zh": "Chinese", "cn": "Cantonese", "fr": "French", "es": "Spanish",
    "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian", "tr": "Turkish",
    "th": "Thai", "ar": "Arabic", "fa": "Persian", "sv": "Swedish", "da": "Danish",
    "nl": "Dutch", "pl": "Polish", "he": "Hebrew", "id": "Indonesian", "vi": "Vietnamese",
}

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Grotesk:wght@400;500;600&display=swap');
:root{--ink:#f2eefc;--dim:#a79cc6;--acc1:#ffb454;--acc2:#ff5d73}
html,body{background:#0a0912!important}
.stApp{background:transparent!important;isolation:isolate;font-family:'Space Grotesk',sans-serif;color:var(--ink)}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{background:transparent!important}
[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu{display:none!important}
.block-container{max-width:1180px;padding-top:3rem!important}

.wall{position:fixed;inset:0;z-index:-1;display:flex;gap:14px;padding:0 14px;overflow:hidden;pointer-events:none;opacity:.6}
.wall::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,9,18,.9) 0%,rgba(10,9,18,.55) 35%,rgba(10,9,18,.85) 100%)}
.wall .col{flex:1;display:flex;flex-direction:column;gap:14px;animation:drift 120s linear infinite}
.wall .col:nth-child(even){animation-direction:reverse;animation-duration:150s}
.wall img{width:100%;display:block;border-radius:8px}
@keyframes drift{from{transform:translateY(0)}to{transform:translateY(-50%)}}

.hero{padding:2rem 0 1rem}
.kicker{font-size:.78rem;letter-spacing:.32em;color:var(--acc1);text-transform:uppercase;margin-bottom:.4rem}
.brand{font-family:'Bebas Neue',sans-serif;font-size:clamp(4rem,11vw,8.5rem);line-height:.9;letter-spacing:.02em;background:linear-gradient(90deg,var(--acc1),var(--acc2));-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent}
.lead{max-width:34rem;color:var(--dim);font-size:1.05rem;margin:.9rem 0 0}
.tag{color:var(--dim);font-style:italic;margin:.4rem 0 1.2rem}
.count{color:var(--dim);font-size:.85rem;letter-spacing:.04em;margin:1.4rem 0 .9rem}
.foot{color:#6f6590;font-size:.75rem;text-align:center;margin:3rem 0 1rem}

button[data-testid^="stBaseButton-pills"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.16)!important;border-radius:999px!important;padding:.35rem 1.1rem!important;transition:all .2s}
button[data-testid^="stBaseButton-pills"] p{color:#e9e3fb!important;font-size:.95rem!important}
button[data-testid^="stBaseButton-pills"]:hover{border-color:var(--acc1)!important}
button[data-testid="stBaseButton-pillsActive"]{background:linear-gradient(90deg,var(--acc1),var(--acc2))!important;border-color:transparent!important}
button[data-testid="stBaseButton-pillsActive"] p{color:#1a1020!important;font-weight:600!important}
[data-testid="stWidgetLabel"] p{color:var(--dim)!important;font-size:.75rem!important;letter-spacing:.12em;text-transform:uppercase}
div[data-baseweb="select"]>div{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.16)!important;border-radius:12px!important}
div[data-baseweb="select"] *{color:var(--ink)!important}
div[data-baseweb="popover"] ul{background:#171420!important}
div[data-baseweb="popover"] li{background:#171420!important;color:var(--ink)!important}
div[data-baseweb="popover"] li:hover{background:#2a2140!important}
button[data-testid="stBaseButton-secondary"]{width:100%;background:transparent!important;border:1px solid rgba(255,255,255,.28)!important;border-radius:999px!important}
button[data-testid="stBaseButton-secondary"] p{color:var(--ink)!important}
button[data-testid="stBaseButton-secondary"]:hover{border-color:var(--acc1)!important}

.st-key-grid{display:grid!important;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:26px 20px!important}
.st-key-grid>*{min-width:0}
[class*="st-key-card_"],[class*="st-key-row_"]{position:relative;gap:0!important}
[class*="st-key-card_"] [data-testid="stButton"],[class*="st-key-row_"] [data-testid="stButton"]{position:absolute;inset:0;z-index:5}
[class*="st-key-card_"] button,[class*="st-key-row_"] button{width:100%;height:100%;min-height:0;opacity:0;cursor:pointer}
.tile{display:block}
.poster{position:relative;aspect-ratio:2/3;border-radius:14px;overflow:hidden;background:linear-gradient(160deg,#2b2145,#150f22);box-shadow:0 10px 28px rgba(0,0,0,.55);transition:transform .25s ease,box-shadow .25s ease}
[class*="st-key-card_"]:hover .poster{transform:translateY(-8px) scale(1.03);box-shadow:0 18px 42px rgba(255,93,115,.3)}
.poster img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.ph{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:14px;text-align:center;font-family:'Bebas Neue',sans-serif;font-size:1.6rem;line-height:1.05;color:#b9addd}
.badge{position:absolute;top:10px;left:10px;padding:3px 10px;border-radius:999px;background:rgba(10,9,18,.78);color:var(--acc1);font-size:.78rem;font-weight:600;backdrop-filter:blur(6px)}
.over{position:absolute;left:0;right:0;bottom:0;padding:44px 12px 12px;display:flex;justify-content:space-between;align-items:center;background:linear-gradient(0deg,rgba(6,5,12,.96),rgba(6,5,12,0));opacity:0;transition:opacity .25s ease;font-size:.8rem;color:#d9d1f2}
[class*="st-key-card_"]:hover .over{opacity:1}
.over b{color:var(--acc1)}
.cap{padding:.65rem .15rem 0}
.cap .t{font-weight:600;font-size:.95rem;line-height:1.25;color:var(--ink)}
.cap .m{font-size:.8rem;color:var(--dim);margin-top:2px}
div[role="dialog"]{background:#120f1c!important;border:1px solid rgba(255,255,255,.12)!important;border-radius:18px!important;color:var(--ink)}
div[role="dialog"] h2{font-family:'Bebas Neue',sans-serif!important;font-size:2.4rem!important;letter-spacing:.03em;color:var(--ink)!important}
div[role="dialog"] [data-testid="stMarkdownContainer"]{color:var(--ink)}
div[role="dialog"] button[aria-label="Close"],div[role="dialog"] button[aria-label="Close"] svg{color:var(--ink)!important;fill:var(--ink)!important}
.dlg{display:flex;gap:24px;flex-wrap:wrap}
.dposter{width:210px;flex:none}
.dinfo{flex:1;min-width:240px}
.dmeta{color:var(--dim);font-size:.9rem}
.dscore{color:var(--acc1);font-weight:600;font-size:1.1rem;margin:.3rem 0 .6rem}
.dscore span{color:var(--dim);font-weight:400;font-size:.8rem}
.dtag{color:var(--dim);font-style:italic;margin-bottom:.6rem}
.dh{font-family:'Bebas Neue',sans-serif;font-size:1.5rem;letter-spacing:.06em;color:var(--acc1);margin:1rem 0 .3rem}
.story{color:#dcd5f0;line-height:1.6;font-size:.98rem}
.imdbbtn{display:inline-block;margin-top:1rem;padding:.5rem 1.2rem;border-radius:999px;background:linear-gradient(90deg,var(--acc1),var(--acc2));color:#1a1020!important;font-weight:600;text-decoration:none!important}
.cast{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:16px}
.cm{text-align:center}
.av{position:relative;width:76px;height:76px;margin:0 auto 6px;border-radius:50%;overflow:hidden;background:linear-gradient(160deg,#3a2c5e,#1a1428);display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:#b9addd}
.av img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cn{font-weight:600;font-size:.85rem;line-height:1.2;color:var(--ink)}
.cc{font-size:.75rem;color:var(--dim);line-height:1.2}
.tk{font-size:.75rem;letter-spacing:.3em;text-transform:uppercase;color:var(--acc1);text-align:center;margin-top:.4rem}
.reel{position:relative;overflow:hidden;padding:26px 0;-webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.strip{position:relative;left:50%;display:flex;gap:14px;width:max-content}
.ri{flex:none;width:120px}
.mark{position:absolute;left:50%;top:8px;bottom:8px;border-left:2px solid rgba(255,180,84,.7);z-index:2}
.reveal{opacity:0;text-align:center;margin-bottom:1rem}
.rt{font-family:'Bebas Neue',sans-serif;font-size:2.6rem;letter-spacing:.04em;line-height:1}
.rm{color:var(--dim);margin:.3rem 0 .6rem}
.rs{max-width:40rem;margin:0 auto;color:#dcd5f0;line-height:1.55}
[data-testid="stSidebar"]{background:rgba(12,10,20,.95)!important;border-right:1px solid rgba(255,255,255,.08)}
[data-testid="stSidebar"] [role="radiogroup"] p,[data-testid="stSidebar"] [data-testid="stThumbValue"],[data-testid="stSidebar"] [data-testid="stTickBarMin"],[data-testid="stSidebar"] [data-testid="stTickBarMax"]{color:var(--ink)!important}
div[data-baseweb="input"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.16)!important;border-radius:12px!important}
div[data-baseweb="input"] input{color:var(--ink)!important;background:transparent!important}
span[data-baseweb="tag"]{background:linear-gradient(90deg,#ffb454,#ff5d73)!important}
span[data-baseweb="tag"] *{color:#1a1020!important}
button[data-testid^="stBaseButton-segmented_control"]{background:rgba(255,255,255,.06)!important;border:1px solid rgba(255,255,255,.16)!important}
button[data-testid^="stBaseButton-segmented_control"] p{color:#e9e3fb!important}
button[data-testid="stBaseButton-segmented_controlActive"]{background:linear-gradient(90deg,var(--acc1),var(--acc2))!important;border-color:transparent!important}
button[data-testid="stBaseButton-segmented_controlActive"] p{color:#1a1020!important;font-weight:600!important}
.sbt{font-family:'Bebas Neue',sans-serif;font-size:1.7rem;letter-spacing:.06em;color:var(--acc1)}
.fbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:10px 14px;margin:.4rem 0 1rem}
.fl{font-weight:600;margin-right:6px}
.chip{background:rgba(255,180,84,.14);color:var(--acc1);border:1px solid rgba(255,180,84,.35);border-radius:999px;padding:2px 12px;font-size:.85rem}
.none{color:var(--dim);font-size:.85rem}
.lhead,.lrow{display:grid;grid-template-columns:64px 64px minmax(0,1fr) 110px 150px;gap:14px;align-items:center;padding:10px 12px}
.lhead{color:var(--dim);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,.12)}
.lrow{border-bottom:1px solid rgba(255,255,255,.07);transition:background .2s}
[class*="st-key-row_"]:hover .lrow{background:rgba(255,180,84,.09)}
.lth .poster{width:52px;border-radius:6px;box-shadow:none}
.lth .ph{display:none}
.ly,.ll{color:var(--dim);font-size:.9rem}
.ltt{font-weight:600}
.lg{color:var(--dim);font-size:.8rem;margin-top:2px}
.stars{color:var(--acc1);letter-spacing:.1em}
.st-key-list{gap:0!important}
.rh{color:var(--dim);font-size:.8rem;margin-top:.6rem;letter-spacing:.06em}
.st-key-reelwrap{position:relative;gap:0!important}
.st-key-reelwrap [data-testid="stButton"]{position:absolute;left:50%;top:22px;width:132px;height:190px;margin-left:-66px;z-index:6}
.st-key-reelwrap button{width:100%;height:100%;min-height:0;opacity:0;cursor:pointer}
.st-key-spin button{background:linear-gradient(90deg,#ffb454,#ff5d73)!important;border:none!important}
.st-key-spin button p{color:#1a1020!important;font-weight:700!important}
</style>"""


def get_genre_names(genre_str):
    try:
        return [g["name"] for g in ast.literal_eval(genre_str)]
    except (ValueError, SyntaxError, TypeError):
        return []


@st.cache_data
def load_data():
    df = pd.read_csv("movies_metadata.csv", low_memory=False)
    for col in ["vote_average", "vote_count", "runtime"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["title", "vote_average", "vote_count"])
    df = df[df["vote_count"] > 0]
    df = df.drop_duplicates(subset=["title", "release_date"])
    df["genre_list"] = df["genres"].apply(get_genre_names)
    df["mid"] = pd.to_numeric(df["id"], errors="coerce")
    df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    # weighted rating: pulls low-vote movies toward the global average
    m = 50
    C = df["vote_average"].mean()
    v, R = df["vote_count"], df["vote_average"]
    df["score"] = v / (v + m) * R + m / (v + m) * C
    return df


@st.cache_data
def get_genres(_df):
    return sorted({g for gl in _df["genre_list"] for g in gl})


def stars(avg):
    n = max(0, min(5, round(avg / 2)))
    return "★" * n + "☆" * (5 - n)


def row_html(row):
    title = html.escape(str(row["title"]))
    year = str(int(row["year"])) if pd.notna(row["year"]) else "n/a"
    lang = LANGS.get(row["original_language"], str(row["original_language"]).upper())
    genres = html.escape(", ".join(row["genre_list"][:3]))
    pp = row["poster_path"]
    img = f'<img src="https://image.tmdb.org/t/p/w92{pp}" alt="" loading="lazy">' if isinstance(pp, str) and pp else ""
    return (
        f'<div class="lrow"><div class="lth"><div class="poster"><div class="ph">{title}</div>{img}</div></div>'
        + f'<div class="ly">{year}</div><div><div class="ltt">{title}</div><div class="lg">{genres}</div></div>'
        + f'<div class="ll">{lang}</div><div><span class="stars">{stars(row["vote_average"])}</span> {row["vote_average"]:.1f}</div></div>'
    )


LIST_HEAD = '<div class="lhead"><div></div><div>Year</div><div>Title</div><div>Language</div><div>Rating</div></div>'


def chips_html(chips):
    body = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in chips)
    body = body or '<span class="none">none, showing everything</span>'
    return f'<div class="fbar"><span class="fl">Active filters</span>{body}</div>'


def build_wall(paths, ncols=8):
    cols = []
    for i in range(ncols):
        imgs = "".join(f'<img src="https://image.tmdb.org/t/p/w185{p}" alt="">' for p in paths[i::ncols])
        cols.append(f'<div class="col">{imgs}{imgs}</div>')
    return '<div class="wall">' + "".join(cols) + "</div>"


def card(row):
    title = html.escape(str(row["title"]))
    year = str(int(row["year"])) if pd.notna(row["year"]) else "n/a"
    lang = LANGS.get(row["original_language"], str(row["original_language"]).upper())
    rating = f'{row["vote_average"]:.1f}'
    pp = row["poster_path"]
    img = f'<img src="https://image.tmdb.org/t/p/w342{pp}" alt="" loading="lazy">' if isinstance(pp, str) and pp else ""
    return (
        f'<div class="tile"><div class="poster"><div class="ph">{title}</div>{img}'
        + f'<div class="badge">★ {rating}</div><div class="over"><span>{lang}</span><b>Story &amp; cast →</b></div></div>'
        + f'<div class="cap"><div class="t">{title}</div><div class="m">{year} · {lang}</div></div></div>'
    )


@st.cache_resource
def load_credits():
    cr = pd.read_csv("credits.csv", usecols=["id", "cast"])
    cr["id"] = pd.to_numeric(cr["id"], errors="coerce")
    cr = cr.dropna(subset=["id"]).drop_duplicates(subset="id")
    return dict(zip(cr["id"].astype(int), cr["cast"]))


def get_cast(movie_id, limit=12):
    if pd.isna(movie_id):
        return []
    raw = load_credits().get(int(movie_id))
    if not isinstance(raw, str):
        return []
    try:
        people = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return []
    people = sorted(people, key=lambda p: p.get("order", 999))
    return people[:limit]


def cast_html(people):
    out = []
    for p in people:
        name = str(p.get("name", ""))
        char = html.escape(str(p.get("character", "")))
        pp = p.get("profile_path")
        img = f'<img src="https://image.tmdb.org/t/p/w185{pp}" alt="">' if isinstance(pp, str) and pp else ""
        out.append(
            f'<div class="cm"><div class="av"><span>{html.escape(name[:1])}</span>{img}</div>'
            f'<div class="cn">{html.escape(name)}</div><div class="cc">{char}</div></div>'
        )
    return '<div class="cast">' + "".join(out) + "</div>"


def fmt_runtime(mins):
    if pd.isna(mins) or mins <= 0:
        return ""
    h, m = divmod(int(mins), 60)
    return f"{h}h {m}m" if h else f"{m}m"


def open_movie(idx):
    row = df.loc[idx]

    @st.dialog(str(row["title"]), width="large")
    def _view():
        title = html.escape(str(row["title"]))
        year = str(int(row["year"])) if pd.notna(row["year"]) else ""
        lang = LANGS.get(row["original_language"], str(row["original_language"]).upper())
        meta = " · ".join(x for x in [year, lang, fmt_runtime(row["runtime"]), ", ".join(row["genre_list"][:3])] if x)
        pp = row["poster_path"]
        img = f'<img src="https://image.tmdb.org/t/p/w342{pp}" alt="">' if isinstance(pp, str) and pp else ""
        story = " ".join(str(row["overview"]).split()) if pd.notna(row["overview"]) else ""
        story = html.escape(story or "No story available for this title.")
        tagline = " ".join(str(row["tagline"]).split()) if pd.notna(row["tagline"]) else ""
        tag_html = f'<div class="dtag">{html.escape(tagline)}</div>' if tagline else ""
        imdb = row["imdb_id"]
        btn = (
            f'<a class="imdbbtn" href="https://www.imdb.com/title/{imdb}/" target="_blank" rel="noopener">Open on IMDb ↗</a>'
            if isinstance(imdb, str) and imdb
            else ""
        )
        st.markdown(
            f'<div class="dlg"><div class="dposter"><div class="poster"><div class="ph">{title}</div>{img}</div></div>'
            f'<div class="dinfo"><div class="dmeta">{html.escape(meta)}</div>'
            f'<div class="dscore">★ {row["vote_average"]:.1f} <span>({int(row["vote_count"]):,} votes)</span></div>'
            f'{tag_html}<div class="dh">Story</div><div class="story">{story}</div>{btn}</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dh">Cast</div>', unsafe_allow_html=True)
        if not os.path.exists("credits.csv"):
            st.info("Put credits.csv (from the same Kaggle zip) in this folder to see the cast.")
        else:
            with st.spinner("Loading cast..."):
                people = get_cast(row["mid"])
            if people:
                st.markdown(cast_html(people), unsafe_allow_html=True)
            else:
                st.caption("Cast info isn't available for this title.")

    _view()


def reel_block(ids, win, name):
    end = -(win * (REEL_W + REEL_G) + REEL_W // 2)
    css = (
        f"<style>@keyframes roll_{name}{{to{{transform:translateX({end}px)}}}}"
        f"@keyframes glow_{name}{{to{{transform:scale(1.1);box-shadow:0 0 0 3px #ffb454,0 0 44px rgba(255,180,84,.6)}}}}"
        f"@keyframes fade_{name}{{to{{opacity:1}}}}"
        f".strip{{animation:roll_{name} 4.6s cubic-bezier(.15,.7,.15,1) forwards}}"
        f".ri.win .poster{{animation:glow_{name} 1s ease 4.6s both}}"
        f".reveal{{animation:fade_{name} .8s ease 4.8s forwards}}</style>"
    )
    items = []
    for n, i in enumerate(ids):
        r = df.loc[i]
        t = html.escape(str(r["title"]))
        cls = "ri win" if n == win else "ri"
        items.append(
            f'<div class="{cls}"><div class="poster"><div class="ph">{t}</div>'
            f'<img src="https://image.tmdb.org/t/p/w185{r["poster_path"]}" alt=""></div></div>'
        )
    return css + '<div class="reel"><div class="mark"></div><div class="strip">' + "".join(items) + "</div></div>"


def reveal_html(r):
    title = html.escape(str(r["title"]))
    year = str(int(r["year"])) if pd.notna(r["year"]) else "n/a"
    lang_name = LANGS.get(r["original_language"], str(r["original_language"]).upper())
    story = " ".join(str(r["overview"]).split()) if pd.notna(r["overview"]) else ""
    if len(story) > 220:
        story = story[:220].rsplit(" ", 1)[0] + "…"
    return (
        f'<div class="reveal"><div class="rt">{title}</div>'
        f'<div class="rm">{year} · {lang_name} · ★ {r["vote_average"]:.1f}</div>'
        f'<div class="rs">{html.escape(story)}</div>'
        f'<div class="rh">click the poster for story &amp; cast</div></div>'
    )


df = load_data()
GENRES = get_genres(df)
lang_opts = [c for c in df["original_language"].value_counts().index if c in LANGS]
YMIN, YMAX = int(df["year"].min()), min(int(df["year"].max()), 2026)

ss = st.session_state
ss.setdefault("mood", "cozy")
ss.setdefault("f_q", "")
ss.setdefault("f_genres", [g for g in MOODS["cozy"]["genres"] if g in GENRES])
ss.setdefault("f_mode", "Any of these")
ss.setdefault("f_years", (YMIN, YMAX))
ss.setdefault("f_rating", 0.0)
ss.setdefault("f_votes", 20)
ss.setdefault("f_langs", [])
ss.setdefault("f_sort", "Top rated")
ss.setdefault("spin_n", 0)
ss.setdefault("spin_seed", date.today().isoformat())


def apply_mood():
    m = st.session_state.get("mood")
    st.session_state["f_genres"] = [g for g in MOODS[m]["genres"] if g in GENRES] if m else []
    st.session_state["f_mode"] = "Any of these"


def do_spin():
    st.session_state["spin_n"] += 1
    st.session_state["spin_seed"] = str(random.random())


def genres_edited():
    st.session_state["mood"] = None


def clear_filters():
    s = st.session_state
    s["mood"] = None
    s["f_q"] = ""
    s["f_genres"] = []
    s["f_mode"] = "Any of these"
    s["f_years"] = (YMIN, YMAX)
    s["f_rating"] = 0.0
    s["f_votes"] = 20
    s["f_langs"] = []


st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sbt">Advanced search</div>', unsafe_allow_html=True)
    st.button("Clear all filters", key="clear_side", on_click=clear_filters)
    st.text_input("Title contains", key="f_q", placeholder="type to search titles")
    st.multiselect("Genres", GENRES, key="f_genres", on_change=genres_edited, placeholder="type to filter genres")
    st.radio("Genre match", ["Any of these", "All of these"], key="f_mode", horizontal=True)
    st.slider("Release year", YMIN, YMAX, key="f_years")
    st.slider("Minimum rating", 0.0, 10.0, step=0.5, key="f_rating")
    st.select_slider("Minimum votes", options=[0, 10, 20, 50, 100, 500, 1000], key="f_votes")
    st.multiselect(
        "Language", lang_opts, key="f_langs", format_func=lambda c: LANGS[c], placeholder="any language"
    )
    st.selectbox("Sort by", SORTS, key="f_sort")

st.markdown(
    '<div class="hero"><div class="kicker">Mood-based cinema</div><div class="brand">REEL MOOD</div>'
    '<p class="lead">Tell it how you feel, or search like a pro. Every language, every era.</p></div>',
    unsafe_allow_html=True,
)

st.pills(
    "Mood",
    list(MOODS),
    key="mood",
    on_change=apply_mood,
    format_func=lambda k: f"{MOODS[k]['emoji']}  {k.title()}",
    label_visibility="collapsed",
)
mood = ss["mood"]
sel, mode, q = ss["f_genres"], ss["f_mode"], ss["f_q"].strip()
years, min_rating, min_votes, langs, sort_by = ss["f_years"], ss["f_rating"], ss["f_votes"], ss["f_langs"], ss["f_sort"]

# ---- apply filters ----
f = df[df["vote_count"] >= min_votes]
if q:
    f = f[f["title"].str.contains(q, case=False, regex=False, na=False)]
if sel:
    check = all if mode == "All of these" else any
    f = f[f["genre_list"].apply(lambda g: check(x in g for x in sel))]
if langs:
    f = f[f["original_language"].isin(langs)]
if tuple(years) != (YMIN, YMAX):
    f = f[f["year"].between(years[0], years[1])]
if min_rating > 0:
    f = f[f["vote_average"] >= min_rating]

if sort_by == "Hidden gems":
    ranked = f[f["vote_count"].between(30, 400) & (f["vote_average"] >= 7)].sort_values("score", ascending=False)
elif sort_by == "Most voted":
    ranked = f.sort_values("vote_count", ascending=False)
elif sort_by == "Newest":
    ranked = f.sort_values(["year", "score"], ascending=False)
elif sort_by == "Oldest":
    ranked = f.sort_values(["year", "score"], ascending=[True, False])
elif sort_by == "Title A-Z":
    ranked = f.assign(_t=f["title"].str.lower()).sort_values("_t")
else:
    ranked = f.sort_values("score", ascending=False)

# ---- background wall follows the filters ----
wall_src = f[f["poster_path"].notna()]
if len(wall_src) < 12:
    wall_src = df[df["poster_path"].notna() & (df["vote_count"] >= 400)]
wall_pool = wall_src.nlargest(200, "score")["poster_path"]
wall_paths = wall_pool.sample(min(48, len(wall_pool)), random_state=11).tolist()
tagline = MOODS[mood]["tag"] if mood else "filter anything. the sidebar has everything."
st.markdown(f'<p class="tag">{tagline}</p>' + build_wall(wall_paths), unsafe_allow_html=True)

# ---- the wheel: first shows the movie of the day, every spin picks a new one ----
sig_str = repr((q, sel, mode, tuple(years), min_rating, min_votes, langs))
label = f"{MOODS[mood]['emoji']} {mood}" if mood else "your filters"
pool = f[f["poster_path"].notna()].nlargest(300, "score")
if len(pool) >= 8:
    rng = random.Random(f"{ss['spin_seed']}-{sig_str}")
    ids = rng.sample(list(pool.index), min(26, len(pool)))
    win = min(20, len(ids) - 3)
    name = hashlib.md5(f"{ss['spin_seed']}{sig_str}".encode()).hexdigest()[:10]
    kicker = f"Movie of the day · {date.today():%a %d %b}" if ss["spin_n"] == 0 else "Your spin"
    st.markdown(f'<div class="tk">{kicker} · {html.escape(label)}</div>', unsafe_allow_html=True)
    with st.container(key="reelwrap"):
        st.markdown(reel_block(ids, win, name), unsafe_allow_html=True)
        if st.button("Story & cast", key="open_pick"):
            open_movie(ids[win])
    st.markdown(reveal_html(df.loc[ids[win]]), unsafe_allow_html=True)
    _, sc, _ = st.columns([2, 1.3, 2])
    sc.button("🎡 Spin the wheel", key="spin", on_click=do_spin)

# ---- active filters bar ----
chips = []
if q:
    chips.append(f'Title: "{q}"')
if sel:
    chips.append("Genre: " + (" and " if mode == "All of these" else " or ").join(sel))
if tuple(years) != (YMIN, YMAX):
    chips.append(f"Years {years[0]}-{years[1]}")
if min_rating > 0:
    chips.append(f"Rating {min_rating:g}+")
if min_votes:
    chips.append(f"{min_votes}+ votes")
if langs:
    chips.append("Language: " + ", ".join(LANGS[c] for c in langs))
st.markdown(chips_html(chips), unsafe_allow_html=True)

sig = (sig_str, sort_by)
if ss.get("sig") != sig:
    ss["sig"] = sig
    ss["shown"] = PAGE
shown = ss["shown"]
picks = ranked.head(shown)

hc1, hc2 = st.columns([3, 1])
hc1.markdown(
    f'<p class="count">{len(ranked):,} films match, showing {len(picks)}</p>', unsafe_allow_html=True
)
view = hc2.segmented_control("View", ["Grid", "List"], default="Grid", key="view", label_visibility="collapsed") or "Grid"

if picks.empty:
    st.info("Nothing matches. Loosen a filter, or hit Clear all filters in the sidebar.")
elif view == "List":
    with st.container(key="list"):
        st.markdown(LIST_HEAD, unsafe_allow_html=True)
        for idx, r in picks.iterrows():
            with st.container(key=f"row_{idx}"):
                st.markdown(row_html(r), unsafe_allow_html=True)
                if st.button("Story & cast", key=f"orow_{idx}"):
                    open_movie(idx)
else:
    with st.container(key="grid"):
        for idx, r in picks.iterrows():
            with st.container(key=f"card_{idx}"):
                st.markdown(card(r), unsafe_allow_html=True)
                if st.button("Story & cast", key=f"open_{idx}"):
                    open_movie(idx)

if not picks.empty and shown < len(ranked):
    _, mid, _ = st.columns([2, 1, 2])
    if mid.button("Load more"):
        ss["shown"] += PAGE
        st.rerun()

st.markdown(
    '<p class="foot">Film data and posters via TMDB. This product is not endorsed or certified by TMDB.</p>',
    unsafe_allow_html=True,
)