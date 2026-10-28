#!/usr/bin/env python3
"""Builds the SVGs used by README.md. Edit the content below, then run: python3 assets/generate.py

`python3 assets/generate.py --github-stats DIR` fetches live GitHub numbers (needs GITHUB_TOKEN) and writes DIR/github-stats.svg.
"""
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
BG, BG2, SURFACE, BORDER = '#161b22', '#0d1117', '#21262d', '#30363d'
FG, MUTED, COMMENT = '#e6edf3', '#6e7681', '#8b949e'
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
BLUR = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>'
CARD = (grad('cardBg', [(0, BG2), (1, BG)], 1, 1)
        + '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="#30363d"/></pattern>')


def card(w, h, glow_at, body, tint=BLUE):
    """Dark rounded panel with a dot grid and one soft, slowly drifting accent glow."""
    gx, gy = glow_at
    return (f'<defs><clipPath id="frame"><rect width="{w}" height="{h}" rx="16"/></clipPath></defs><g clip-path="url(#frame)">'
            f'<rect width="{w}" height="{h}" fill="url(#cardBg)"/><rect width="{w}" height="{h}" fill="url(#dots)" opacity=".55"/>'
            f'<circle class="drift" cx="{gx}" cy="{gy}" r="260" fill="{tint}" opacity=".16" filter="url(#blur)"/>'
            f'<circle class="drift" cx="{gx + 160}" cy="{gy + 200}" r="200" fill="{PURPLE}" opacity=".09" filter="url(#blur)" style="animation-delay:-6s"/>'
            f'{body}</g><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="16" fill="none" stroke="{BORDER}" stroke-width="2"/>')


CARD_CSS = """
.drift { animation: drift 14s ease-in-out infinite alternate; }
@keyframes drift { from { transform: translate(-40px, 10px); } to { transform: translate(40px, -10px); } }
.rise { animation: rise 1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes rise { from { opacity: 0; transform: translateY(12px); } }
"""


def hero():
    W, H = 1200, 320
    body = f'''
<text x="1120" y="258" text-anchor="end" font-size="220" font-weight="800" letter-spacing="6" fill="url(#accentX)" fill-opacity=".32">MB</text>
<rect x="72" y="96" width="4" height="132" rx="2" fill="url(#accent)"/>
<g class="rise">
  <text x="100" y="162" font-size="76" font-weight="700" fill="{FG}" letter-spacing="-1">Mithil Batra</text>
  <text x="102" y="204" font-size="24" fill="{COMMENT}">Software Engineer · CSE @ NIT Delhi</text>
</g>
<text x="102" y="244" class="mono rise" font-size="17" letter-spacing="3" style="animation-delay:.25s"><tspan fill="{BLUE}">BACKEND</tspan><tspan fill="{MUTED}"> / </tspan><tspan fill="{PURPLE}">FULL-STACK</tspan><tspan fill="{MUTED}"> / </tspan><tspan fill="{GREEN}">MACHINE LEARNING</tspan></text>'''
    defs = CARD + BLUR + grad('accent', [(0, BLUE), (1, PURPLE)], 0, 1) + grad('accentX', [(0, BLUE), (1, PURPLE)])
    write('hero.svg', W, H, 'Mithil Batra — Software Engineer · CSE @ NIT Delhi', defs, CARD_CSS, card(W, H, (980, 160), body))


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
        ('cat oss.txt', [[('Merged: Mockito unit tests for ', FG), ('uber-doma-architecture', CYAN, True), (' (#995)', COMMENT)]]),
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
    defs, body = [], []
    for i, (value, suffix, label, color) in enumerate(tiles):
        x = i * (TW + GAP)
        chars = value + suffix
        widths = [13 if ch == '.' else 28 for ch in chars]
        cx = x + TW / 2 - sum(widths) / 2
        body.append(f'<rect x="{x + 1:.1f}" y="11" width="{TW - 2:.1f}" height="{TH}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
                    f'<rect x="{x + 24:.1f}" y="11" width="28" height="3" rx="1.5" fill="{color}"/>')
        col_delay = 0.3 + i * 0.25
        for j, (ch, cw) in enumerate(zip(chars, widths)):
            mid, cx = cx + cw / 2, cx + cw
            if ch.isdigit():
                d = int(ch)
                defs.append(f'<clipPath id="c{i}{j}"><rect x="{mid - cw / 2:.1f}" y="{BASE - 44}" width="{cw}" height="{HC}"/></clipPath>')
                strip = ''.join(f'<text x="{mid:.1f}" y="{BASE + k * HC}" text-anchor="middle">{k % 10}</text>' for k in range(20))
                body.append(f'<g clip-path="url(#c{i}{j})"><g class="roll" style="transform:translateY(-{(10 + d) * HC}px);animation-delay:{col_delay + j * 0.2:.2f}s">{strip}</g></g>')
            else:
                fill = f' fill="{color}"' if ch == '+' else ''
                body.append(f'<text x="{mid:.1f}" y="{BASE}" text-anchor="middle"{fill}>{ch}</text>')
        body.append(f'<text x="{x + TW / 2:.1f}" y="124" text-anchor="middle" class="lbl">{escape(label)}</text>')
    css = f'''
text {{ font-size: 44px; font-weight: 700; fill: {FG}; font-variant-numeric: tabular-nums; }}
.lbl {{ font-size: 13px; font-weight: 700; letter-spacing: 1.4px; fill: {COMMENT}; }}
.roll {{ animation: roll 2.4s cubic-bezier(.15,.75,.25,1) both; }}
@keyframes roll {{ from {{ transform: translateY(0); }} }}
'''
    write('stats.svg', W, H, '800+ DSA problems solved · 99.467 JEE Main percentile · 8.93 CGPA at NIT Delhi · JEE Advanced AIR 5376', ''.join(defs), css, ''.join(body))


