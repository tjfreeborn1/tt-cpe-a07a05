"""Keysight E4990A impedance accuracy, data-sheet Equation 1 (four-terminal-pair port).

acc(fm, Zx, vmv, mt=5, cable=1) -> |Z| accuracy in %; the phase accuracy is acc/100 rad.
fm: frequency in Hz, Zx: |Z| in ohm, vmv: oscillator level in mVrms, mt: measurement-time mode, cable: 0/1/2 m.
These are the guaranteed limits after open/short compensation.
"""
def acc(fm,Zx,vmv,mt=5,cable=1):
    # Equation 1, four-terminal-pair port (E4990A data sheet); E [%] = Ep + (Zs/|Zx| + Yo*|Zx|)*100
    F=fm/1e6
    Epl={0:0,1:0.02+2*F/100,2:0.02+3*F/100}[cable]
    Epbw={5:0,4:0.06 if fm<50e3 else 0.03,3:0.2 if fm<50e3 else 0.1}[mt]
    Eposc=(100/vmv-1)*(0.018+Epbw) if vmv<=100 else 0.018*(200/vmv-1)
    Ep=0.5 if fm<100 else 0.3 if fm<=800 else 0.075 if fm<=1e6 else 0.1*F
    Yol={0:0,1:500e-9*F/100,2:1e-6*F/100}[cable]
    Yo=10e-9 if fm<100 else 2.5e-9 if fm<=200e3 else 5e-9 if fm<=1e6 else 50e-9
    Kbw={5:1,4:1,3:3 if fm<=1e6 else 4}[mt]; Kyosc=500/vmv if vmv<=500 else 1000/vmv
    Kzosc=100/vmv if vmv<=100 else 200/vmv if vmv<=200 else 1
    Zsl=0 if cable==0 else (5e-3 if fm<500 else 2e-3); Zs=10e-3 if fm<100 else 2.5e-3
    YoI=Yol+Kbw*Kyosc*Yo; ZsI=Zsl+Kbw*Kzosc*Zs
    return Epl+Epbw+Eposc+Ep+(ZsI/Zx+YoI*Zx)*100
