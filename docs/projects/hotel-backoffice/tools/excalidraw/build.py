#!/usr/bin/env python3
"""Build an Excalidraw board from a JSON spec + the screenshots in ../../screens/.

    python3 build.py <spec.json> <out.excalidraw>

The output embeds every screenshot (live guest data), so it is written to
../../board/, which is gitignored. The spec and this script are safe to commit.

Spec shape:
{
  "title": "...", "subtitle": "...",
  "imageWidth": 600,          # width of each screenshot on the canvas
  "maxImageHeight": 900,      # taller screenshots are cropped from the top
  "sections": [
    {"name": "...", "items": [{"screen": "fd-room-map", "caption": "..."}],
     "arrows": true,          # connect items left to right
     "panel": "optional free text shown after the last item",
     "note": "optional one-line subtitle under the section name"}
  ]
}
"""
import base64, hashlib, io, json, random, sys, time
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SCREENS = HERE.parent.parent / 'screens'
CACHE = HERE.parent.parent / 'board' / '.cache'

FONT = 2            # Helvetica: legible, supported by every Excalidraw version
INK = '#1e1e1e'
MUTED = '#495057'
SOURCE_PX = 1000    # stored resolution: sharp when zoomed in, small on disk

NOW = int(time.time() * 1000)
_ids = 0


def uid(prefix):
    global _ids
    _ids += 1
    return f'{prefix}-{_ids}'


def base(kind, x, y, w, h, **kw):
    el = {
        'id': uid(kind), 'type': kind, 'x': x, 'y': y, 'width': w, 'height': h,
        'angle': 0, 'strokeColor': INK, 'backgroundColor': 'transparent',
        'fillStyle': 'solid', 'strokeWidth': 1, 'strokeStyle': 'solid',
        'roughness': 0, 'opacity': 100, 'groupIds': [], 'frameId': None,
        'roundness': None, 'seed': random.randint(1, 2**31), 'version': 1,
        'versionNonce': random.randint(1, 2**31), 'isDeleted': False,
        'boundElements': [], 'updated': NOW, 'link': None, 'locked': False,
    }
    el.update(kw)
    return el


_font_cache = {}


def _measure(line, size):
    """Width of a line in px. Measured with the real font — estimating by character
    count clips capitals, which Excalidraw then renders cut off."""
    if size not in _font_cache:
        try:
            from PIL import ImageFont
            _font_cache[size] = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', size)
        except Exception:
            _font_cache[size] = None
    font = _font_cache[size]
    if font is None:
        return len(line) * size * 0.62
    return font.getlength(line)


def _wrap(paragraph, size, width):
    if not paragraph:
        return ['']
    out, line = [], ''
    for word in paragraph.split(' '):
        trial = f'{line} {word}'.strip()
        if line and _measure(trial, size) > width:
            out.append(line)
            line = word
        else:
            line = trial
    out.append(line)
    return out


def text(x, y, s, size=16, width=None, color=INK):
    """Pre-wrapped text; width only drives where the line breaks go."""
    if width:
        s = '\n'.join('\n'.join(_wrap(p, size, width)) for p in s.split('\n'))
    lines = s.split('\n')
    w = max(_measure(l, size) for l in lines) + size * 0.6   # trailing slack
    h = len(lines) * size * 1.25
    return base('text', x, y, w, h, text=s, originalText=s, fontSize=size,
                fontFamily=FONT, textAlign='left', verticalAlign='top',
                containerId=None, lineHeight=1.25, autoResize=True,
                strokeColor=color)


def prep_image(screen, display_w, max_display_h):
    """Resize to SOURCE_PX wide, crop from the top if too tall, return (file, display_h)."""
    src = SCREENS / f'{screen}.png'
    im = Image.open(src).convert('RGB')
    im = im.resize((SOURCE_PX, round(im.height * SOURCE_PX / im.width)), Image.LANCZOS)
    max_src_h = round(max_display_h * SOURCE_PX / display_w)
    cropped = im.height > max_src_h
    if cropped:
        im = im.crop((0, 0, SOURCE_PX, max_src_h))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=72, optimize=True)
    data = buf.getvalue()
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f'{screen}.jpg').write_bytes(data)
    file_id = hashlib.sha1(data).hexdigest()
    files_entry = {'mimeType': 'image/jpeg', 'id': file_id, 'created': NOW,
                   'dataURL': 'data:image/jpeg;base64,' + base64.b64encode(data).decode()}
    return files_entry, round(im.height * display_w / SOURCE_PX), cropped


