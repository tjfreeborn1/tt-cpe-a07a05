"""Tiny helper to emit Magic Tcl. Coordinates in um; converted to internal units (0.005 um)."""
G = 0.005
def iu(x): return int(round(x / G))
class Tcl:
    def __init__(s): s.l = ['snap internal', 'tech unlock *']
    def __call__(s, line): s.l.append(line)
    def rect(s, layer, x1, y1, x2, y2):
        if x2 < x1: x1, x2 = x2, x1
        if y2 < y1: y1, y2 = y2, y1
        s.l.append(f'box values {iu(x1)} {iu(y1)} {iu(x2)} {iu(y2)}; paint {layer}')
    def erase(s, layer, x1, y1, x2, y2):
        s.l.append(f'box values {iu(x1)} {iu(y1)} {iu(x2)} {iu(y2)}; erase {layer}')
    def label(s, layer, x, y, text, port=None, w=0.2):
        s.l.append(f'box values {iu(x-w/2)} {iu(y-w/2)} {iu(x+w/2)} {iu(y+w/2)}; label {text} FreeSans 0.25u -{layer}')
        if port is not None: s.l.append(f'port make {port}')
    def gencell(s, dev, name, x, y, params):
        s.l.append(f'box values {iu(x)} {iu(y)} {iu(x)} {iu(y)}')
        s.l.append(f'eval magic::gencell sky130::{dev} {name} {{{params}}}')
    def write(s, fn): open(fn, 'w').write('\n'.join(s.l) + '\n')
