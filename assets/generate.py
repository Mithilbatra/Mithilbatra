#!/usr/bin/env python3
"""Builds the animated SVGs used by README.md. Edit the content below, then run: python3 assets/generate.py"""
import random
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
BG, BG2, SURFACE, BORDER = '#1a1b26', '#16161e', '#24283b', '#2f334d'
FG, MUTED, COMMENT = '#c0caf5', '#565f89', '#9aa5ce'
BLUE, CYAN, PURPLE, MAGENTA = '#7aa2f7', '#7dcfff', '#bb9af7', '#ff007c'
GREEN, YELLOW, ORANGE, RED = '#9ece6a', '#e0af68', '#ff9e64', '#f7768e'


def write(name, w, h, label, defs, css, body):
    label = escape(label, {'"': '&quot;'})
    (OUT / name).write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<defs>{defs}</defs>
<style>
text {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
{css}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{body}
</svg>
''')


def grad(id_, stops, x2=1, y2=0):
    s = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


GLOW = '<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
BLUR = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>'
SKY = grad('sky', [(0, '#05060d'), (0.55, BG), (1, '#2b1d45')], 0, 1)
FLOOR = grad('floorG', [(0, '#2b1d45'), (1, '#07070d')], 0, 1)
HZ_LINE = grad('hzG', [(0, '#ff9e6400'), (0.3, ORANGE), (0.5, MAGENTA), (0.7, PURPLE), (1, '#bb9af700')])
TWINKLE = '.star circle { animation: twinkle 3s ease-in-out infinite alternate; } @keyframes twinkle { from { opacity: .15; } }'


def stars(rnd, n, w, h):
    dots = ''.join(
        f'<circle cx="{rnd.uniform(8, w - 8):.0f}" cy="{rnd.uniform(8, h):.0f}" r="{rnd.choice((0.6, 0.8, 1, 1.3, 1.7))}" '
        f'style="animation-duration:{rnd.uniform(2, 5):.1f}s;animation-delay:-{rnd.uniform(0, 5):.1f}s"/>' for _ in range(n))
    return f'<g class="star" fill="{FG}">{dots}</g>'


def grid(w, hz, h, n=10, period=3.0):
    """Synthwave floor: rays from the vanishing point plus horizontal lines rushing toward the viewer."""
    rays = ''.join(f'<line x1="{w / 2}" y1="{hz}" x2="{x}" y2="{h}"/>' for x in range(-2400, w + 2401, 120))
    rows = ''.join(
        f'<line class="hl" x1="0" x2="{w}" y1="{hz}" y2="{hz}" style="transform:translateY({(h - hz) * (i / n) ** 2:.1f}px);animation-delay:-{period * i / n:.2f}s"/>'
        for i in range(n))
    defs = f'<clipPath id="floor"><rect x="0" y="{hz}" width="{w}" height="{h - hz}"/></clipPath>'
    css = (f'.hl {{ animation: hl {period}s cubic-bezier(.55,0,1,.45) infinite; }}'
           f'@keyframes hl {{ from {{ transform: translateY(0); opacity: 0; }} 25% {{ opacity: .9; }} to {{ transform: translateY({h - hz}px); opacity: 1; }} }}')
    body = (f'<rect x="0" y="{hz}" width="{w}" height="{h - hz}" fill="url(#floorG)"/>'
            f'<g clip-path="url(#floor)" stroke="{PURPLE}" stroke-width="1.2"><g opacity=".45">{rays}</g>{rows}</g>'
            f'<rect x="0" y="{hz - 5}" width="{w}" height="10" fill="url(#hzG)" opacity=".5" filter="url(#blur)"/>'
            f'<rect x="0" y="{hz - 1.25}" width="{w}" height="2.5" fill="url(#hzG)"/>')
    return defs, css, body


def hero():
    W, H, HZ = 1200, 420, 300
    rnd = random.Random(7)
    ridge_l = [(0, 232), (70, 252), (140, 205), (205, 250), (262, 226), (330, 268), (400, 300)]
    ridge_r = [(W - x, y) for x, y in ridge_l]
    pts = lambda r: ' '.join(f'{x},{y}' for x, y in r)
    mountains = ''.join(
        f'<polygon points="{pts(r)} {r[-1][0]},{HZ} {r[0][0]},{HZ}" fill="url(#mtn)"/><polyline points="{pts(r)}" fill="none" stroke="{PURPLE}" stroke-width="1.5" opacity=".7"/>'
        for r in (ridge_l, ridge_r))
    stripes = ''.join(f'<rect x="0" y="{HZ - 72 + k * 10.5:.1f}" width="{W}" height="{1.5 + k * 1.1:.1f}" fill="#000"/>' for k in range(7))
    gdefs, gcss, gbody = grid(W, HZ, H)
    name = 'MITHIL BATRA'
    defs = (SKY + FLOOR + HZ_LINE + GLOW + BLUR + gdefs
            + grad('sunG', [(0, ORANGE), (0.55, MAGENTA), (1, PURPLE)], 0, 1)
            + grad('nameG', [(0, CYAN), (0.4, BLUE), (0.7, PURPLE), (1, MAGENTA)])
            + grad('mtn', [(0, '#1f1a33'), (1, '#0d0d18')], 0, 1)
            + grad('shineG', [(0, '#ffffff00'), (0.5, '#ffffffcc'), (1, '#ffffff00')])
            + grad('tail', [(0, '#ffffff00'), (1, '#ffffff')])
            + f'<mask id="sunMask"><rect width="{W}" height="{H}" fill="#fff"/>{stripes}</mask>'
            + f'<clipPath id="above"><rect width="{W}" height="{HZ}"/></clipPath>'
            + f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
            + f'<clipPath id="nameClip"><text x="600" y="150" text-anchor="middle" class="name">{name}</text></clipPath>'
            + '<radialGradient id="vig" cx=".5" cy=".45" r=".75"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>'
            + '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>')
    css = TWINKLE + gcss + f'''
.name {{ font-size: 92px; font-weight: 800; letter-spacing: 6px; }}
.sub {{ font-size: 19px; font-weight: 600; letter-spacing: 7px; fill: {FG}; }}
.hud {{ font-size: 13px; fill: {COMMENT}; letter-spacing: 1px; }}
.rise {{ animation: rise 1.2s cubic-bezier(.2,.8,.2,1) both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(18px); }} }}
.g1, .g2 {{ opacity: 0; mix-blend-mode: screen; animation: g1 5s steps(1) infinite 2s; }}
.g2 {{ animation-name: g2; }}
@keyframes g1 {{ 0%, 89% {{ opacity: 0; transform: none; }} 90% {{ opacity: .85; transform: translate(-7px, 2px); }} 92% {{ opacity: .85; transform: translate(5px, -3px); }} 94% {{ opacity: .6; transform: translate(-2px, 0); }} 96%, 100% {{ opacity: 0; transform: none; }} }}
@keyframes g2 {{ 0%, 89% {{ opacity: 0; transform: none; }} 90% {{ opacity: .85; transform: translate(7px, -2px); }} 92% {{ opacity: .85; transform: translate(-5px, 3px); }} 94% {{ opacity: .6; transform: translate(3px, 1px); }} 96%, 100% {{ opacity: 0; transform: none; }} }}
.shine {{ animation: shine 6s ease-in-out infinite 1.5s; }}
@keyframes shine {{ from {{ transform: translateX(0) skewX(-20deg); }} 35%, to {{ transform: translateX(1400px) skewX(-20deg); }} }}
.pulse {{ animation: pulse 4s ease-in-out infinite alternate; }}
@keyframes pulse {{ from {{ opacity: .25; }} to {{ opacity: .55; }} }}
.blink {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.meteor {{ opacity: 0; animation: meteor 9s ease-in infinite 3s; }}
@keyframes meteor {{ 0% {{ opacity: 0; transform: translate(0, 0); }} 1% {{ opacity: 1; }} 9% {{ opacity: 0; transform: translate(-460px, 190px); }} 100% {{ opacity: 0; transform: translate(-460px, 190px); }} }}
'''
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(rnd, 80, W, HZ - 20)}
<g class="meteor"><line x1="1000" y1="30" x2="1110" y2="-16" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/></g>
<g clip-path="url(#above)">
  <circle class="pulse" cx="600" cy="{HZ}" r="135" fill="url(#sunG)" filter="url(#blur)"/>
  <circle cx="600" cy="{HZ}" r="100" fill="url(#sunG)" mask="url(#sunMask)"/>
</g>
{mountains}
{gbody}
<g class="rise">
  <text x="600" y="150" text-anchor="middle" class="name g1" fill="{CYAN}">{name}</text>
  <text x="600" y="150" text-anchor="middle" class="name g2" fill="{MAGENTA}">{name}</text>
  <text x="600" y="150" text-anchor="middle" class="name" fill="url(#nameG)" filter="url(#glow)">{name}</text>
  <g clip-path="url(#nameClip)"><rect class="shine" x="-260" y="40" width="140" height="140" fill="url(#shineG)"/></g>
</g>
<text x="600" y="196" text-anchor="middle" class="sub rise" style="animation-delay:.4s">SOFTWARE ENGINEER · CSE @ NIT DELHI</text>
<text x="28" y="36" class="hud mono" textLength="156">&gt; hello_world.init()</text><rect class="blink" x="190" y="25" width="8" height="14" fill="{COMMENT}"/>
<circle class="blink" cx="1108" cy="31" r="5" fill="{GREEN}" style="animation-duration:2s"/><text x="1172" y="36" text-anchor="end" class="hud mono">ONLINE</text>
<text x="28" y="{H - 22}" class="hud mono">BACKEND · FULL-STACK · ML</text>
<text x="{W - 28}" y="{H - 22}" text-anchor="end" class="hud mono">NEW DELHI · IN</text>
<rect width="{W}" height="{H}" fill="url(#scan)" opacity=".5"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="{BORDER}" stroke-width="2"/>'''
    write('hero.svg', W, H, 'Mithil Batra — Software Engineer · CSE @ NIT Delhi', defs, css, body)


def mono_line(segs, x0, y, cw):
    """Places each coloured segment on a fixed character grid so columns line up in any monospace font."""
    out, col = [], 0
    for seg in segs:
        text, color, bold = (seg + (False,))[:3]
        lead, core = len(text) - len(text.lstrip(' ')), text.strip(' ')
        if core:
            weight = ' font-weight="700"' if bold else ''
            out.append(f'<text class="mono" x="{x0 + (col + lead) * cw:.1f}" y="{y}" fill="{color}"{weight} textLength="{len(core) * cw:.1f}">{escape(core)}</text>')
        col += len(text)
    return ''.join(out), col


def json_line(key, vals, last=False):
    segs = [('  "' + key + '"', BLUE), (':' + ' ' * (9 - len(key)), FG), ('[', FG)]
    for i, v in enumerate(vals):
        segs.append((f'"{v}"', GREEN))
        if i < len(vals) - 1:
            segs.append((', ', FG))
    segs.append((']' + ('' if last else ','), FG))
    return segs


def terminal():
    W, FS, CW, LH, X0, TOP = 860, 14, 8.4, 22, 26, 70
    prompt = [('mithil', GREEN, True), ('@', FG), ('nit-delhi', CYAN, True), (' ~ ', BLUE), ('$ ', PURPLE)]
    script = [
        ('whoami', [[('Mithil Batra', FG, True), (' · CS undergrad @ NIT Delhi · CGPA 8.93', COMMENT)]]),
        ('cat role.txt', [[('Software Engineering Intern', FG), (' @ ', COMMENT), ('HSBC', RED, True), (' · Summer 2026', COMMENT)]]),
        ('ls ~/work', [[('backend/', BLUE, True), ('  full-stack/', BLUE, True), ('  machine-learning/', BLUE, True), ('  open-source/', BLUE, True), ('  dsa/', BLUE, True)]]),
        ('cat stack.json', [[('{', FG)],
                            json_line('backend', ['Java', 'Spring Boot', 'Node.js', 'REST', 'Microservices']),
                            json_line('frontend', ['Next.js', 'React', 'Tailwind CSS']),
                            json_line('ml', ['Python', 'scikit-learn', 'Pandas', 'OpenCV']),
                            json_line('cloud', ['GCP', 'AWS', 'Azure', 'Docker'], last=True),
                            [('}', FG)]]),
        ('cat oss.txt', [[('Writing Mockito unit tests for ', FG), ('uber-doma-architecture', CYAN, True)]]),
        ('echo $MOTTO', [[('"Build it end to end."', YELLOW, True)]]),
    ]
    rows, typing, row, t = [], [], 0, 0.5  # rows: (time shown, markup); everything loops every T seconds
    for cmd, outs in script:
        y = TOP + row * LH
        p, pc = mono_line(prompt, X0, y, CW)
        c, _ = mono_line([(cmd, FG)], X0 + pc * CW, y, CW)
        n, start, i = len(cmd), t + 0.45, len(rows)
        dur, cx, shift = max(0.3, n * 0.055), X0 + pc * CW, f'transform:translateX({n * CW:.1f}px)'
        rows.append((t, f'{p}{c}'
                        f'<rect x="{cx:.1f}" y="{y - FS}" width="{n * CW + 4:.1f}" height="{LH}" fill="{BG}" style="{shift};animation-name:k{i}"/>'
                        f'<rect x="{cx:.1f}" y="{y - FS + 1}" width="{CW:.1f}" height="{FS + 3}" fill="{FG}" style="{shift};opacity:0;animation-name:k{i},v{i}"/>'))
        typing.append((i, n, t, start, dur))
        row, t = row + 1, start + dur + 0.3
        for segs in outs:
            rows.append((t, mono_line(segs, X0, TOP + row * LH, CW)[0]))
            row, t = row + 1, t + 0.07
        t += 0.35
    y = TOP + row * LH
    p, pc = mono_line(prompt, X0, y, CW)
    rows.append((t, f'{p}<rect class="blink" x="{X0 + pc * CW:.1f}" y="{y - FS + 1}" width="{CW:.1f}" height="{FS + 3}" fill="{FG}"/>'))
    T = t + 6
    at = lambda sec: f'{100 * sec / T:.2f}%'
    keys = [f'@keyframes s{i} {{ 0%, {at(t0)} {{ opacity: 0; }} {at(t0 + 0.01)}, 98% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}' for i, (t0, _) in enumerate(rows)]
    for i, n, t0, start, dur in typing:
        keys.append(f'@keyframes k{i} {{ 0%, {at(start)} {{ transform: translateX(0); animation-timing-function: steps({n}, end); }} {at(start + dur)}, 100% {{ transform: translateX({n * CW:.1f}px); }} }}')
        keys.append(f'@keyframes v{i} {{ 0%, {at(t0)} {{ opacity: 0; }} {at(t0 + 0.01)}, {at(start + dur + 0.25)} {{ opacity: 1; }} {at(start + dur + 0.26)}, 100% {{ opacity: 0; }} }}')
    rows = [f'<g style="animation-name:s{i}">{markup}</g>' for i, (_, markup) in enumerate(rows)]
    H = TOP + row * LH + 24
    css = f'''
.mono {{ font-size: {FS}px; }}
.ttl {{ font-size: 12px; fill: {COMMENT}; }}
g, rect {{ animation-duration: {T:.2f}s; animation-iteration-count: infinite; animation-timing-function: linear; }}
{chr(10).join(keys)}
.blink {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
'''
    body = f'''<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{BG}"/>
<rect x="1" y="1" width="{W - 2}" height="38" rx="12" fill="{BG2}"/><rect x="1" y="26" width="{W - 2}" height="13" fill="{BG2}"/>
<circle cx="24" cy="20" r="6.5" fill="{RED}"/><circle cx="46" cy="20" r="6.5" fill="{YELLOW}"/><circle cx="68" cy="20" r="6.5" fill="{GREEN}"/>
<text x="{W / 2}" y="24" text-anchor="middle" class="mono ttl">mithil@nit-delhi: ~ — zsh</text>
{''.join(rows)}
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="none" stroke="{BORDER}" stroke-width="2"/>'''
    write('terminal.svg', W, H, 'Terminal: Mithil Batra, CS undergrad at NIT Delhi (CGPA 8.93), Software Engineering Intern at HSBC, works on backend, full-stack, machine learning and open source', '', css, body)


def stats():
    W, H, GAP, TH, HC, BASE = 860, 160, 16, 140, 56, 88
    TW = (W - 3 * GAP) / 4
    tiles = [('800', '+', 'DSA PROBLEMS SOLVED', YELLOW), ('99.467', '', 'JEE MAIN PERCENTILE', BLUE),
             ('8.93', '', 'CGPA · NIT DELHI', GREEN), ('5376', '', 'JEE ADVANCED AIR', PURPLE)]
    defs, body = [GLOW], []
    for i, (value, suffix, label, color) in enumerate(tiles):
        x = i * (TW + GAP)
        chars = value + suffix
        widths = [13 if ch == '.' else 28 for ch in chars]
        cx = x + TW / 2 - sum(widths) / 2
        defs.append(f'<radialGradient id="tg{i}" cx="1" cy="1" r="1"><stop offset="0" stop-color="{color}" stop-opacity=".22"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        defs.append(f'<clipPath id="bar{i}"><rect x="{x + 18:.1f}" y="10" width="{TW - 36:.1f}" height="3"/></clipPath>')
        body.append(f'<rect x="{x + 1:.1f}" y="11" width="{TW - 2:.1f}" height="{TH}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
                    f'<rect x="{x + 1:.1f}" y="11" width="{TW - 2:.1f}" height="{TH}" rx="14" fill="url(#tg{i})"/>'
                    f'<rect x="{x + 18:.1f}" y="10" width="{TW - 36:.1f}" height="3" rx="1.5" fill="{color}" filter="url(#glow)"/>'
                    f'<g clip-path="url(#bar{i})"><rect class="glint" x="{x - 30:.1f}" y="10" width="40" height="3" fill="#fff" style="animation-delay:{i * 0.6:.1f}s"/></g>')
        col_delay = 0.3 + i * 0.25
        for j, (ch, cw) in enumerate(zip(chars, widths)):
            mid, cx = cx + cw / 2, cx + cw
            if ch.isdigit():
                d = int(ch)
                defs.append(f'<clipPath id="c{i}{j}"><rect x="{mid - cw / 2:.1f}" y="{BASE - 44}" width="{cw}" height="{HC}"/></clipPath>')
                strip = ''.join(f'<text x="{mid:.1f}" y="{BASE + k * HC}" text-anchor="middle">{k % 10}</text>' for k in range(20))
                body.append(f'<g clip-path="url(#c{i}{j})"><g class="roll" style="--y:-{(10 + d) * HC}px;transform:translateY(var(--y));animation-delay:{col_delay + j * 0.2:.2f}s">{strip}</g></g>')
            else:
                fill = f' fill="{color}"' if ch == '+' else ''
                body.append(f'<text x="{mid:.1f}" y="{BASE}" text-anchor="middle"{fill}>{ch}</text>')
        body.append(f'<text x="{x + TW / 2:.1f}" y="124" text-anchor="middle" class="lbl">{escape(label)}</text>')
    css = f'''
text {{ font-size: 46px; font-weight: 800; fill: {FG}; font-variant-numeric: tabular-nums; }}
.lbl {{ font-size: 11.5px; font-weight: 700; letter-spacing: 2.2px; fill: {COMMENT}; }}
.roll {{ animation: roll 9s cubic-bezier(.15,.75,.25,1) infinite backwards; }}
@keyframes roll {{ 0% {{ transform: translateY(0); }} 28%, 100% {{ transform: translateY(var(--y)); }} }}
.glint {{ opacity: 0; animation: glint 3.2s ease-in-out infinite; }}
@keyframes glint {{ from {{ opacity: .9; transform: translateX(0); }} 60%, to {{ opacity: .9; transform: translateX({TW:.0f}px); }} }}
'''
    write('stats.svg', W, H, '800+ DSA problems solved · 99.467 JEE Main percentile · 8.93 CGPA at NIT Delhi · JEE Advanced AIR 5376', ''.join(defs), css, ''.join(body))


def divider():
    W, H, Y = 1200, 28, 14
    defs = (GLOW + BLUR + grad('line', [(0, '#7aa2f700'), (0.2, BLUE), (0.5, PURPLE), (0.8, MAGENTA), (1, '#ff007c00')])
            + grad('pulse', [(0, '#7dcfff00'), (0.5, CYAN), (1, '#7dcfff00')]))
    css = f'''
.pulse {{ opacity: 0; animation: sweep 5s cubic-bezier(.45,0,.55,1) infinite; }}
@keyframes sweep {{ 0% {{ opacity: 0; transform: translateX(-220px); }} 12%, 80% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translateX({W}px); }} }}
.gem {{ transform-box: fill-box; transform-origin: center; animation: gem 2.5s ease-in-out infinite alternate; }}
@keyframes gem {{ from {{ opacity: .45; }} }}
'''
    body = f'''<rect x="0" y="{Y - 0.75}" width="{W}" height="1.5" fill="url(#line)" opacity=".8"/>
<g class="pulse"><rect x="0" y="{Y - 3}" width="220" height="6" fill="url(#pulse)" filter="url(#blur)"/><rect x="0" y="{Y - 1}" width="220" height="2" fill="url(#pulse)"/></g>
<rect class="gem" x="{W / 2 - 5}" y="{Y - 5}" width="10" height="10" fill="{BG}" stroke="{PURPLE}" stroke-width="1.5" transform="rotate(45 {W / 2} {Y})" filter="url(#glow)"/>'''
    write('divider.svg', W, H, 'Section divider', defs, css, body)


TECH_ROWS = [
    [('Java', '#f89820'), ('Python', '#ffd43b'), ('C++', '#659ad2'), ('C', '#a8b9cc'), ('TypeScript', '#3178c6'), ('JavaScript', '#f7df1e'),
     ('Spring Boot', '#6db33f'), ('Next.js', '#ffffff'), ('React', '#61dafb'), ('Node.js', '#5fa04e'), ('Flask', FG), ('Tailwind CSS', '#38bdf8'), ('OpenCV', '#7aa2f7')],
    [('PostgreSQL', '#4169e1'), ('MySQL', '#4479a1'), ('MongoDB', '#47a248'), ('GCP', '#4285f4'), ('AWS', '#ff9900'), ('Azure', '#3ba5f2'),
     ('Docker', '#2496ed'), ('Git', '#f05032'), ('scikit-learn', '#f7931e'), ('Pandas', '#e70488'), ('Postman', '#ff6c37'), ('Figma', '#a259ff'),
     ('REST APIs', GREEN), ('Microservices', PURPLE), ('Webhooks', CYAN)],
]


def ticker():
    W, H, SPEED = 900, 112, 45
    rows, css = [], [f'text {{ font-size: 15px; font-weight: 600; fill: {FG}; }}']
    for r, items in enumerate(TECH_ROWS):
        y, x, pills = 32 + r * 50, 0, []
        for name, color in items:
            tw = sum(10 if ch.isupper() else 8.2 if ch.isalnum() else 9 if ch == '+' else 4.5 for ch in name)
            pills.append(f'<rect x="{x}" y="{y - 17}" width="{tw + 46:.0f}" height="34" rx="17" fill="{SURFACE}" stroke="{BORDER}"/>'
                         f'<circle cx="{x + 19}" cy="{y}" r="4.5" fill="{color}" filter="url(#glow)"/>'
                         f'<text x="{x + 31}" y="{y + 5}" textLength="{tw:.0f}">{escape(name)}</text>')
            x += tw + 46 + 14
        strip = ''.join(pills)
        rows.append(f'<g class="row{r}">{strip}<g transform="translate({x:.0f} 0)">{strip}</g></g>')
        a, b = (0, -x) if r == 0 else (-x, 0)
        css.append(f'.row{r} {{ animation: m{r} {x / SPEED:.1f}s linear infinite; transform: translateX({a:.0f}px); }}'
                   f'@keyframes m{r} {{ from {{ transform: translateX({a:.0f}px); }} to {{ transform: translateX({b:.0f}px); }} }}')
    defs = (GLOW + grad('fade', [(0, '#000'), (0.08, '#fff'), (0.92, '#fff'), (1, '#000')])
            + f'<mask id="ends"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')
    write('ticker.svg', W, H, 'Tech stack: ' + ', '.join(n for row in TECH_ROWS for n, _ in row), defs, '\n'.join(css), f'<g mask="url(#ends)">{"".join(rows)}</g>')


def banner(name, label, defs, css, body, accent):
    W, H = 820, 200
    defs = (GLOW + grad('bannerBg', [(0, BG), (1, BG2)], 1, 1) + f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
            + '<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#3b4261"/></pattern>'
            + f'<radialGradient id="spot" cx="0" cy="0" r="1"><stop offset="0" stop-color="{accent}" stop-opacity=".18"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>' + defs)
    css = f'''
.title {{ font-size: 44px; font-weight: 900; font-style: italic; letter-spacing: 1px; }}
.sub {{ font-size: 12px; fill: {COMMENT}; letter-spacing: 1px; }}
.tag {{ font-size: 11px; font-weight: 700; letter-spacing: 1.5px; }}
.blink {{ animation: blink 1.2s ease-in-out infinite alternate; }}
@keyframes blink {{ from {{ opacity: .2; }} }}
''' + css
    body = (f'<g clip-path="url(#frame)"><rect width="{W}" height="{H}" fill="url(#bannerBg)"/><rect width="{W}" height="{H}" fill="url(#dots)" opacity=".35"/>'
            f'<rect width="{W}" height="{H}" fill="url(#spot)"/>{body}</g>'
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="{BORDER}" stroke-width="2"/>')
    write(name, W, H, label, defs, css, body)


def pitwall():
    track = 'M612 150C604 118 612 84 640 70L700 46C722 38 748 44 760 62C772 80 766 98 748 104L716 114C704 118 706 132 718 136L770 150C790 156 788 178 766 178L632 178C618 178 614 164 612 150Z'
    bars = ''.join(
        f'<text x="380" y="{y + 11}" class="mono tag" fill="{FG}">P{i + 1}</text>'
        f'<rect x="410" y="{y}" width="150" height="14" rx="7" fill="{SURFACE}"/>'
        f'<rect class="grow" x="410" y="{y}" width="{150 * f:.0f}" height="14" rx="7" fill="{c}" style="animation-delay:{0.3 + i * 0.2:.1f}s"/>'
        for i, (y, f, c) in enumerate([(70, .88, YELLOW), (102, .7, FG), (134, .54, ORANGE)]))
    sectors = ''.join(
        f'<rect class="sector" x="{32 + i * 92}" y="150" width="86" height="26" rx="5" style="animation-delay:-{i * 1.3:.1f}s"/>'
        f'<text x="{75 + i * 92}" y="167" text-anchor="middle" class="mono tag" fill="{BG}">S{i + 1}</text>' for i in range(3))
    defs = grad('pwG', [(0, RED), (1, ORANGE)]) + BLUR
    css = f'''
.grow {{ transform-box: fill-box; transform-origin: left center; animation: grow 6s cubic-bezier(.2,.8,.2,1) infinite; }}
@keyframes grow {{ 0% {{ transform: scaleX(0); }} 30%, 100% {{ transform: scaleX(1); }} }}
.sector {{ fill: {PURPLE}; animation: sector 3.9s steps(1) infinite; }}
@keyframes sector {{ 0% {{ fill: {YELLOW}; }} 33% {{ fill: {GREEN}; }} 66% {{ fill: {PURPLE}; }} }}
.lap {{ stroke-dasharray: 8 92; animation: lap 4s linear infinite; }}
@keyframes lap {{ from {{ stroke-dashoffset: 100; }} to {{ stroke-dashoffset: 0; }} }}
'''
    body = f'''
<rect x="32" y="30" width="66" height="22" rx="11" fill="{RED}" fill-opacity=".15" stroke="{RED}"/>
<circle class="blink" cx="45" cy="41" r="4" fill="{RED}"/><text x="55" y="45" class="mono tag" fill="{RED}">LIVE</text>
<text x="32" y="104" class="title" fill="url(#pwG)" filter="url(#glow)">PIT WALL</text>
<text x="32" y="130" class="mono sub">F1 PODIUM PREDICTION · FASTF1 TELEMETRY</text>
{sectors}
<text x="380" y="50" class="mono tag" fill="{COMMENT}">PODIUM CONFIDENCE</text>
{bars}
<text x="612" y="34" class="mono tag" fill="{COMMENT}">LIVE TIMING</text>
<path d="{track}" fill="none" stroke="{BORDER}" stroke-width="11" stroke-linejoin="round"/>
<path d="{track}" fill="none" stroke="#3b4261" stroke-width="1" stroke-dasharray="4 6"/>
<line x1="602" y1="146" x2="622" y2="146" stroke="{FG}" stroke-width="3"/>
<path class="lap" d="{track}" pathLength="100" fill="none" stroke="{ORANGE}" stroke-width="10" opacity=".5" filter="url(#blur)" style="stroke-dasharray:14 86"/>
<path class="lap" d="{track}" pathLength="100" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>'''
    banner('pitwall.svg', 'Pit Wall: F1 podium prediction and live timing dashboard', defs, css, body, RED)


def resolvr():
    states = [('TRIGGERED', RED), ('ACKNOWLEDGED', YELLOW), ('ESCALATED', ORANGE), ('RESOLVED', GREEN)]
    pills = ''.join(
        f'<g class="state" style="animation-delay:{i * 2 - 8}s;opacity:{1 if i == 3 else 0}"><rect x="32" y="150" width="150" height="26" rx="13" fill="{c}" fill-opacity=".15" stroke="{c}"/>'
        f'<circle cx="48" cy="163" r="4" fill="{c}"/><text x="60" y="167" class="mono tag" fill="{c}">{s}</text></g>' for i, (s, c) in enumerate(states))
    cols = ''.join(
        f'<text x="{360 + i * 150}" y="40" class="mono tag" fill="{COMMENT}">{h}</text>'
        f'<rect x="{360 + i * 150}" y="50" width="136" height="132" rx="10" fill="{BG2}" stroke="{BORDER}"/>'
        f'<rect x="{368 + i * 150}" y="{60 if i != 1 else 128}" width="120" height="48" rx="6" fill="{SURFACE}" opacity=".45"/>'
        for i, h in enumerate(['OPEN', 'IN PROGRESS', 'RESOLVED']))
    defs = grad('rsG', [(0, RED), (1, PURPLE)])
    css = f'''
.state {{ animation: state 8s steps(1) infinite; }}
@keyframes state {{ 0% {{ opacity: 1; }} 25%, 100% {{ opacity: 0; }} }}
.ping {{ transform-box: fill-box; transform-origin: center; animation: ping 2s ease-out infinite; }}
@keyframes ping {{ from {{ transform: scale(1); opacity: .9; }} to {{ transform: scale(3.2); opacity: 0; }} }}
.card {{ transform: translateX(300px); animation: move 8s ease-in-out infinite; }}
@keyframes move {{ 0%, 22% {{ transform: translateX(0); opacity: 1; }} 27%, 72% {{ transform: translateX(150px); }} 77%, 94% {{ transform: translateX(300px); opacity: 1; }} 97% {{ transform: translateX(300px); opacity: 0; }} 98% {{ transform: translateX(0); opacity: 0; }} 100% {{ transform: translateX(0); opacity: 1; }} }}
.sev {{ fill: {GREEN}; animation: sev 8s steps(1) infinite; }}
@keyframes sev {{ 0% {{ fill: {RED}; }} 25% {{ fill: {YELLOW}; }} 50% {{ fill: {ORANGE}; }} 75% {{ fill: {GREEN}; }} }}
'''
    body = f'''
<circle class="ping" cx="44" cy="44" r="6" fill="none" stroke="{RED}" stroke-width="2"/>
<circle class="ping" cx="44" cy="44" r="6" fill="none" stroke="{RED}" stroke-width="2" style="animation-delay:1s"/>
<circle cx="44" cy="44" r="6" fill="{RED}" filter="url(#glow)"/>
<text x="72" y="49" class="mono tag" fill="{RED}">ON-CALL · PAGING</text>
<text x="32" y="106" class="title" fill="url(#rsG)" filter="url(#glow)">RESOLVR</text>
<text x="32" y="132" class="mono sub">INCIDENTS · ON-CALL · ESCALATION</text>
{pills}
{cols}
<g class="card">
  <rect x="368" y="94" width="120" height="58" rx="6" fill="{SURFACE}" stroke="#3b4261"/>
  <rect class="sev" x="368" y="94" width="4" height="58" rx="2"/>
  <text x="380" y="112" class="mono tag" fill="{FG}">INC-1042</text>
  <text x="380" y="128" class="mono" font-size="10" fill="{COMMENT}">checkout 5xx spike</text>
  <rect class="sev" x="380" y="136" width="34" height="10" rx="5" opacity=".8"/>
</g>'''
    banner('resolvr.svg', 'Resolvr: an incident moving from triggered to resolved on a Kanban board', defs, css, body, PURPLE)


def interviewer():
    rnd = random.Random(3)
    eq = ''.join(
        f'<rect x="{32 + i * 12}" y="{182 - h:.0f}" width="6" height="{h:.0f}" rx="3" style="animation-duration:{rnd.uniform(.45, 1.1):.2f}s;animation-delay:-{rnd.uniform(0, 1):.2f}s"/>'
        for i, h in ((i, rnd.uniform(8, 30)) for i in range(24)))
    dots = ''.join(f'<circle class="bounce" cx="{742 + i * 12}" cy="108" r="3.5" fill="{BLUE}" style="animation-delay:{i * 0.15:.2f}s"/>' for i in range(3))
    C = 87.96
    defs = grad('aiG', [(0, GREEN), (1, CYAN)]) + grad('eqG', [(0, GREEN), (1, CYAN)], 0, 1)
    css = f'''
.eq rect {{ fill: url(#eqG); transform-box: fill-box; transform-origin: center bottom; animation: eq .8s ease-in-out infinite alternate; }}
@keyframes eq {{ from {{ transform: scaleY(.2); }} }}
.q {{ animation: q 9s ease-out infinite; }}
@keyframes q {{ 0% {{ opacity: 0; transform: translateY(8px); }} 6%, 92% {{ opacity: 1; transform: none; }} 98%, 100% {{ opacity: 0; }} }}
.bubble {{ animation: bubble 9s ease-out infinite; }}
@keyframes bubble {{ 0%, 11% {{ opacity: 0; transform: translateY(8px); }} 15%, 92% {{ opacity: 1; transform: none; }} 98%, 100% {{ opacity: 0; }} }}
.typing {{ opacity: 0; animation: typing 9s steps(1) infinite; }}
@keyframes typing {{ 0% {{ opacity: 0; }} 15% {{ opacity: 1; }} 36%, 100% {{ opacity: 0; }} }}
.bounce {{ animation: bounce .6s ease-in-out infinite alternate; }}
@keyframes bounce {{ to {{ transform: translateY(-4px); }} }}
.ans {{ animation: ans 9s ease-out infinite; }}
@keyframes ans {{ 0%, 36% {{ opacity: 0; }} 40%, 92% {{ opacity: 1; }} 98%, 100% {{ opacity: 0; }} }}
.fb {{ animation: fb 9s ease-out infinite; }}
@keyframes fb {{ 0%, 48% {{ opacity: 0; transform: translateY(8px); }} 53%, 92% {{ opacity: 1; transform: none; }} 98%, 100% {{ opacity: 0; }} }}
.ring {{ stroke-dasharray: {C}; stroke-dashoffset: {C * .12:.1f}; animation: ring 9s ease-out infinite; }}
@keyframes ring {{ 0%, 52% {{ stroke-dashoffset: {C}; }} 72%, 100% {{ stroke-dashoffset: {C * .12:.1f}; }} }}
'''
    body = f'''
<rect x="32" y="30" width="58" height="22" rx="11" fill="{RED}" fill-opacity=".15" stroke="{RED}"/>
<circle class="blink" cx="45" cy="41" r="4" fill="{RED}"/><text x="55" y="45" class="mono tag" fill="{RED}">REC</text>
<rect x="98" y="30" width="80" height="22" rx="11" fill="{PURPLE}" fill-opacity=".15" stroke="{PURPLE}"/>
<text x="138" y="45" text-anchor="middle" class="mono tag" fill="{PURPLE}">GEMINI</text>
<text x="32" y="104" class="title" fill="url(#aiG)" filter="url(#glow)" style="font-size:38px">AI INTERVIEWER</text>
<text x="32" y="130" class="mono sub">ROLE-AWARE QUESTIONS · AI FEEDBACK</text>
<g class="eq">{eq}</g>
<g class="q">
  <circle cx="378" cy="54" r="12" fill="{PURPLE}" fill-opacity=".25" stroke="{PURPLE}"/><text x="378" y="58" text-anchor="middle" class="mono tag" fill="{PURPLE}">AI</text>
  <rect x="398" y="36" width="320" height="36" rx="10" fill="{SURFACE}"/>
  <text x="412" y="59" class="mono" font-size="12" fill="{FG}">Walk me through a system you designed.</text>
</g>
<g class="bubble">
  <rect x="436" y="90" width="354" height="36" rx="10" fill="{BLUE}" fill-opacity=".14" stroke="{BLUE}" stroke-opacity=".6"/>
  <g class="typing">{dots}</g>
  <text class="ans mono" x="450" y="113" font-size="12" fill="{FG}">Sure, I built Resolvr, an incident platform…</text>
</g>
<g class="fb">
  <rect x="398" y="140" width="392" height="44" rx="10" fill="{GREEN}" fill-opacity=".08" stroke="{GREEN}" stroke-opacity=".5"/>
  <circle cx="420" cy="162" r="11" fill="{GREEN}" fill-opacity=".2" stroke="{GREEN}"/>
  <path d="M415 162l4 4 7-8" fill="none" stroke="{GREEN}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="440" y="158" class="mono tag" fill="{GREEN}">FEEDBACK READY</text>
  <text x="440" y="174" class="mono" font-size="11" fill="{COMMENT}">clarity · depth · structure</text>
  <circle cx="760" cy="162" r="14" fill="none" stroke="{SURFACE}" stroke-width="4"/>
  <circle class="ring" cx="760" cy="162" r="14" fill="none" stroke="{GREEN}" stroke-width="4" stroke-linecap="round" transform="rotate(-90 760 162)"/>
</g>'''
    banner('interviewer.svg', 'AI Mock Interviewer: an AI question, a spoken answer and generated feedback', defs, css, body, GREEN)


def footer():
    W, H, HZ = 1200, 230, 190
    gdefs, gcss, gbody = grid(W, HZ, H, n=6, period=2.4)
    defs = (SKY + FLOOR + HZ_LINE + GLOW + BLUR + gdefs + grad('ftG', [(0, CYAN), (0.5, BLUE), (1, PURPLE)])
            + grad('sunG', [(0, ORANGE), (0.55, MAGENTA), (1, PURPLE)], 0, 1)
            + f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
            + f'<clipPath id="above"><rect width="{W}" height="{HZ}"/></clipPath>')
    css = TWINKLE + gcss + f'''
.big {{ font-size: 42px; font-weight: 800; letter-spacing: 10px; }}
.line {{ font-size: 20px; fill: {FG}; }}
.contact {{ font-size: 16px; fill: {COMMENT}; letter-spacing: 1px; }}
'''
    body = f'''<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#sky)"/>
{stars(random.Random(11), 40, W, HZ - 10)}
<circle cx="600" cy="{HZ}" r="90" fill="url(#sunG)" opacity=".35" filter="url(#blur)" clip-path="url(#above)"/>
{gbody}
<text x="600" y="76" text-anchor="middle" class="big" fill="url(#ftG)" filter="url(#glow)">THANKS FOR VISITING</text>
<text x="600" y="120" text-anchor="middle" class="line">Open to conversations about backend systems, machine learning and building products end to end.</text>
<text x="600" y="156" text-anchor="middle" class="contact mono">mithil.batra05@gmail.com · linkedin.com/in/mithilbatra211205</text>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="none" stroke="{BORDER}" stroke-width="2"/>'''
    write('footer.svg', W, H, 'Thanks for visiting. Open to conversations about backend systems, machine learning and building products end to end. mithil.batra05@gmail.com', defs, css, body)


if __name__ == '__main__':
    for build in (hero, terminal, stats, divider, ticker, pitwall, resolvr, interviewer, footer):
        build()
    print('wrote', ', '.join(sorted(p.name for p in OUT.glob('*.svg'))))
