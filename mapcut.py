import nethandler as nh
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None #these images are too HUGE
import twc.dsmarshal as dsm
import os
import json
#import pygame as pg
import rendereglobals as rg
import traceback as tb

def vginfo(vgfile):
    extents = [1, 1]
    def setExtents(w, h):
        nonlocal extents
        extents = [w, h]
    polylines = []
    def addPolyline(pl, name):
        polylines.append(pl)
    with open(vgfile, "r") as f:
        exec(f.read(), {"setExtents": setExtents, "addPolyline": addPolyline})
    return extents, polylines

def draw_polylines(polylines, sz):
    im = Image.new("1", sz, "black")
    idraw = ImageDraw.Draw(im)
    for l in polylines:
        print(l)
        idraw.polygon(l, None, "white", 1)
    return im, idraw

def process(mtype, debug=False, vonly=False):
    print("MAPCUT")
    print(f"PROCESS {mtype}")
    md = dsm.get(mtype+".MapData")
    mapname = md.mapName
    print(mapname)
    if not vonly:
        mappath = nh.requestNetAssetExt(f"/usr/local/twc/rsrc/maps/{mapname}")
        if mapname.endswith(".bfg"):
            dt = rg.newjoin(os.environ["RENDEREROOT"], "temp", f"{mapname}.jpeg")
            if os.path.exists(dt):
                finalmapimg = Image.open(dt)
            else:
                print(f"Assembling {mapname} for the first time! This will be cached until you delete your temporary files again.")
                with open(mappath, "r") as f:
                    mapdef = f.read().strip().split("\n")
                total = int(mapdef[0])
                cols = int(mapdef[1])
                rows = total//cols
                maps = mapdef[2:]
                mp = []
                for map in maps:
                    mp.append(Image.open(nh.requestNetAssetExt(map)))
                finalmapimg = Image.new("RGB",
                    (sum([m.width for m in mp[:cols]]),
                    sum([m.height for m in mp[::rows]]))
                )
                
                xx = 0
                yy = 0
                for row in range(rows):
                    for col in range(cols):
                        cmap = mp[col+row*cols]
                        finalmapimg.paste(cmap, (xx, yy))
                        xx += cmap.width
                    xx = 0
                    yy += mp[row*cols].height
                del maps #memory management!
                finalmapimg.save(rg.newjoin(os.environ["RENDEREROOT"], "temp", f"{mapname}.jpeg"))
        else:
            finalmapimg = Image.open(mappath).convert("RGB")
    
    #cut
    cx, cy = md.mapcutCoordinate
    cw, ch = md.mapcutSize
    if not vonly:
        cy = finalmapimg.height-cy
        crop = (cx, cy-ch, cx+cw, cy)
        intermediate = finalmapimg.crop(crop)
        print(crop, cw, ch)
        final = intermediate.resize(md.mapFinalSize, Image.Resampling.LANCZOS)
        os.makedirs(rg.newjoin(os.environ["TWCPERSDIR"], "data", "map.cuts"), exist_ok=True)
        final.save(rg.newjoin(os.environ["TWCPERSDIR"], "data", "map.cuts", f"{mtype}.map.tif"))
    
    dcx, dcy1 = cx, cy #getattr(md, "datacutCoordinate", (cx, cy))
    dcw, dch = cw, ch #getattr(md, "datacutSize", (cw, ch))
    
    fdcw, fdch = md.mapFinalSize #getattr(md, "dataFinalSize", md.mapFinalSize)
    
    finalmapimg = None
    intermediate = None
    final = None
    
    for v in md.vectors:
        vx = v.split(".")[-2]
        ex, pl = vginfo(nh.requestNetAssetExt(f"/usr/local/twc/rsrc/maps/{v}"))
        if debug:
            ib, idraw = draw_polylines(pl, ex)
        if hasattr(md, "datacutCoordinate"):
            dcy = dcy1
        else:
            dcy = ex[1] - dcy1
        
        left = dcx
        right = dcx+dcw
        top = dcy
        bottom = dcy+dch
        print("vstats", v, left, right, top, bottom, "full", ex)
        
        finalpl = []
        for pol in pl:
            poly_is_inside = False
            for pt in pol:
                ptx, pty = pt
                if (left <= ptx <= right) and (top <= pty <= bottom):
                    poly_is_inside = True
                    print("IT'S IN")
                    break
            
            if poly_is_inside:
                finalpl.append([((p[0]-dcx)*fdcw/dcw, (ex[1]-p[1]-(ex[1]-bottom))*fdch/dch) for p in pol])
        
        if debug:
            idraw.rectangle((left, top, right, bottom), fill=1, width=9)
            ib.save(v+".png")
        vectorCut = rg.newjoin(os.environ["TWCPERSDIR"], "data", "map.cuts", f'{mtype}.{vx}.vg')
        with open(vectorCut, "w") as f:
            f.write(json.dumps([fdcw, fdch, finalpl], indent=4))

if __name__ == "__main__":
    try:
        process('Config.1.Local_RegionalDopplerRadar')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_MetroDopplerRadar')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_RegionalForecastMap')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_MetroForecastMap')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_RegionalObservationMap')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_MetroObservationMap')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_Satellite')
    except:
        tb.print_exc()
    try:
        process('Config.1.Local_RadarSatelliteComposite')
    except:
        tb.print_exc()
    try:
        process('Config.1.Radar_LocalDoppler')
    except:
        tb.print_exc()