def footer():
    W, H = 1200, 170
    body = f'''
<text x="600" y="68" text-anchor="middle" font-size="34" font-weight="600" fill="{FG}">Thanks for visiting</text>
<text x="600" y="106" text-anchor="middle" font-size="22" fill="{COMMENT}">Open to conversations about backend systems, machine learning and building products end to end.</text>
<text x="600" y="142" text-anchor="middle" class="mono" font-size="18" fill="{BLUE}">mithil.batra05@gmail.com · linkedin.com/in/mithilbatra211205</text>'''
    write('footer.svg', W, H, 'Thanks for visiting. Open to conversations about backend systems, machine learning and building products end to end. mithil.batra05@gmail.com', CARD + BLUR, CARD_CSS, card(W, H, (200, 20), body))


PROJECTS = [
    dict(file='pitwall', accent=RED, kicker='01 · MACHINE LEARNING', name='Pit Wall', url='mithil-f1-pitwall.duckdns.org', shot='pitwall.jpg',
         desc=['F1 podium prediction and analytics dashboard', 'built on live FastF1 timing and telemetry data.'],
         points=['Walk-forward backtests across 3 seasons', 'Random Forest vs gradient boosting', 'Live FastF1 ingestion, daily retraining'],
         stack=['Python', 'Flask', 'scikit-learn', 'FastF1', 'Docker']),
    dict(file='resolvr', accent=YELLOW, kicker='02 · MOBILE · INCIDENT RESPONSE', name='Resolvr', url=None, shot=None,
         desc=['Issue tracker plus incident escalation for', 'on-call teams: a mini Jira and mini xMatters.'],
         points=['Mobile Kanban boards for issues', 'Instant alerts, one-tap acknowledgment', 'Auto-escalation when nobody responds'],
         stack=['React Native', 'Expo', 'Node.js', 'Express', 'MongoDB']),
    dict(file='interviewer', accent=GREEN, kicker='03 · GENERATIVE AI', name='AI Mock Interviewer', url='automated-ai-interviewer-nbog.vercel.app', shot='interviewer.jpg',
         desc=['Mock interview platform that tailors questions', 'and grades answers with the Gemini API.'],
         points=['Questions tailored to role and experience', 'Gemini-graded answers with feedback', 'Sessions and scores stored in PostgreSQL'],
         stack=['Next.js', 'Tailwind CSS', 'Gemini API', 'PostgreSQL', 'Drizzle']),
]


def browser(x, y, w, url, shot):
    """Browser window framing a real screenshot of the live site (16:10)."""
    ih = w * 10 / 16
    data = base64.b64encode((OUT / 'shots' / shot).read_bytes()).decode()
    return (f'<clipPath id="shot"><path d="M{x} {y + 34}h{w}v{ih - 12}a12 12 0 0 1-12 12H{x + 12}a12 12 0 0 1-12-12z"/></clipPath>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{ih + 34}" rx="12" fill="{BG2}" stroke="{BORDER}" stroke-width="1.5"/>'
            + ''.join(f'<circle cx="{x + 20 + i * 18}" cy="{y + 17}" r="5.5" fill="{c}"/>' for i, c in enumerate((RED, YELLOW, GREEN)))
            + f'<rect x="{x + w / 2 - 150}" y="{y + 7}" width="300" height="20" rx="10" fill="{SURFACE}"/>'
            f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" class="mono" font-size="13" fill="{COMMENT}">{escape(url)}</text>'
            f'<image x="{x}" y="{y + 34}" width="{w}" height="{ih}" preserveAspectRatio="xMidYMin slice" clip-path="url(#shot)" href="data:image/jpeg;base64,{data}"/>')


