import pya
a=pya.Layout(); a.read('tt_um_tjfreeborn1_cpe_a07a05.gds'); b=pya.Layout(); b.read('tt_um_tjfreeborn1_cpe_a07a05.oas')
ta=a.top_cell(); tb=b.top_cell(); print('top', ta.name, tb.name, 'dbu', a.dbu, b.dbu)
tot=0; nl=0
la={(i.layer,i.datatype):k for k,i in zip(a.layer_indexes(),a.layer_infos())}
lb={(i.layer,i.datatype):k for k,i in zip(b.layer_indexes(),b.layer_infos())}
print('layers', len(la), len(lb), 'same set', set(la)==set(lb))
for key in sorted(set(la)|set(lb)):
    ra=pya.Region(ta.begin_shapes_rec(la[key])) if key in la else pya.Region()
    rb=pya.Region(tb.begin_shapes_rec(lb[key])) if key in lb else pya.Region()
    x=ra^rb; n=x.count(); tot+=n; nl+=1
    if n: print('XOR diff on layer',key,n)
print('layers compared',nl,'total XOR polygons',tot)
