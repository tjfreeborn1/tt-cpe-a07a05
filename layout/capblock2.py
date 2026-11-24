"""Network capacitor block: MOS rows (W=10/L=10 fingers) + MIM bands per branch + 5-bit trim bank band.
Block-local frame: rows from x=0, y=0; branch buses (met2 columns) and bank exits on the LEFT (x<0)."""
import math
from maglib import Tcl
FP, RH = 10.29, 10.59
CA, CPP = 2.000e-3, 0.165e-3          # MIM pF/um2, pF/um (perimeter) from the ngspice model
G = 0.84                               # capm spacing (same plate)
def roww(n): return FP * n + 0.29
def sd_x(k): return FP * k + 0.145
def cmim(w, h): return CA * w * h + CPP * 2 * (w + h)
def r2(x, q=0.01): return round(x / q) * q
def tile_band(Wt, Ctarget, smax=30.0):
    """tiles across width Wt with equal size, as few rows as possible; returns (nx, ny, sx, sy, height)"""
    nx = max(1, math.ceil((Wt + G) / (smax + G))); sx = r2((Wt - (nx - 1) * G) / nx - 0.005)
    for ny in range(1, 50):
        # solve sy: nx*ny*cmim(sx, sy) = Ctarget
        a = nx * ny * (CA * sx + 2 * CPP); b = nx * ny * 2 * CPP * sx
        sy = (Ctarget - b) / a
        if sy <= smax: 
            sy = r2(sy); return nx, ny, sx, sy, ny * sy + (ny - 1) * G
    raise ValueError
def solve_w(C, h):
    return r2((C - 2 * CPP * h) / (CA * h + 2 * CPP))