def phone(cx, y):
    """Schematic of Resolvr's incidents screen, using the app's own status colours."""
    w, h = 236, 420
    x = cx - w / 2
    sx, sw = x + 12, w - 24
    cards = ''
    for i, (status, color, button) in enumerate([('ACTIVE', '#e74c3c', True), ('ACKNOWLEDGED', '#f39c12', False), ('RESOLVED', '#27ae60', False)]):
        cy = y + 118 + i * 92
        ch = 82 if button else 70
        cards += (f'<rect x="{sx + 10}" y="{cy}" width="{sw - 20}" height="{ch}" rx="8" fill="#fff"/>'
                  f'<rect x="{sx + 10}" y="{cy}" width="4" height="{ch}" rx="2" fill="{color}"/>'
                  f'<circle cx="{sx + 28}" cy="{cy + 16}" r="5" fill="{color}"/>'
                  f'<text x="{sx + 38}" y="{cy + 20}" font-size="10" font-weight="700" fill="{color}">{status}</text>'
                  f'<rect x="{sx + 24}" y="{cy + 32}" width="{sw - 60}" height="6" rx="3" fill="#bdc3c7"/>'
                  f'<rect x="{sx + 24}" y="{cy + 46}" width="{sw - 100}" height="6" rx="3" fill="#dfe4e6"/>')
        if button:
            cards += (f'<rect x="{sx + 24}" y="{cy + 58}" width="{sw - 48}" height="18" rx="9" fill="#e74c3c"/>'
                      f'<text x="{sx + sw / 2}" y="{cy + 71}" text-anchor="middle" font-size="9" font-weight="700" fill="#fff" letter-spacing="1">ACKNOWLEDGE</text>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="36" fill="#0b0d12" stroke="{BORDER}" stroke-width="2"/>'
            f'<clipPath id="screen"><rect x="{sx}" y="{y + 12}" width="{sw}" height="{h - 24}" rx="26"/></clipPath><g clip-path="url(#screen)">'
            f'<rect x="{sx}" y="{y + 12}" width="{sw}" height="{h - 24}" fill="#ecf0f1"/>'
            f'<rect x="{sx}" y="{y + 12}" width="{sw}" height="94" fill="#fff"/>'
            f'<rect x="{cx - 40}" y="{y + 20}" width="80" height="18" rx="9" fill="#0b0d12"/>'
            f'<text x="{sx + 16}" y="{y + 66}" font-size="17" font-weight="700" fill="#2c3e50">Incidents</text>'
            f'<text x="{sx + 16 + sw / 4}" y="{y + 96}" text-anchor="middle" font-size="11" font-weight="600" fill="#3498db">Active</text>'
            f'<text x="{sx + 16 + 3 * sw / 4 - 32}" y="{y + 96}" text-anchor="middle" font-size="11" fill="#7f8c8d">Past</text>'
            f'<rect x="{sx}" y="{y + 103}" width="{sw / 2}" height="3" fill="#3498db"/>'
            f'{cards}</g>')


def project_card(p):
    W, H = 1200, 480
    a = p['accent']
    body = [f'<text x="56" y="92" class="mono" font-size="15" letter-spacing="3" fill="{a}">{escape(p["kicker"])}</text>',
            f'<text x="56" y="146" font-size="44" font-weight="700" fill="{FG}">{escape(p["name"])}</text>']
    body += [f'<text x="56" y="{190 + i * 30}" font-size="21" fill="{COMMENT}">{escape(line)}</text>' for i, line in enumerate(p['desc'])]
    for i, point in enumerate(p['points']):
        y = 284 + i * 36
        body.append(f'<circle cx="62" cy="{y - 7}" r="4.5" fill="{a}"/><text x="80" y="{y}" font-size="19" fill="{FG}">{escape(point)}</text>')
    x, y = 56, 392
    for name in p['stack']:
        w = len(name) * 9.4 + 32
        if x + w > 560:
            x, y = 56, y + 42
        body.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="34" rx="17" fill="{a}" fill-opacity=".1" stroke="{a}" stroke-opacity=".45"/>'
                    f'<text x="{x + w / 2:.0f}" y="{y + 23}" text-anchor="middle" font-size="16" fill="{FG}">{escape(name)}</text>')
        x += w + 8
    if p['shot']:
        body.append(browser(588, 44, 572, p['url'], p['shot']))
    else:
        body.append(phone(874, 30))
        body.append(f'<text x="1026" y="466" class="mono" font-size="13" fill="{MUTED}">illustration</text>')
    label = f'{p["name"]}: {" ".join(p["desc"])} ' + '; '.join(p['points']) + '. Built with ' + ', '.join(p['stack']) + '.'
    write(f'project-{p["file"]}.svg', W, H, label, CARD + BLUR, '', card(W, H, (990, 240), ''.join(body), tint=a))


