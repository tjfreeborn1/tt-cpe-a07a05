v {xschem version=3.4.8RC file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tt_um_tjfreeborn1_cpe_a07a05: fractional-order capacitors (CPE) alpha=0.7 on ua[0], alpha=0.5 on ua[1], 5-bit trim banks} -400 -500 0 0 0.4 0.4 {}
C {ipin.sym} -900 -400 0 0 {name=l1 sig_type=std_logic lab=VGND}
C {ipin.sym} -900 -360 0 0 {name=l2 sig_type=std_logic lab=VDPWR}
C {ipin.sym} -900 -320 0 0 {name=l3 sig_type=std_logic lab=ui_in[7:0]}
C {ipin.sym} -900 -280 0 0 {name=l4 sig_type=std_logic lab=uio_in[7:0]}
C {ipin.sym} -900 -240 0 0 {name=l5 sig_type=std_logic lab=ena}
C {ipin.sym} -900 -200 0 0 {name=l6 sig_type=std_logic lab=clk}
C {ipin.sym} -900 -160 0 0 {name=l7 sig_type=std_logic lab=rst_n}
C {opin.sym} -900 0 0 0 {name=l8 sig_type=std_logic lab=uo_out[7:0]}
C {opin.sym} -900 40 0 0 {name=l9 sig_type=std_logic lab=uio_out[7:0]}
C {opin.sym} -900 80 0 0 {name=l10 sig_type=std_logic lab=uio_oe[7:0]}
C {iopin.sym} -900 200 0 0 {name=l11 sig_type=std_logic lab=ua[7:0]}
C {cpe_a07.sym} 0 -300 0 0 {name=xcpe07}
C {lab_pin.sym} -80 -310 0 0 {name=l12 sig_type=std_logic lab=ua[0]}
C {lab_pin.sym} 80 -310 0 1 {name=l13 sig_type=std_logic lab=VGND}
C {cpe_a05.sym} 0 0 0 0 {name=xcpe05}
C {lab_pin.sym} -80 -10 0 0 {name=l14 sig_type=std_logic lab=ua[1]}
C {lab_pin.sym} 80 -10 0 1 {name=l15 sig_type=std_logic lab=VGND}
C {trimbank.sym} 400 -300 0 0 {name=xbank07}
C {lab_pin.sym} 320 -350 0 0 {name=l16 sig_type=std_logic lab=ua[0]}
C {lab_pin.sym} 480 -250 0 1 {name=l17 sig_type=std_logic lab=VGND}
C {lab_pin.sym} 480 -350 0 1 {name=l18 sig_type=std_logic lab=gA0}
C {lab_pin.sym} 480 -330 0 1 {name=l19 sig_type=std_logic lab=gA1}
C {lab_pin.sym} 480 -310 0 1 {name=l20 sig_type=std_logic lab=gA2}
C {lab_pin.sym} 480 -290 0 1 {name=l21 sig_type=std_logic lab=gA3}
C {lab_pin.sym} 480 -270 0 1 {name=l22 sig_type=std_logic lab=gA4}
C {trimbank.sym} 400 0 0 0 {name=xbank05}
C {lab_pin.sym} 320 -50 0 0 {name=l23 sig_type=std_logic lab=ua[1]}
C {lab_pin.sym} 480 50 0 1 {name=l24 sig_type=std_logic lab=VGND}
C {lab_pin.sym} 480 -50 0 1 {name=l25 sig_type=std_logic lab=gB0}
C {lab_pin.sym} 480 -30 0 1 {name=l26 sig_type=std_logic lab=gB1}
C {lab_pin.sym} 480 -10 0 1 {name=l27 sig_type=std_logic lab=gB2}
C {lab_pin.sym} 480 10 0 1 {name=l28 sig_type=std_logic lab=gB3}
C {lab_pin.sym} 480 30 0 1 {name=l29 sig_type=std_logic lab=gB4}
C {sky130_stdcells/buf_2.sym} 900 -300 0 0 {name=xbufA0 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 -300 0 0 {name=l30 sig_type=std_logic lab=ui_in[0]}
C {lab_pin.sym} 940 -300 0 1 {name=l31 sig_type=std_logic lab=gA0}
C {sky130_stdcells/buf_2.sym} 1200 -300 0 0 {name=xbufB0 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1160 -300 0 0 {name=l32 sig_type=std_logic lab=uio_in[0]}
C {lab_pin.sym} 1240 -300 0 1 {name=l33 sig_type=std_logic lab=gB0}
C {sky130_stdcells/buf_2.sym} 900 -220 0 0 {name=xbufA1 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 -220 0 0 {name=l34 sig_type=std_logic lab=ui_in[1]}
C {lab_pin.sym} 940 -220 0 1 {name=l35 sig_type=std_logic lab=gA1}
C {sky130_stdcells/buf_2.sym} 1200 -220 0 0 {name=xbufB1 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1160 -220 0 0 {name=l36 sig_type=std_logic lab=uio_in[1]}
C {lab_pin.sym} 1240 -220 0 1 {name=l37 sig_type=std_logic lab=gB1}
C {sky130_stdcells/buf_2.sym} 900 -140 0 0 {name=xbufA2 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 -140 0 0 {name=l38 sig_type=std_logic lab=ui_in[2]}
C {lab_pin.sym} 940 -140 0 1 {name=l39 sig_type=std_logic lab=gA2}
C {sky130_stdcells/buf_2.sym} 1200 -140 0 0 {name=xbufB2 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1160 -140 0 0 {name=l40 sig_type=std_logic lab=uio_in[2]}
C {lab_pin.sym} 1240 -140 0 1 {name=l41 sig_type=std_logic lab=gB2}
C {sky130_stdcells/buf_2.sym} 900 -60 0 0 {name=xbufA3 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 -60 0 0 {name=l42 sig_type=std_logic lab=ui_in[3]}
C {lab_pin.sym} 940 -60 0 1 {name=l43 sig_type=std_logic lab=gA3}
C {sky130_stdcells/buf_2.sym} 1200 -60 0 0 {name=xbufB3 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1160 -60 0 0 {name=l44 sig_type=std_logic lab=uio_in[3]}
C {lab_pin.sym} 1240 -60 0 1 {name=l45 sig_type=std_logic lab=gB3}
C {sky130_stdcells/buf_2.sym} 900 20 0 0 {name=xbufA4 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 20 0 0 {name=l46 sig_type=std_logic lab=ui_in[4]}
C {lab_pin.sym} 940 20 0 1 {name=l47 sig_type=std_logic lab=gA4}
C {sky130_stdcells/buf_2.sym} 1200 20 0 0 {name=xbufB4 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1160 20 0 0 {name=l48 sig_type=std_logic lab=uio_in[4]}
C {lab_pin.sym} 1240 20 0 1 {name=l49 sig_type=std_logic lab=gB4}
C {sky130_stdcells/conb_1.sym} 800 250 0 0 {name=xtie0 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 270 0 1 {name=l50 sig_type=std_logic lab=uo_out[0]}
C {lab_pin.sym} 860 230 0 1 {name=l51 sig_type=std_logic lab=nc_hi0}
C {sky130_stdcells/conb_1.sym} 1060 250 0 0 {name=xtie1 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1120 270 0 1 {name=l52 sig_type=std_logic lab=uo_out[1]}
C {lab_pin.sym} 1120 230 0 1 {name=l53 sig_type=std_logic lab=nc_hi1}
C {sky130_stdcells/conb_1.sym} 1320 250 0 0 {name=xtie2 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1380 270 0 1 {name=l54 sig_type=std_logic lab=uo_out[2]}
C {lab_pin.sym} 1380 230 0 1 {name=l55 sig_type=std_logic lab=nc_hi2}
C {sky130_stdcells/conb_1.sym} 1580 250 0 0 {name=xtie3 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1640 270 0 1 {name=l56 sig_type=std_logic lab=uo_out[3]}
C {lab_pin.sym} 1640 230 0 1 {name=l57 sig_type=std_logic lab=nc_hi3}
C {sky130_stdcells/conb_1.sym} 1840 250 0 0 {name=xtie4 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1900 270 0 1 {name=l58 sig_type=std_logic lab=uo_out[4]}
C {lab_pin.sym} 1900 230 0 1 {name=l59 sig_type=std_logic lab=nc_hi4}
C {sky130_stdcells/conb_1.sym} 2100 250 0 0 {name=xtie5 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 2160 270 0 1 {name=l60 sig_type=std_logic lab=uo_out[5]}
C {lab_pin.sym} 2160 230 0 1 {name=l61 sig_type=std_logic lab=nc_hi5}
C {sky130_stdcells/conb_1.sym} 800 370 0 0 {name=xtie6 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 390 0 1 {name=l62 sig_type=std_logic lab=uo_out[6]}
C {lab_pin.sym} 860 350 0 1 {name=l63 sig_type=std_logic lab=nc_hi6}
C {sky130_stdcells/conb_1.sym} 1060 370 0 0 {name=xtie7 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1120 390 0 1 {name=l64 sig_type=std_logic lab=uo_out[7]}
C {lab_pin.sym} 1120 350 0 1 {name=l65 sig_type=std_logic lab=nc_hi7}
C {sky130_stdcells/conb_1.sym} 1320 370 0 0 {name=xtie8 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1380 390 0 1 {name=l66 sig_type=std_logic lab=uio_out[0]}
C {lab_pin.sym} 1380 350 0 1 {name=l67 sig_type=std_logic lab=nc_hi8}
C {sky130_stdcells/conb_1.sym} 1580 370 0 0 {name=xtie9 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1640 390 0 1 {name=l68 sig_type=std_logic lab=uio_out[1]}
C {lab_pin.sym} 1640 350 0 1 {name=l69 sig_type=std_logic lab=nc_hi9}
C {sky130_stdcells/conb_1.sym} 1840 370 0 0 {name=xtie10 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1900 390 0 1 {name=l70 sig_type=std_logic lab=uio_out[2]}
C {lab_pin.sym} 1900 350 0 1 {name=l71 sig_type=std_logic lab=nc_hi10}
C {sky130_stdcells/conb_1.sym} 2100 370 0 0 {name=xtie11 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 2160 390 0 1 {name=l72 sig_type=std_logic lab=uio_out[3]}
C {lab_pin.sym} 2160 350 0 1 {name=l73 sig_type=std_logic lab=nc_hi11}
C {sky130_stdcells/conb_1.sym} 800 490 0 0 {name=xtie12 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 510 0 1 {name=l74 sig_type=std_logic lab=uio_out[4]}
C {lab_pin.sym} 860 470 0 1 {name=l75 sig_type=std_logic lab=nc_hi12}
C {sky130_stdcells/conb_1.sym} 1060 490 0 0 {name=xtie13 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1120 510 0 1 {name=l76 sig_type=std_logic lab=uio_out[5]}
C {lab_pin.sym} 1120 470 0 1 {name=l77 sig_type=std_logic lab=nc_hi13}
C {sky130_stdcells/conb_1.sym} 1320 490 0 0 {name=xtie14 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1380 510 0 1 {name=l78 sig_type=std_logic lab=uio_out[6]}
C {lab_pin.sym} 1380 470 0 1 {name=l79 sig_type=std_logic lab=nc_hi14}
C {sky130_stdcells/conb_1.sym} 1580 490 0 0 {name=xtie15 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1640 510 0 1 {name=l80 sig_type=std_logic lab=uio_out[7]}
C {lab_pin.sym} 1640 470 0 1 {name=l81 sig_type=std_logic lab=nc_hi15}
C {sky130_stdcells/conb_1.sym} 1840 490 0 0 {name=xtie16 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1900 510 0 1 {name=l82 sig_type=std_logic lab=uio_oe[0]}
C {lab_pin.sym} 1900 470 0 1 {name=l83 sig_type=std_logic lab=nc_hi16}
C {sky130_stdcells/conb_1.sym} 2100 490 0 0 {name=xtie17 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 2160 510 0 1 {name=l84 sig_type=std_logic lab=uio_oe[1]}
C {lab_pin.sym} 2160 470 0 1 {name=l85 sig_type=std_logic lab=nc_hi17}
C {sky130_stdcells/conb_1.sym} 800 610 0 0 {name=xtie18 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 860 630 0 1 {name=l86 sig_type=std_logic lab=uio_oe[2]}
C {lab_pin.sym} 860 590 0 1 {name=l87 sig_type=std_logic lab=nc_hi18}
C {sky130_stdcells/conb_1.sym} 1060 610 0 0 {name=xtie19 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1120 630 0 1 {name=l88 sig_type=std_logic lab=uio_oe[3]}
C {lab_pin.sym} 1120 590 0 1 {name=l89 sig_type=std_logic lab=nc_hi19}
C {sky130_stdcells/conb_1.sym} 1320 610 0 0 {name=xtie20 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1380 630 0 1 {name=l90 sig_type=std_logic lab=uio_oe[4]}
C {lab_pin.sym} 1380 590 0 1 {name=l91 sig_type=std_logic lab=nc_hi20}
C {sky130_stdcells/conb_1.sym} 1580 610 0 0 {name=xtie21 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1640 630 0 1 {name=l92 sig_type=std_logic lab=uio_oe[5]}
C {lab_pin.sym} 1640 590 0 1 {name=l93 sig_type=std_logic lab=nc_hi21}
C {sky130_stdcells/conb_1.sym} 1840 610 0 0 {name=xtie22 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 1900 630 0 1 {name=l94 sig_type=std_logic lab=uio_oe[6]}
C {lab_pin.sym} 1900 590 0 1 {name=l95 sig_type=std_logic lab=nc_hi22}
C {sky130_stdcells/conb_1.sym} 2100 610 0 0 {name=xtie23 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__}
C {lab_pin.sym} 2160 630 0 1 {name=l96 sig_type=std_logic lab=uio_oe[7]}
C {lab_pin.sym} 2160 590 0 1 {name=l97 sig_type=std_logic lab=nc_hi23}
