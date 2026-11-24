import json, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
g=json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'build/geo.json')); t=json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'build/geo_top.json'))
X7,Y7,X5,Y5,Xr,Yr=[t[k] for k in ('X7','Y7','X5','Y5','Xr','Yr')]
INK,INK2,SURF,GRID="#0b0b0b","#52514e","#fcfcfb","#c3c2b7"
BL,OR,AQ,YE,GR="#2a78d6","#eb6834","#1baf7a","#eda100","#898781"
fig,ax=plt.subplots(figsize=(13,9.4),facecolor=SURF); ax.set_facecolor(SURF)
ax.add_patch(Rectangle((0,0),334.88,225.76,fill=False,ec=INK,lw=1.4))
def box(x1,y1,x2,y2,c,label='',sub='',a=0.16,fs=8.5,ls='-'):
    x1,x2=min(x1,x2),max(x1,x2)
    ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fc=c,alpha=a,ec='none'))
    ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fill=False,ec=c,lw=1.1,ls=ls))
    if label: ax.text((x1+x2)/2,(y1+y2)/2+(3 if sub else 0),label,ha='center',va='center',fontsize=fs,color=INK)
    if sub: ax.text((x1+x2)/2,(y1+y2)/2-3.5,sub,ha='center',va='center',fontsize=fs-1,color=INK2)
for key,X,Y,s,name in (('i07',X7,Y7,1,'α = 0.7'),('i05',X5,Y5,-1,'α = 0.5')):
    i=g[key]; W=i['W']
    xa,xb=X+s*0,X+s*W
    bk=i['bank']; box(xa,Y+bk['tsheet'][1],xb,Y+bk['band_top'],OR,f'Trim bank ({name})','5 bits, 0.3–4.8 pF MIM, top plate = pin',a=0.20)
    for b in i['branches']:
        m=b['mim']; box(xa,Y+m['y1']-0.6,xb,Y+m['y2']+0.6,BL,f"{name}  {b['name']}",f"{b['units']} MOS units + {m['n']} MIM tiles",a=0.13)
    rg=i['ring']; ax.add_patch(Rectangle((min(X+s*rg[0],X+s*rg[2]),Y+rg[1]),abs(rg[2]-rg[0]),rg[3]-rg[1],fill=False,ec=BL,lw=1.6))
ir=g['ir']['ring']; box(Xr+ir[0],Yr+ir[1],Xr+ir[2],Yr+ir[3],AQ,'Resistors','53 xhigh-poly\nstripes',a=0.2)
for x1,x2 in ((136.9,145.0),(193.2,202.4)): box(x1,35,x2,76,YE,'',a=0.3)
ax.annotate('bank B switches',(141,76),(150,126),ha='center',fontsize=7.5,color=INK2,arrowprops=dict(arrowstyle='-',color=INK2,lw=0.6)); ax.annotate('bank A switches',(197.8,76),(188,126),ha='center',fontsize=7.5,color=INK2,arrowprops=dict(arrowstyle='-',color=INK2,lw=0.6))
box(29.6,219.0,141.2,221.7,YE,'',a=0.35); ax.text(85,214.6,'24 tie cells · 10 buffers + antenna diodes',ha='center',fontsize=8,color=INK2)
for x,n in ((1,'VDPWR'),(4,'VGND')): ax.add_patch(Rectangle((x,5),2,217.5,fc=GR,ec=GR))
ax.text(-3,113,'VDPWR / VGND stripes (metal 4)',rotation=90,va='center',ha='center',fontsize=7.5,color=INK2)
for x,n,dx,ha in ((152.26,'ua[0]  (α = 0.7)',6,'left'),(132.94,'ua[1]  (α = 0.5)',-6,'right')):
    ax.add_patch(Rectangle((x-0.45,0),0.9,2.5,fc=INK)); ax.annotate(n,(x,0),(x+dx,-11),ha=ha,fontsize=8.5,color=INK,arrowprops=dict(arrowstyle='-',color=INK2,lw=0.6))
ax.text(169,165,'node routes →\n← gate lines from buffers',ha='center',fontsize=7.5,color=INK2)
ax.set_xlim(-8,341); ax.set_ylim(-17,232); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Layout v1 of tt_um_tjfreeborn1_cpe_a07a05 in the 2×2 tile (334.9 × 225.8 µm), to scale',loc='left',fontsize=11.5,color=INK)
fig.tight_layout(); fig.savefig(sys.argv[3] if len(sys.argv) > 3 else 'floorplan.png',dpi=150,facecolor=SURF)