def projects():
    for p in PROJECTS:
        project_card(p)


STATS_QUERY = """query($login: String!) { user(login: $login) {
  repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) { totalCount nodes { stargazerCount
    languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } } } }
  contributionsCollection { totalCommitContributions contributionCalendar { totalContributions } }
  pullRequests(states: MERGED) { totalCount } } }"""


def fetch_stats(login, token):
    req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': STATS_QUERY, 'variables': {'login': login}}).encode(),
                                 {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if 'errors' in data:
        raise SystemExit(f'GitHub API error: {data["errors"]}')
    return data['data']['user']


def github_stats(user):
    W, H = 860, 210
    repos = user['repositories']
    langs = {}
    for repo in repos['nodes']:
        for e in repo['languages']['edges']:
            name, color = e['node']['name'], e['node']['color'] or COMMENT
            size, _ = langs.get(name, (0, color))
            langs[name] = (size + e['size'], color)
    total = sum(size for size, _ in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    cc = user['contributionsCollection']
    rows = [('Contributions (last year)', cc['contributionCalendar']['totalContributions']),
            ('Commits (last year)', cc['totalCommitContributions']),
            ('Merged pull requests', user['pullRequests']['totalCount']),
            ('Public repositories', repos['totalCount'])]
    body = [f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>',
            f'<text x="32" y="42" class="h">GitHub activity</text><text x="452" y="42" class="h">Top languages</text>',
            f'<line x1="420" y1="28" x2="420" y2="{H - 28}" stroke="{BORDER}"/>']
    for i, (label, value) in enumerate(rows):
        y = 84 + i * 32
        body.append(f'<text x="32" y="{y}" class="k">{label}</text><text x="388" y="{y}" text-anchor="end" class="v">{value:,}</text>')
    x = 452.0
    body.append(f'<clipPath id="bar"><rect x="452" y="62" width="376" height="10" rx="5"/></clipPath><g clip-path="url(#bar)">')
    for name, (size, color) in top:
        w = 376 * size / total
        body.append(f'<rect x="{x:.1f}" y="62" width="{w + 0.5:.1f}" height="10" fill="{color}"/>')
        x += w
    body.append(f'<rect x="{x:.1f}" y="62" width="{828 - x:.1f}" height="10" fill="{SURFACE}"/></g>')
    for i, (name, (size, color)) in enumerate(top):
        lx, ly = 452 + (i % 2) * 200, 106 + (i // 2) * 30
        body.append(f'<circle cx="{lx + 5}" cy="{ly - 5}" r="5" fill="{color}"/>'
                    f'<text x="{lx + 18}" y="{ly}" class="k">{escape(name)}<tspan class="p" dx="6">{100 * size / total:.1f}%</tspan></text>')
    css = f'''
.h {{ font-size: 18px; font-weight: 600; fill: {FG}; }}
.k {{ font-size: 15px; fill: {COMMENT}; }}
.v {{ font-size: 17px; font-weight: 600; fill: {FG}; font-variant-numeric: tabular-nums; }}
.p {{ font-size: 14px; fill: {MUTED}; font-variant-numeric: tabular-nums; }}
'''
    label = 'GitHub activity: ' + ', '.join(f'{k} {v}' for k, v in rows) + '. Top languages: ' + ', '.join(n for n, _ in top)
    write('github-stats.svg', W, H, label, '', css, ''.join(body))


if __name__ == '__main__':
    if sys.argv[1:2] == ['--github-stats']:
        OUT = Path(sys.argv[2])
        OUT.mkdir(parents=True, exist_ok=True)
        github_stats(fetch_stats(os.environ.get('GITHUB_REPOSITORY_OWNER', 'Mithilbatra'), os.environ['GITHUB_TOKEN']))
    else:
        for build in (hero, terminal, stats, projects, footer):
            build()
    print('wrote', ', '.join(sorted(p.name for p in OUT.glob('*.svg'))))
