"""render.py in.gds out.png [cell] [x0 y0 x1 y1 um] -- render with the sky130 layer properties"""
import sys, os, klayout.lay as lay, klayout.db as db
gds, png = sys.argv[1], sys.argv[2]
lv = lay.LayoutView(); lv.load_layout(gds, True)
lyp=os.path.join(os.environ.get('PDK_ROOT','/usr/local/share/pdk'),'sky130A/libs.tech/klayout/tech/sky130A.lyp')
lv.load_layer_props(lyp)
if len(sys.argv)>3 and sys.argv[3]!='-': 
    ly=lv.cellview(0).layout(); lv.select_cell(ly.cell(sys.argv[3]).cell_index(),0)
lv.max_hier(); lv.set_config("background-color","#ffffff"); lv.set_config("grid-visible","false")
if len(sys.argv)>7: lv.zoom_box(db.DBox(*map(float,sys.argv[4:8])))
else: lv.zoom_fit()
lv.save_image(png, 1600, 1100)
