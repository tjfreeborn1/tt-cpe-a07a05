* gate drive ff 125
.lib /home/claude/pdk/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice ff
.include ../../pex/top_pex.spice
.temp 125
.option rshunt=1e12
Vdd vdd 0 1.62
VA a 0 1.0
VB b 0 1.0
Vin in 0 pulse(0 1.62 10n 2n 2n 400n 1u)
X1 a b in in in in in in in in in in vdd 0 toppex
.control
tran 0.1n 900n
meas tran g4hi find v(x1.swA4/G) at=400n
meas tran g0hi find v(x1.swA0/G) at=400n
meas tran t4r when v(x1.swA4/G)=1.54 rise=1
meas tran t0r when v(x1.swA0/G)=1.54 rise=1
meas tran tb4r when v(x1.swB4/G)=1.54 rise=1
meas tran g4lo find v(x1.swA4/G) at=890n
meas tran t4f when v(x1.swA4/G)=0.08 fall=1
meas tran idd avg i(Vdd) from=300n to=400n
.endc
.end