def arrow(a, b):
    y = a['y'] + min(a['height'], b['height']) / 2
    x0, x1 = a['x'] + a['width'] + 12, b['x'] - 12
    el = base('arrow', x0, y, x1 - x0, 0, points=[[0, 0], [x1 - x0, 0]],
              strokeWidth=2, lastCommittedPoint=None, startArrowhead=None,
              endArrowhead='arrow', elbowed=False,
              startBinding={'elementId': a['id'], 'focus': 0, 'gap': 12},
              endBinding={'elementId': b['id'], 'focus': 0, 'gap': 12})
    a['boundElements'].append({'type': 'arrow', 'id': el['id']})
    b['boundElements'].append({'type': 'arrow', 'id': el['id']})
    return el


def build(spec):
    W = spec.get('imageWidth', 600)
    MAXH = spec.get('maxImageHeight', 900)
    GAP, PAD, SECTION_GAP = 120, 60, 160
    elements, files = [], {}

    y = 0
    elements.append(text(0, y, spec['title'], size=44))
    y += 70
    if spec.get('subtitle'):
        sub = text(0, y, spec['subtitle'], size=18, width=1800, color=MUTED)
        elements.append(sub)
        y += sub['height'] + 40
    y += 40

    for sec in spec['sections']:
        children = []
        head = text(PAD, y + 40, sec['name'], size=30)
        children.append(head)
        top = head['y'] + head['height'] + 16
        if sec.get('note'):
            note = text(PAD, top, sec['note'], size=18, width=1600, color=MUTED)
            children.append(note)
            top += note['height'] + 16
        top += 24

        x, bottom, imgs = PAD, top, []
        for it in sec['items']:
            f, h, cropped = prep_image(it['screen'], W, MAXH)
            files[f['id']] = f
            img = base('image', x, top, W, h, fileId=f['id'], status='saved',
                       scale=[1, 1], crop=None, strokeColor='transparent')
            img['customData'] = {'screen': it['screen']}
            cap_txt = it.get('caption', '')
            if cropped:
                cap_txt += '\n(long page, top shown)'
            cap = text(x, top + h + 16, f"{it['screen']}\n{cap_txt}".strip(), size=16, width=W)
            children += [img, cap]
            imgs.append(img)
            bottom = max(bottom, cap['y'] + cap['height'])
            x += W + GAP

        if sec.get('arrows', True):
            for a, b in zip(imgs, imgs[1:]):
                children.append(arrow(a, b))

        if sec.get('panel'):
            panel = text(x, top, sec['panel'], size=17, width=sec.get('panelWidth', 620))
            children.append(panel)
            bottom = max(bottom, panel['y'] + panel['height'])
            x += sec.get('panelWidth', 620) + GAP

        fw, fh = x - GAP + PAD, bottom - y + PAD
        frame = base('frame', 0, y, fw, fh, name=sec['name'], strokeColor='#bbbbbb')
        for c in children:
            c['frameId'] = frame['id']
        elements += children + [frame]
        y += fh + SECTION_GAP

    return {'type': 'excalidraw', 'version': 2, 'source': 'ctrl/hotel-backoffice/tools/excalidraw',
            'elements': elements,
            'appState': {'viewBackgroundColor': '#ffffff', 'gridSize': None},
            'files': files}


if __name__ == '__main__':
    spec_path, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    board = build(json.loads(spec_path.read_text()))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(board, ensure_ascii=False))
    kinds = {}
    for e in board['elements']:
        kinds[e['type']] = kinds.get(e['type'], 0) + 1
    print(f"{out_path}  {out_path.stat().st_size / 1e6:.1f} MB  {kinds}  images={len(board['files'])}")