def build(t: Tcl, branches, N, P=10.8, keep_right=0.0, bank=True, tag='x', bank_cw=29.8):
    """branches: list of dict(name, units, cmim[pF]); returns info dict (block-local coordinates)."""
    B = len(branches)
    rows = []
    for bi, b in enumerate(branches):
        u = b['units']
        while u > 0:
            nf = min(N, u); rows.append((bi, nf)); u -= nf
    R = len(rows); Wr = roww(N)
    # paired rows: even rows gate-on-top, odd rows gate-on-bottom (gates face each other);
    # a p-tap strip between pairs keeps every n-diff within 15 um of a tap (LU.2)
    ys = [0.0]; taps = []
    for r in range(1, R):
        if r % 2 == 1: ys.append(ys[-1] + 10.88)
        else:
            taps.append(ys[-1] + 10.71); ys.append(ys[-1] + 11.26)
    top = ys[-1] + RH
    def gate_y(r): return (ys[r] + 10.29, ys[r] + 10.52) if r % 2 == 0 else (ys[r] + 0.05, ys[r] + 0.28)
    def sd_y(r): return (ys[r] + 0.13, ys[r] + 10.13) if r % 2 == 0 else (ys[r] + 0.44, ys[r] + 10.44)
    busx = [-1.25 - 0.9 * k for k in range(B)]                 # bus column centres (met2, 0.5 wide)
    xl = busx[-1] - 0.25 - 0.9 - 0.6                            # ring left (outer edge)
    xr = Wr + 0.8; yb = -1.4; yt = top + 0.8
    info = dict(R=R, W=Wr, top=top, ring=(xl, yb, xr + 0.6, yt + 0.6), busx=busx, branches=[], ys=ys, taps=taps)
    # ---------------- MOS rows
    for r, (bi, nf) in enumerate(rows):
        y = ys[r]
        opt = 'topc 1 botc 0' if r % 2 == 0 else 'topc 0 botc 1'
        t.gencell('sky130_fd_pr__nfet_01v8', f'{tag}r{r}', 0, y, f'w 10 l 10 nf {nf} m 1 guard 0 {opt} conn_gates 1 full_metal 1')
        s1, s2 = sd_y(r)
        for k in range(nf + 1):
            c = sd_x(k)
            t.rect('metal1', c - 0.17, s1, c + 0.17, s2)
            t.rect('via1', c - 0.17, s1 + 0.47, c + 0.17, s2 - 0.47)
        bx = busx[bi]; g1, g2 = gate_y(r)
        t.rect('metal1', bx - 0.25, g1, 0.6, g2)
        t.rect('via1', bx - 0.2, g1 - 0.05, bx + 0.2, g2 + 0.05)   # gate strip -> bus
        t.rect('metal1', bx - 0.25, g1 - 0.1, bx + 0.25, g2 + 0.1)
    # ---------------- tap strips between row pairs (psubdiff + li), joined to the ring
    for ty in taps:
        t.rect('psubdiff', xl + 0.6, ty, xr, ty + 0.41)
        t.rect('psubdiffcont', xl + 0.7, ty + 0.12, xr - 0.1, ty + 0.29)
        t.rect('locali', xl + 0.6, ty + 0.04, xr, ty + 0.37)
    # ---------------- guard ring
    for (x1, y1, x2, y2) in ((xl, yb, xr + 0.6, yb + 0.6), (xl, yt, xr + 0.6, yt + 0.6), (xl, yb, xl + 0.6, yt + 0.6), (xr, yb, xr + 0.6, yt + 0.6)):
        for L in ('psubdiff', 'locali', 'metal1'): t.rect(L, x1, y1, x2, y2)
    for (x1, y1, x2, y2) in ((xl + 0.3, yb + 0.15, xr + 0.3, yb + 0.45), (xl + 0.3, yt + 0.15, xr + 0.3, yt + 0.45), (xl + 0.15, yb + 0.3, xl + 0.45, yt + 0.3), (xr + 0.15, yb + 0.3, xr + 0.45, yt + 0.3)):
        t.rect('psubdiffcont', x1, y1, x2, y2); t.rect('viali', x1, y1, x2, y2)
    # ---------------- MIM bands
    X0 = 1.2; Wt = Wr - 1.4 - keep_right
    ty0 = yb + 0.75; ty1 = yt - 0.15
    y = ty0
    bankinfo = None
    if bank:
        cw = bank_cw; ch = r2((1.2 - 2 * CPP * cw) / (CA * cw + 2 * CPP))
        w1 = solve_w(0.6, ch); w0 = solve_w(0.3, ch)
        GB = 2.28                                   # capm spacing between different bits (islands 0.94 + 0.4 gap)
        tail_gap = 1.34 + 3 * 0.4 + 2 * 0.4 + 1.34  # three exit tails between the two rows
        row1 = [(4, 4, cw)]                          # (bit, ncells, width)
        row2 = [(3, 2, cw), (2, 1, cw), (1, 1, w1), (0, 1, w0)]
        need = max(4 * cw + 3 * G, 3 * cw + G + w1 + w0 + 3 * GB)
        if need > Wt: raise ValueError(f'bank row {need:.1f} > {Wt:.1f}')
        tiles_b = {}
        ya = y + 0.94; yr2 = ya; yr1 = ya + ch + tail_gap
        x = X0
        for (bit, n, w) in row2:
            tiles_b[bit] = [(x + i * (w + G), yr2, w, ch) for i in range(n)]
            x += n * w + (n - 1) * G + GB
        x = X0
        tiles_b[4] = [(x + i * (cw + G), yr1, cw, ch) for i in range(4)]
        band_top = yr1 + ch + 0.94                   # island top
        # islands (met3) + tails, mimcap, contacts
        islands = {}
        for bit, tl in tiles_b.items():
            x1 = min(a for a, _, _, _ in tl) - 0.94; x2 = max(a + w for a, _, w, _ in tl) + 0.94
            y1 = tl[0][1] - 0.94; y2 = tl[0][1] + ch + 0.94
            islands[bit] = (x1, y1, x2, y2)
            t.rect('metal3', x1, y1, x2, y2)
            for (a, b_, w, h) in tl:
                t.rect('mimcap', a, b_, a + w, b_ + h); t.rect('mimcapcontact', a + 0.2, b_ + 0.2, a + w - 0.2, b_ + h - 0.2)
        exitx = xl - 1.0
        # bit3 (row2 leftmost) and bit4 (row1) exit directly left; bits 2,1,0 use tails in the gap
        exits = {}
        x1, y1, x2, y2 = islands[4]; t.rect('metal3', exitx, y1 + 2.0, x1 + 0.5, y1 + 2.6); exits[4] = (exitx, y1 + 2.3)
        x1, y1, x2, y2 = islands[3]; t.rect('metal3', exitx, y1 + 2.0, x1 + 0.5, y1 + 2.6); exits[3] = (exitx, y1 + 2.3)
        gy0 = yr2 + ch + 1.34
        for j, bit in enumerate((2, 1, 0)):
            ty = gy0 + j * 0.8
            x1, y1, x2, y2 = islands[bit]
            t.rect('metal3', x1 + 0.5, y2 - 0.5, x1 + 0.9, ty + 0.4)      # riser from island to tail
            t.rect('metal3', exitx, ty, x1 + 0.9, ty + 0.4); exits[bit] = (exitx, ty + 0.2)
        # top plate sheet (t)
        tsheet = (exitx, y, Wr + 1.0, band_top)
        t.rect('metal4', *tsheet)
        bankinfo = dict(ch=ch, cw=cw, w1=w1, w0=w0, exits=exits, tsheet=tsheet, band_top=band_top,
                        C={4: 4 * cmim(cw, ch), 3: 2 * cmim(cw, ch), 2: cmim(cw, ch), 1: cmim(w1, ch), 0: cmim(w0, ch)})
        y = band_top + 0.4 + 0.94           # plane starts at band_top+0.4; network capm >= 1.34 from islands
        plane_y0 = band_top + 0.4
    else:
        plane_y0 = yb
    info['bank'] = bankinfo
    # met3 ground plane
    t.rect('metal3', 0.1, plane_y0, xr + 0.6, yt + 0.6)
    # branch bands
    bands = []
    for bi, b in enumerate(branches):
        nx, ny, sx, sy, h = tile_band(Wt, b['cmim'])
        y1 = y; y2 = y + h
        tl = [(X0 + i * (sx + G), y1 + j * (sy + G), sx, sy) for i in range(nx) for j in range(ny)]
        for (a, b_, w, hh) in tl:
            t.rect('mimcap', a, b_, a + w, b_ + hh); t.rect('mimcapcontact', a + 0.2, b_ + 0.2, a + w - 0.2, b_ + hh - 0.2)
        bands.append(dict(y1=y1, y2=y2, tiles=tl, sx=sx, sy=sy, n=nx * ny, C=nx * ny * cmim(sx, sy)))
        y = y2 + 1.24                       # band gap (capm 0.84 + met4 0.4 rule room)
    if y - 1.24 > ty1: raise ValueError(f'MIM bands overflow: need {y - 1.24 - ty0:.1f}, have {ty1 - ty0:.1f}')
    info['mim_spare'] = ty1 - (y - 1.24)
    # met4 sheets: split the space between bands evenly
    edges = [plane_y0 + 0.2] + [(bands[i]['y2'] + bands[i + 1]['y1']) / 2 for i in range(B - 1)] + [yt + 0.6]
    r0 = 0
    for bi, b in enumerate(branches):
        nr = sum(1 for (x, _) in rows if x == bi)
        gy1 = min(gate_y(r0)[0], gate_y(r0 + nr - 1)[0]); gy2 = max(gate_y(r0)[1], gate_y(r0 + nr - 1)[1])
        s1 = edges[bi] + 0.2; s2 = edges[bi + 1] - 0.2
        sheet_x1 = busx[bi] - 0.45
        t.rect('metal4', sheet_x1, s1, Wr + 1.0, s2)
        # via stack at bus column inside the band (met3 island must avoid plane: plane starts at x=0.1)
        vy = min(max(s1 + 0.6, min(gy2, s2 - 3.0)), s2 - 3.0)
        bx = busx[bi]
        t.rect('metal2', bx - 0.25, min(gy1, vy) - 0.1, bx + 0.25, max(gy2, vy + 1.6) + 0.1)    # bus column
        t.rect('metal3', bx - 0.35, vy + 0.2, bx + 0.35, vy + 2.6)
        t.rect('via2', bx - 0.2, vy + 0.4, bx + 0.2, vy + 1.0)
        t.rect('via3', bx - 0.2, vy + 1.6, bx + 0.2, vy + 2.3)
        info['branches'].append(dict(name=b['name'], units=b['units'], rows=nr, bus=(bx, min(gy1, vy), max(gy2, vy + 1.6)), island=(bx - 0.35, vy + 0.2, bx + 0.35, vy + 2.6),
                                     sheet=(sheet_x1, s1, Wr + 1.0, s2), mim=bands[bi]))
        r0 += nr
    # ground columns (met2), via1 to ring, via2 to plane in gaps between capm rows
    capbands = sorted([(b_, b_ + hh) for bd in bands for (_, b_, _, hh) in bd['tiles']])
    free = []; cur = plane_y0 + 0.1
    for (y1, y2) in capbands:
        if y1 - cur >= 0.3 + 2 * 0.13: free.append((cur + 0.13, y1 - 0.13))
        cur = max(cur, y2)
    if yt + 0.55 - cur >= 0.56: free.append((cur + 0.13, yt + 0.55))
    for k in range(N + 1):
        c = sd_x(k)
        t.rect('metal2', c - 0.17, yb, c + 0.17, yt + 0.6)
        t.rect('via1', c - 0.17, yb + 0.05, c + 0.17, yb + 0.55)
        t.rect('via1', c - 0.17, yt + 0.05, c + 0.17, yt + 0.55)
        if k > 0:
            for (f1, f2) in free: t.rect('via2', c - 0.17, f1, c + 0.17, f2)
    info['via2_bands'] = free
    info['rows_list'] = rows
    return info
