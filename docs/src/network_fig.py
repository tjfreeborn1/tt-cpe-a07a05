"""Datasheet figure: generic network schematic (one per pin). Run from the repo root: writes docs/network.png."""
import schemdraw, schemdraw.elements as elm
schemdraw.config(fontsize=17, font='DejaVu Sans', margin=0.6)
H = 6.0
X = dict(Rp=2.0, b1=4.0, b2=6.0, dots=7.5, bN=9.0, t0=11.6, t1=13.8, tdots=15.4, t4=17.0)
with schemdraw.Drawing(file='docs/network.png', dpi=110, show=False) as d:
    d += elm.Dot(open=True).at((0, 0)).label('ua pin', loc='left')
    d += elm.Line().at((0, 0)).to((X['t4'], 0))
    d += elm.Line().at((X['Rp'], -H)).to((X['t4'], -H))
    d += elm.Ground().at((X['Rp'], -H))
    d += elm.Dot().at((X['Rp'], 0))
    d += elm.Resistor().at((X['Rp'], 0)).down().length(H).label('Rp', loc='bottom')
    for key, n in (('b1', '1'), ('b2', '2'), ('bN', 'N')):
        x = X[key]
        d += elm.Dot().at((x, 0))
        d += elm.Resistor().at((x, 0)).down().length(H / 2).label(f'R{n}', loc='bottom')
        d += elm.Capacitor().down().length(H / 2).label(f'C{n}', loc='bottom')
        d += elm.Dot().at((x, -H))
    d += elm.Label().at((X['dots'], -H / 2)).label('· · ·', fontsize=20)
    for key, k in (('t0', 0), ('t1', 1), ('t4', 4)):
        x = X[key]
        if k < 4: d += elm.Dot().at((x, 0))
        d += elm.Capacitor().at((x, 0)).down().length(H / 2).label(f'{0.3 * 2 ** k:.1f} pF', loc='bottom')
        d += elm.Switch().down().length(H / 2).label(f'bit {k}', loc='bottom')
        if k < 4: d += elm.Dot().at((x, -H))
    d += elm.Label().at((X['tdots'], -H / 2)).label('· · ·', fontsize=20)
    d += elm.Label().at(((X['b1'] + X['bN']) / 2, 1.1)).label('RC branches, k = 1 … N', fontsize=16)
    d += elm.Label().at(((X['t0'] + X['t4']) / 2, 1.1)).label('5-bit trim bank', fontsize=16)
