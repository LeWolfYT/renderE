import rendereglobals as rg
from PIL import Image, ImageFilter
from io import BytesIO
import os
import glob
import nethandler
import libmv
import builtins
import freetype
rl = rg.rl
pg = rg.pg

def parsePath(path : str):
    if path.startswith("/rsrc"):
        return path.replace("/rsrc", os.environ["RENDERERSRC"], 1)
    if path.startswith("/media"):
        return path.replace("/media", os.environ["RENDEREMEDIA"], 1)
    return path

def createImage(self, name, evict=0, x1=0, y1=0, x2=1, y2=1):
    ogname = name+""
    pname = parsePath(name)
    possible = glob.glob(pname+".*")
    print(possible)
    if os.path.exists(ogname):
        name = ogname
    else:
        if len(possible) > 0:
            name = possible[0]
        else:
            name = nethandler.requestNetAsset(name, "gfx")
        if not name:
            renderElog(f"No suitable image found for {ogname}!")
            exit(1)
    
    yy1 = 1-y2
    yy2 = 1-y1
    arr = BytesIO()
    
    try:
        im = Image.open(name).convert("RGBA")
        if (x1 != 0) or (y1 != 0) or (x2 != 1) or (y2 != 1):
            im = im.crop((x1*im.width, y1*im.height, x2*im.width, yy2*im.height))
        im.save(arr, format="PNG")
    except:
        if name.endswith((".tif", ".tiff")): #keeping this just in case
            im = pg.image.load(name)
            new_size = (im.width * (x2 - x1), im.height * (yy2 - yy1))
            im2 = pg.Surface(new_size, pg.SRCALPHA)
            im2.blit(im, (-x1*im.width, -yy1*im.height))#, special_flags=pg.BLEND_PREMULTIPLIED)
            pg.image.save(im2, arr, "PNG")
    arr = arr.getvalue()
    self.im2 = rl.load_image_from_memory('.png', arr, len(arr))
    rl.image_alpha_premultiply(self.im2)
    self.texture = None
    self._size = (self.im2.width, self.im2.height)
    self.optimal_size = (self.im2.width, self.im2.height)

def createIcon(self, name, evict=0):
    ogname = name+""
    pname = parsePath(name)
    possible = glob.glob(pname+".mv")
    print(possible)
    if len(possible) > 0:
        name = possible[0]
    else:
        name = nethandler.requestNetAssetExt(name, "mv")
    if not name:
        print(f"No suitable icon found for {ogname}!")
        exit(1)
    
    with open(name, "rb") as f:
        data = f.read()
    
    print("loading mv ", name)
    #self._frames = libmv.loadmv(data)
    self._ims = libmv.loadmv(data)
    
    
    #self._rframes = [rl.ffi.new('char []', fr.tobytes()) for fr in self._frames]
    self.idx = 0
    self.framect = len(self._ims)
    
    self.textures = None
    self._size = (self._ims[0].width, self._ims[0].height)

def createTTFont(self, name, pointSize, shadow, sr=0.08, sg=0.08, sb=0.08, sa=1.0, sx=1, sy=2, t=0, l=None, evict=0):
    self.pointsize = pointSize
    ogname = name+""
    pname = parsePath(name)
    possible = glob.glob(pname+".*")
    if len(possible) > 0:
        name = possible[0]
    else:
        name = nethandler.requestNetAsset(name, "font")
    if not name:
        print(f"No suitable font found for {ogname}!")
        exit(1)
    
    self.font = freetype.Face(name)
    self.name = name
    self.font.set_char_size(64*pointSize)
    
    matrix = freetype.Matrix(int(1 * 65536), 0, 0, int(8/9 * 65536))
    freetype.FT_Set_Transform(self.font._FT_Face, matrix, freetype.Vector(0, 0))
    
    print(dir(self.font.size))
    self.ascent = self.font.size.ascender / 64.0
    self.descent = self.font.size.descender / 64.0
    self.l = l or (self.font.size.height / 64.0)
    #builtins.__dict__["rg_font_cache"][(ogname, self.pxSize)] = (self.font, self.reallineheight, self.ascent, self.descent, self.ref)
    self.scol = (sr, sg, sb, sa)

def createAudio(self):
    return

def createAudioClip(self, name, evict=0, duration_limit=0, loop_limit=1):
    ogname = name+""
    pname = parsePath(name)
    if os.path.exists(pname):
        name = ogname
    else:
        name = nethandler.requestNetAssetExt(name)
    if not name:
        print(f"No suitable sound found for {ogname}!")
        exit(1)
    self.name = name
    self.file = rg.pg.Sound(name)
    
    self.chan = None
    self.evict = evict
    self.duration_limit = duration_limit
    self.time_played = 0
    self.loop_limit = loop_limit
    self.level = 1
    self.mix = 1
    self.single_play = 0
    self.btype = 1

import av
#import numpy as np
def createQTMovie(self, name, evict=0):
    ogname = name+""
    pname = parsePath(name)
    if os.path.exists(ogname+".mov"):
        name = ogname+".mov"
    elif os.path.exists(pname+".mov"):
        name = pname+".mov"
    else:
        name = nethandler.requestNetAssetExt(name, "mov")
    self.images = []
    if not name:
        self.name = None
        self.cap = None
        self.textures = []
        raise Exception(ogname)
    cap = av.open(name)
    self.name = name
    self.cap = cap
    vs = cap.streams.video[0]

    i = 0
    for frame in cap.decode(video=0):
        if type(frame) == av.VideoFrame:
            frameimg = frame.to_ndarray(format="rgba")
            im = Image.fromarray(frameimg)
            arr = BytesIO()
            im.save(arr, format="PNG")
            arr = arr.getvalue()
            img = rl.load_image_from_memory('.png', arr, len(arr))
            rl.image_alpha_premultiply(img)
            self.images.append(img)
            self._size = im.size
    self.textures = [None] * len(self.images)