# uncompyle6 version 3.9.3
# Python bytecode version base 2.2 (60717)
# Decompiled from: Python 3.13.2 (main, Feb  4 2025, 14:51:09) [Clang 16.0.0 (clang-1600.0.26.6)]
# Embedded file name: RenderScript.py
# Compiled at: 2007-01-12 11:17:28

import rendereglobals as rg
from . import _renderd
import os

rg.__dict__["box_thing"] = None

load_stuff = {}

def fix_font_text(surf, ascent, descent, ref=None):
    #pygame sometimes renders text with blank space on the bottom idk why, but it messes with baseline-based text drawing
    #this is notable for making the flat rock LF ldl look really bad
    if ref is None:
        ref = surf
    diff = (ascent-descent) - ref.height
    #renderElog("diff", diff)
    if diff == 0:
        return surf
    elif diff < 0:
        return surf.subsurface(rg.pg.Rect(0, 0, surf.width, surf.height+diff)).copy()
    else:
        newsurf = rg.pg.Surface((surf.width, surf.height+diff))
        newsurf.blit(surf, (0, 0))

class ObjectWrapper:

    def __init__(self):
        raise RuntimeError('Instantiated abstract class: ' + self.__name__)

    def __del__(self):
        pass

    def add_loaded(self):
        cname = type(self).__name__
        if cname not in load_stuff:
            load_stuff[cname] = 1
        else:
            load_stuff[cname] += 1
    
    def remove_loaded(self):
        cname = self.__class__.__name__
        if cname not in load_stuff:
            load_stuff[cname] = 0
        else:
            load_stuff[cname] -= 1

class Layer(ObjectWrapper):

    def __init__(self):
        self.pages = []
        self.timer = -1
        self.totals = []
        self.pa = 0
        return

    def addPage(self, page):
        self.pages.append((page, page.duration()))
        if len(self.totals) == 0:
            self.totals.append(page.duration())
        else:
            self.totals.append(page.duration()+self.totals[-1])
    
    def __del__(self):
        self.pages = []


class Page(ObjectWrapper):

    def __init__(self, duration=0):
        """duration == 0 means page plays forever"""
        self.timer = 0
        self._duration = duration
        self.started = False
        self.ended = False
        self._elements = []
        self._onStartCommands = []
        self._onFrameCommands = []
        self._onEndCommands = []

    def addItem(self, item):
        item.added = True
        if type(item) is EffectSequencer:
            item.timer = (not getattr(item.target, "added", True))-1
        if isinstance(item, PageCommand):
            frame = item.activeFrame()
            if frame == 0:
                return self.addOnStartCommand(item)
            elif frame == self._duration - 1:
                return self.addOnEndCommand(item)
            else:
                return self.addOnFrameCommand(item, frame)
        else:
            #res = _renderd.Page_addItem(self, item)
            res = 1
            if type(item) in (Text, Clock):
                rg.text_queue.append(item)
            self._elements.append(item)
            return res

    def addOnStartCommand(self, cmd):
        self._onStartCommands.append(cmd)
        return

    def addOnFrameCommand(self, cmd, activeFrame, forceAtEnd=0):
        #res = _renderd.Page_addOnFrameCommand(self, activeFrame, cmd, forceAtEnd)
        self._onFrameCommands.append([cmd, activeFrame, forceAtEnd])
        return 

    def addOnEndCommand(self, cmd):
        #res = _renderd.Page_addOnEndCommand(self, cmd)
        self._onEndCommands.append(cmd)
        return 

    def elements(self):
        return self._elements

    def onStartCommands(self):
        return self._onStartCommands

    def onFrameCommands(self):
        return self._onFrameCommands

    def onEndCommands(self):
        return self._onEndCommands

    def duration(self):
        return self._duration

    def unload(self):
        self.__del__(True)

    def __del__(self, manual=False):
        for i in self._elements:
            rg.unloadqueue.append(i)

class Font(ObjectWrapper):

    def __init__(self, pointsize):
        self.pointsize = pointsize

    def pointSize(self):
        return self.pointsize

    def tracking(self):
        return 0

    def leading(self):
        return 0

    def stringSize(self, str):
        bn = self.font.size(str)
        return bn

    def stringWidth(self, str):
        (w, h) = self.stringSize(str)
        return w

    def stringHeight(self, str):
        (w, h) = self.stringSize(str)
        return h

from PIL import Image as Img
import freetype
import numpy as np

class Character:
    def __init__(self, font, color, char):
        tfont : freetype.Face = font.font
        tfont.load_char(char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_LIGHT)
        self.char = char
    
        slot = tfont.glyph
        bitmap = slot.bitmap
        width = bitmap.width
        rows = bitmap.rows
        
        self.bearing = slot.bitmap_top
        self.hbearing = slot.bitmap_left
        self.advance = slot.metrics.horiAdvance / 64.0
        
        self.empty = (width == 0 or rows == 0)
        if self.empty:
            return
        
        shadow = font.shadow
        alpha = Img.frombytes("L", (width, rows), bytes(bitmap.buffer))
        
        if shadow:
            mainimage = Img.new("RGB", alpha.size, color)
            shadowimage = Img.new("RGB", alpha.size, tuple([round(i*255) for i in font.scol]))
            mainimage.putalpha(alpha)
            shadowimage.putalpha(alpha)
            pilimage = Img.new("RGBA", (alpha.size[0]+font.sx, alpha.size[1]+font.sy))
            pilimage.paste(shadowimage, (font.sx, font.sy), shadowimage)
            pilimage.alpha_composite(mainimage, (0, 0))
        else:
            pilimage = Img.new("RGB", alpha.size, color)
            pilimage.putalpha(alpha)
        
        buf = BytesIO()
        pilimage.save(buf, "BMP")
        bv = buf.getvalue()
        self.image = rg.rl.load_image_from_memory(".bmp", bv, len(bv))
        rg.rl.image_alpha_premultiply(self.image)
        self.texture = None
        
    def load(self):
        if self.empty:
            return
        if self.texture is None:
            self.texture = rg.rl.load_texture_from_image(self.image)
    
    def unload(self):
        if self.empty:
            return
        if self.texture is not None:
            rg.rl.unload_texture(self.texture)
            self.texture = None
        if self.image is not None:
            rg.rl.unload_texture(self.image)
            self.image = None

class TTFont(Font):

    def __init__(self, name, pointSize, shadow=1, sr=0.08, sg=0.08, sb=0.08, sa=1.0, sx=1, sy=2, t=0, l=None, evict=0):
        self.shadow = shadow
        self.scol = (sr, sg, sb, sa)
        self.sx = sx*1
        self.sy = sy*1
        self.chars = {}
        self.t = t
        self.name = None
        Font.__init__(self, pointSize)
        if l == None:
            l = pointSize
        _renderd.createTTFont(self, name, pointSize, shadow, sr, sg, sb, sa, sx, sy, t / 2, l, evict)

    def get_char(self, char, color):
        if self.shadow:
            ckey = (char, self.name, color, self.pointSize(), self.sx, self.sy, self.scol)
        else:
            ckey = (char, self.name, color, self.pointSize())
        if ckey not in builtins.__dict__["rg_font_cache"]:
            character = Character(self, color, char)
            builtins.__dict__["rg_font_cache"][ckey] = character
        else:
            character = builtins.__dict__["rg_font_cache"][ckey]
        
        return character

    def stringSize(self, str):
        return get_text_size(str, (235, 235, 235), self)

    def tracking(self):
        return self.t

    def leading(self):
        return self.l

class TTOutlineFont(Font):

    def __init__(self, name, pointSize, thickness=1, t=0, l=None, evict=0):
        if l == None:
            l = pointSize
        Font.__init__(self, pointSize)
        _renderd.createTTOutlineFont(self, name, pointSize, thickness, t / 2, l, evict)


class Renderable(ObjectWrapper):

    def setAnimationState(self, animate):
        return #_renderd.Renderable_setAnimationState(self, animate)

    def animationState(self):
        return #_renderd.Renderable_getAnimationState(self)

    def setVisibility(self, visible):
        self.visible = visible
        return

    def visibility(self):
        return self.visible


class PageCommand(Renderable):

    def __init__(self, activeFrame=0):
        self.timer = -1
        self._activeFrame = activeFrame

    def activeFrame(self):
        return self._activeFrame


class CreateNamedLayer(PageCommand):

    def __init__(self, activeFrame, lname, depth, repeat=0, autoDestroy=1):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname
        self.depth = depth
        self.repeat = repeat
        self.autoDestroy = autoDestroy


class DestroyNamedLayer(PageCommand):

    def __init__(self, activeFrame, lname):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname


class SetLayer(PageCommand):

    def __init__(self, activeFrame, lname, layer):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname
        self.layer = layer

    def unload(self):
        self.layer = None

class AppendLayer(PageCommand):

    def __init__(self, activeFrame, lname, layer):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname
        self.layer = layer
    
    def unload(self):
        self.layer = None


class RemoveLayer(PageCommand):

    def __init__(self, activeFrame, lname):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname

    def unload(self):
        self.layer = None

class ActivateLayer(PageCommand):

    def __init__(self, activeFrame, lname):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname
    

class DeactivateLayer(PageCommand):

    def __init__(self, activeFrame, lname):
        PageCommand.__init__(self, activeFrame)
        self.lname = lname

    def unload(self):
        self.layer = None

class SelectInputSource(PageCommand):

    def __init__(self, activeFrame, src):
        PageCommand.__init__(self, activeFrame)


class LoadPresentation(PageCommand):

    def __init__(self, activeFrame, fileName):
        PageCommand.__init__(self, activeFrame)
        self.fileName = fileName


class ActivateGpiPin(PageCommand):

    def __init__(self, activeFrame, pin):
        PageCommand.__init__(self, activeFrame)


class DeactivateGpiPin(PageCommand):

    def __init__(self, activeFrame, pin):
        PageCommand.__init__(self, activeFrame)

class SetWatermarkSID(PageCommand):
    
    def __init__(self, activeFrame, sid, sidSum):
        PageCommand.__init__(self, activeFrame)
        #_renderd.createSetWatermarkSID(self, sid, sidSum)
        return

class RenderCommand(ObjectWrapper):
    pass


class CreateNamedLayerCmd(RenderCommand):

    def __init__(self, lname, depth, repeat=0, autoDestroy=1):
        self.lname = lname
        self.depth = depth
        self.repeat = repeat
        self.autoDestroy = autoDestroy


class DestroyNamedLayerCmd(RenderCommand):

    def __init__(self, lname):
        self.lname = lname


class SetNamedLayerViewPortCmd(RenderCommand):

    def __init__(self, lname, x, y, w, h, sx=1, sy=1, tx=0, ty=0):
        self.lname = lname
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.sx = sx
        self.sy = sy
        self.tx = tx
        self.ty = ty


class SetLayerCmd(RenderCommand):

    def __init__(self, lname, layer):
        self.lname = lname
        self.layer = layer

    def unload(self):
        self.layer = None

class AppendLayerCmd(RenderCommand):

    def __init__(self, lname, layer):
        self.lname = lname
        self.layer = layer

    def unload(self):
        self.layer = None

class RemoveLayerCmd(RenderCommand):

    def __init__(self, lname):
        self.lname = lname


class ActivateLayerCmd(RenderCommand):

    def __init__(self, lname):
        self.lname = lname


class DeactivateLayerCmd(RenderCommand):

    def __init__(self, lname):
        self.lname = lname
        


class SelectInputSourceCmd(RenderCommand):

    def __init__(self, src, activeFrame=0):
        _renderd.createSelectInputSource(self, src, activeFrame)
        


class LoadPresentationCmd(RenderCommand):

    def __init__(self, fileName):
        self.fileName = fileName
        


class ActivateGpiPinCmd(RenderCommand):

    def __init__(self, pin):
        _renderd.createActivateGpiPin(self, pin)
        


class DeactivateGpiPinCmd(RenderCommand):

    def __init__(self, pin):
        _renderd.createDeactivateGpiPin(self, pin)
        

class SetWatermarkSIDCmd(RenderCommand):

    def __init__(self, sid, sidSum):
        #_renderd.createSetWatermarkSID(self, sid, sidSum)
        return

class ModifyNamedLayerCmd(RenderCommand):

    def __init__(self, name, newName, depth, repeat, autoDestroy):
        self.name = name
        self.newName = newName
        self.depth = depth
        self.repeat = repeat
        self.autoDestroy = autoDestroy
        


class ReplaceLayerCmd(RenderCommand):

    def __init__(self, name, layer):
        self.name = name
        self.layer = layer
        


class SignalEventCmd(RenderCommand):

    def __init__(self, type, params, channel='SystemEventChannel'):
        _renderd.createSignalEvent(self, type, params, channel)
        


class GraphicRenderable(Renderable):

    def __init__(self):
        self._position = (0, 0)
        self._size = (0, 0)
        self.effects = []
        self.visible = True
        self.setTransitionable(1)
        self.seq_start_after = False
        self._color = (1, 1, 1, 1)
        self.unloaded = False
        self.added = False
        self.dynamicfilter = None
        self.add_loaded()
    
    def size(self):
        return self._size
        
    def addGraphicEffect(self, effect):
        self.effects.append(effect)
    
    def addEffectSequencer(self, seq, repeat, loopLimit):
        self.effects.append(seq)
    

    def setTransitionable(self, val):
        self._transitionable = val
        

    def transitionable(self):
        return self._transitionable
        return

    def setPosition(self, x, y):
        self._position = (x, y)
        return

    def position(self):
        return self._position
        return

    def setSize(self, w, h):
        self._size = (w, h)
        return

    def size(self):
        return self._size

    def setColor(self, r=0, g=0, b=0, a=1):
        self._color = (r, g, b, a)
        return

    def color(self):
        return self._color
        return

    def addDynamicFilter(self, filter):
        self.dynamicfilter = filter
    
    def __del__(self):
        self.remove_loaded()
        return super().__del__()

class Box(GraphicRenderable):

    def __init__(self):
        #if not rg.__dict__["box_thing"]:
        #    rg.__dict__["box_thing"] = self
        super().__init__()
        return
        

import dateutil as dut
from datetime import datetime
class Clock(GraphicRenderable):
    LEFT = 0
    RIGHT = 1
    CENTER = 2

    def __init__(self, font, format, lcase_ampm=1, justification=LEFT, timezone='', timezoneDisplay=''):
        """Specify the font and format used to display the time.
        format is a string in the format expected by the strftime c-lib func.
        timezone is a string used to set the TZ environment variable for alternate timezones.
        timzoneDisplay is the string value that will replace '<z>' within the format string.
        """
        GraphicRenderable.__init__(self)
        self.font = font
        self.format = format
        self.lcase_ampm = lcase_ampm
        self.justification = justification
        self.timezone = timezone
        self.timezoneDisplay = timezoneDisplay
        if timezone == "":
            self.tz = None
        else:
            self.tz = dut.tz.gettz(timezone)
        self.s = self.get_format()
        self.lasts = self.s+""
        self.cachedtex = None
        self.cachedimg = None
        self.cimg = None
        self.fnt = font
        self.glist = None
        self.ksize = None
        self.rtex = None
        self.draw_off = (0, 0)
        self.text_bounds = (0, 0)
        self.processed = False
        
        
        self._lastcol = tuple(list(self._color))
        #self._textsize = self.textbase.size
        #self._size = self.textbase.size
        
        #self.basesize = self.textbase.get_size()
        #_renderd.createClock(self, font, format, lcase_ampm, justification, timezone, timezoneDisplay)

    def get_format(self):
        now = datetime.now(tz=self.tz)
        i = str(int(now.strftime("%I")))
        if nh.personality != "Watt":
            i = i.rjust(2)
        return now.strftime(self.format.replace("%l", i)).replace("<z>", self.timezoneDisplay)

    def process(self):
        if self.processed:
            return
        self.processed = True
        glist, clist, ctg, top_o = build_glyph_list(0, 0, self.s, tuple([round(c*255) for c in self._color]), self.fnt)
        vv = list(ctg.values())
        try:
            x_min = min([min(x, key=lambda val: val[0]) for x in vv], key=lambda val: val[0])[0]
        except:
            return
        y_min = min([min(y, key=lambda val: val[1]) for y in vv], key=lambda val: val[1])[1]
        x_mx = max([max(x, key=lambda val: val[0]+val[2]) for x in vv], key=lambda val: val[0]+val[2])
        y_mx = max([max(y, key=lambda val: val[1]+val[3]) for y in vv], key=lambda val: val[1]+val[3])
        x_max = x_mx[0]+x_mx[2]
        y_max = y_mx[1]+y_mx[3]
        rtw = abs(x_max-x_min)
        rth = abs(y_max-y_min)
        self.text_bounds = (rtw, rth)

    def size(self):
        self.process()
        return self.text_bounds# or get_text_size(self.s, tuple([round(c*255) for c in self._color]), self.fnt, self)

    def unload(self):
        if self.rtex:
            rg.rl.unload_render_texture(self.rtex)

class TimeCode(GraphicRenderable):

    def __init__(self, font):
        GraphicRenderable.__init__(self)
        

from io import BytesIO
import builtins

def crop_text(surf: rg.pg.Surface):
    final_left = 0
    found_left = False
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            c = surf.get_at((x, y))
            if c.a != 0:
                found_left = True
                break
        if found_left:
            break
        final_left += 1
    return surf.subsurface(rg.pg.Rect(final_left, 0, surf.get_width()-final_left, surf.get_height()))


tracking = True
def get_text_size(s, col, font : TTFont, store=None):
    width = 0
    lines = 0
    for line in s.split("\n"):
        lines += 1
        lwidth = 0
        i = 1
        for c in line:
            last_char = (i == len(line))
            char = font.get_char(c, col)
            lwidth += char.advance
            if tracking:
                lwidth += (font.tracking() * font.pointSize() / 2000)
            if font.font.has_kerning and not last_char:
                if not s[i] == "\n":
                    kern = font.font.get_kerning(ord(c), ord(s[i]), mode=0).x / 64.0
                    lwidth += kern
            i += 1
        if tracking:
            lwidth -= (font.tracking() * font.pointSize() / 2000)
        if lwidth > width:
            width = lwidth+0
    
    out = (round(width), font.leading()*lines)
    if store:
        store.ksize = out
    return out

def build_glyph_list(x, y, s, col, font : TTFont, top=False, more=False):
    """
    Outputs a list of coordinates and textures for drawing text.
    This should make the new text system a BIT less horrible to work with.
    """
    xx = x+0
    yy = y+0
    
    char_to_glyph = {}
    glist = set()
    clist = {}
    i = 1
    max_x = 0
    for char in s:
        glist.add(char)
        last_char = (i == len(s))
        if char == "\n":
            xx = x+0
            yy -= font.leading()
        else:
            character = font.get_char(char, col)
            if not character.empty:
                offset = -character.image.height+character.bearing
                if char not in char_to_glyph:
                    char_to_glyph[char] = []
                    clist[char] = character
                char_to_glyph[char].append([int(xx)+character.hbearing, yy+offset, round(character.image.width), character.image.height])
            xx += character.advance
            if font.font.has_kerning and not last_char:
                if not s[i] == "\n":
                    kern = font.font.get_kerning(ord(char), ord(s[i]), mode=0).x / 64.0
                    xx += kern
            max_x = max(max_x, xx)
            if tracking:
                xx += (font.tracking() * font.pointSize() / 2000)
        i += 1
    
    under = font.get_char("_", col)
    top_o = under.image.height - under.bearing + 4
    if more:
        return glist, clist, char_to_glyph, top_o, max_x
    else:
        return glist, clist, char_to_glyph, top_o

class Text(GraphicRenderable):

    def __init__(self, font : TTFont, str, debug=False):
        GraphicRenderable.__init__(self)
        self.fnt = font
        self.s = builtins.str(str)
        self.lasts = builtins.str(self.s)
        self.bounds = None
        self.text_bounds = (0, 0)
        self.buf = BytesIO()
        self.glist = None
        self.rtex = None
        self.debug = debug
        self.ksize = None
        self.draw_off = (0, 0)
        self.top_offset = 0
        
        self.processed = False
    
    def process(self):
        if self.processed:
            return
        self.processed = True
        glist, clist, ctg, top_o, max_x = build_glyph_list(0, 0, self.s, tuple([round(c*255) for c in self._color]), self.fnt, more=True)
        vv = list(ctg.values())
        try:
            x_min = min([min(x, key=lambda val: val[0]) for x in vv], key=lambda val: val[0])[0]
        except:
            return
        y_min = min([min(y, key=lambda val: val[1]) for y in vv], key=lambda val: val[1])[1]
        #x_mx = max([max(x, key=lambda val: val[0]+val[2]) for x in vv], key=lambda val: val[0]+val[2])
        y_mx = max([max(y, key=lambda val: val[1]+val[3]) for y in vv], key=lambda val: val[1]+val[3])
        x_max = max_x #x_mx[0]+x_mx[2]
        y_max = y_mx[1]+y_mx[3]
        rtw = abs(x_max-x_min)
        rth = abs(y_max-y_min)
        self.text_bounds = (rtw, rth)
    
    def unload(self):
        if self.rtex:
            rg.rl.unload_render_texture(self.rtex)

    def font(self):
        return self.fnt
        return

    def str(self):
        return self.s
        return

    def size(self):
        self.process()
        return self.text_bounds #ksize or get_text_size(self.s, tuple([round(c*255) for c in self._color]), self.fnt, self)

    def setBoundingBoxSize(self, w, h):
        self.bounds = (w, h)
    
    def setColor(self, r=0, g=0, b=0, a=1):
        super().setColor(r, g, b, a)
        self.process()
        return
        


class Marquee(Text):

    def __init__(self, font, str, step=2, repeat=1):
        Text.__init__(self, font, str)
        
        self.step = step
        self.repeat = repeat
        self.pos = 0
        return

    def setSpeed(self, step):
        #return _renderd.Marquee_setSpeed(self, step)
        self.step = step
        return
    
    

class QTMovie(GraphicRenderable):

    def __init__(self, name, evict=0):
        self.loop = 0
        self.idx = -1
        GraphicRenderable.__init__(self)
        self.images = []
        _renderd.createQTMovie(self, name, evict)
        return

    def getNumFrames(self):
        return len(self.images)
        return

    def setLooping(self, looping):
        self.loop = looping
        return

    def unload(self):
        if self.images is not None:
            for im in self.images:
                if im is not None:
                    rg.rl.unload_image(im)
                im = None
        self.images = []
        if self.textures is not None:
            for tx in self.textures:
                if tx is not None:
                    rg.rl.unload_texture(tx)
                tx = None
        self.textures = []

class Icon(GraphicRenderable):

    def __init__(self, name:str, evict=0, loop=1, delayAnim=0):
        GraphicRenderable.__init__(self)
        if name.startswith("/rsrc/icons_s/"):
            name = name.replace("/rsrc/icons_s/", "/media/icons/small/", 1)
        
        if name.startswith("/rsrc/icons_m/"):
            name = name.replace("/rsrc/icons_m/", "/media/icons/medium/", 1)
        
        if name.startswith("/rsrc/icons_l/"):
            name = name.replace("/rsrc/icons_l/", "/media/icons/large/", 1)
        self.name = name
        self.evict = evict
        self.unloaded = False
        self.loop = loop
        self.delayAnim = delayAnim
        _renderd.createIcon(self, name, evict)
        return
    
    def unload(self):
        if self.unloaded:
            return
        if self.textures:
            for i, tx in enumerate(self.textures):
                if tx is not None:
                    print(f"unloading texture {i}")
                    rg.rl.unload_texture(tx)
                tx = None
        if self._ims:
            print(self._ims)
            print(self.name)
            for i, im in enumerate(self._ims):
                if im is not None:
                    print(f"unloading image {i}")
                    rg.rl.unload_image(im)
                self._ims[i] = None
        self.unloaded = True

class DynamicImage(GraphicRenderable):
    def __init__(self, target, filter, evict=0):
        GraphicRenderable.__init__(self)
        target.addDynamicFilter(filter)

class Image(GraphicRenderable):
    pass

class JPEG_Image(Image):

    def __init__(self, name, evict=0, x1=0, y1=0, x2=1, y2=1):
        Image.__init__(self)
        _renderd.createImage(self, name, evict, x1, y1, x2, y2)
        return
    def unload(self):
        if self.texture:
            print("Unloading Texture...")
            rg.rl.unload_texture(self.texture)
        if self.im2:
            print("Unloading Image...")
            rg.rl.unload_image(self.im2)


class TIFF_Image(Image):

    def __init__(self, name, evict=0, x1=0, y1=0, x2=1, y2=1):
        Image.__init__(self)
        _renderd.createImage(self, name, evict, x1, y1, x2, y2)
        return
    def unload(self):
        if self.texture:
            print("Unloading Texture...")
            rg.rl.unload_texture(self.texture)
            self.texture = None
        if self.im2:
            print("Unloading Image...")
            if rg.rl.is_image_valid(self.im2):
                rg.rl.unload_image(self.im2)
                self.im2 = None
class CompositedImage(Image):

    def __init__(self, debug=False):
        GraphicRenderable.__init__(self)
        self.rtex = None
        self.ftex = None
        self._size = (720, 480)
        self.items = []
        self.debug = debug
        return

    def unload(self):
        if self.rtex:
            rg.rl.unload_render_texture(self.rtex)
            self.rtex = None
        if self.ftex:
            rg.rl.unload_render_texture(self.ftex)
            self.ftex = None

    def bounds(self):
        return None

    def addItem(self, child):
        if type(child) in (Text, Clock):
            rg.text_queue.append(child)
            child.process()
        self.items.append(child)
        return
    

class ClipboardImage(Image):

    def __init__(self):
        GraphicRenderable.__init__(self)
        #_renderd.createClipboardImage(self)
        return

import json
class VectorImage(GraphicRenderable):
    """A image made up of points, lines, and curves."""

    def __init__(self, name, lineThickness=1, evict=0):
        GraphicRenderable.__init__(self)
        self.polys = []
        self.lineThickness = lineThickness
        self.im = None
        self.tx = None
        if os.path.exists(name + ".vg"):
            with open(name + ".vg", "r") as f:
                fl = json.loads(f.read())
            self._size = (fl[0], fl[1])
            self.polys = fl[2]
            buf = BytesIO()
            tempsurf = rg.pg.Surface((fl[0], fl[1]), rg.pg.SRCALPHA)
            
            for pol in self.polys:
                rg.pg.draw.lines(tempsurf, (255, 255, 255), False, pol, self.lineThickness)
            rg.pg.image.save(tempsurf, buf, ".bmp")
            bv = buf.getvalue()
            self.im = rg.rl.load_image_from_memory(".bmp", bv, len(bv))
    
    def unload(self):
        if self.tx:
            rg.rl.unload_texture(self.tx)
            self.tx = None
        if self.im:
            rg.rl.unload_image(self.im)
            self.im = None
        #_renderd.createVectorImage(self, name, lineThickness, evict)

import nethandler as nh
class CompositeRenderable(GraphicRenderable):

    def __init__(self, debug=False):
        GraphicRenderable.__init__(self)
        self.rtex = None
        self.ftex = None
        self._size = (720, 480)
        self.items = []
        self.cached_items = []
        self.debug = debug
        self.positioned = False
        return

    def unload(self):
        if self.rtex:
            rg.rl.unload_render_texture(self.rtex)
            self.rtex = None
        if self.ftex:
            rg.rl.unload_render_texture(self.ftex)
            self.ftex = None

    def addItem(self, child):
        child.added = True
        if type(child) in (Text, Clock):
            rg.text_queue.append(child)
            child.process()
        self.items.append(child)
        self.cached_items.append((child.position(), child.size()))
        return

    def bounds(self):
        top = None
        right = None
        left = 0
        bottom = 0
        tleft = None
        tbottom = None
        for pos, size in self.cached_items:
            #pos = child.position()
            #size = child.size()
            if not right:
                right = pos[0]+size[0]
            else:
                right = max(right, pos[0]+size[0])
            if not top:
                top = pos[1]+size[1]
            else:
                top = max(top, pos[1]+size[1])
            #keep track of left and bottom, might be useful?
            if not tleft:
                tleft = pos[0]
            else:
                tleft = min(tleft, pos[0])
            if not tbottom:
                tbottom = pos[1]
            else:
                tbottom = min(tbottom, pos[1])
            left = min(pos[0], left)
            bottom = min(pos[1], bottom)
        if not top:
            top = 0
        if not right:
            right = 0
        
        return (left, bottom, right, top, tleft, tbottom)
        #return (abs(right-left), abs(top-bottom))
    
    def size(self):
        b = self.bounds()
        return (abs(b[2]), abs(b[3]))
    
    def bsize(self):
        xx, yy = self.position()
        
        rell = 0
        relb = 0
        
        for child in self.items:
            rx, ry = child.position()
            rx -= xx
            ry -= yy
            rell = min(rell, rx)
            relb = min(relb, ry)
        
        return rell, relb

class ScrollingCompositeRenderable(CompositeRenderable):

    def __init__(self, step=2, spacing=2, repeat=1):
        GraphicRenderable.__init__(self)
        self.step = step
        self.spacing = spacing
        self.repeat = repeat
        self.scroll = 0
        self.rtex = None
        self.ftex = None
        self.bbox = (720, 480)
        self.debug = False
        self.items = []
        self.cached_items = []
        return

    def unload(self):
        if self.rtex:
            rg.rl.unload_render_texture(self.rtex)
            self.rtex = None
        if self.ftex:
            rg.rl.unload_render_texture(self.ftex)
            self.ftex = None

    def setSpeed(self, step):
        self.step = step
        return

    def setSpacing(self, spacing):
        self.spacing = spacing
        return

    def setBoundingBoxSize(self, w, h):
        self.bbox = (w, h)
        self._size = (w, h)
        return

    def getBoundingBoxSize(self):
        return self.bbox
        return

    def addItem(self, child):
        self.items.append(child)
        self.cached_items.append((child.position(), child.size()))
        return


class Polygon(GraphicRenderable):

    def __init__(self):
        GraphicRenderable.__init__(self)
        self.vertices = []
        self.leftmost = 0
        self.rightmost = 0
        self.topmost = 0
        self.bottommost = 0
        return

    def addVertex(self, x, y, r=1, g=1, b=1, a=1):
        self.vertices.append((rg.rl.Vector3(x, y, 0), r, g, b, a))
        if x < self.leftmost:
            self.leftmost = x
        if y > self.topmost:
            self.topmost = y
        if x > self.rightmost:
            self.rightmost = x
        if y < self.bottommost:
            self.bottommost = y
        self._size = (abs(self.rightmost-self.leftmost), abs(self.topmost-self.bottommost))
        return

class LineRenderer(GraphicRenderable):
    def __init__(self, thickness=1.0):
        GraphicRenderable.__init__(self)
        self.vertices = []
        self.leftmost = 0
        self.rightmost = 0
        self.topmost = 0
        self.bottommost = 0
        self.thickness = round(thickness)
        self.rgba = (1, 1, 1, 1)
        self.cached = None
        return

    def drawLines(self):
        if self._size == (0, 0):
            return
        tempsurf = rg.pg.Surface(self._size, rg.pg.SRCALPHA)
        
        buf = BytesIO()
        if self.thickness == 1:
            rg.pg.draw.aalines(tempsurf, (255, 255, 255), False, [(v[0]+self.leftmost, self._size[1] - v[1] + self.bottommost) for v in self.vertices])
        else:
            rg.pg.draw.lines(tempsurf, (255, 255, 255), False, [(v[0]+self.leftmost, self._size[1] - v[1] + self.bottommost) for v in self.vertices], self.thickness)
        rg.pg.image.save(tempsurf, buf, ".bmp")
        bv = buf.getvalue()
        self.cached = rg.rl.load_image_from_memory(".bmp", bv, len(bv))

    def addVertex(self, x, y, r=1, g=1, b=1, a=1):
        self.vertices.append((x, y, r, g, b, a))
        self.rgba = (r, g, b, a)
        if x < self.leftmost:
            self.leftmost = x
        if y > self.topmost:
            self.topmost = y
        if x > self.rightmost:
            self.rightmost = x
        if y < self.bottommost:
            self.bottommost = y
        self._size = (abs(self.rightmost-self.leftmost), abs(self.topmost-self.bottommost))
        return
    
    def unload(self):
        if self.tx:
            rg.rl.unload_texture(self.tx)
            self.tx = None
        if self.cached:
            rg.rl.unload_image(self.cached)
            self.cached = None

class RichText(CompositeRenderable):

    def __init__(self, textItemList):
        CompositeRenderable.__init__(self)
        w = 0
        h = 0
        tempList = []
        for item in textItemList:
            (strText, font, color) = item
            (r, g, b, a) = color
            gr = Text(font, strText)
            gr.setColor(r, g, b, a)
            gr.setPosition(w, font.sy)
            (wgr, hgr) = gr.size()
            tempList.append(gr)
            w += wgr
            if hgr > h:
                h = hgr

        self.setSize(w, h)
        for item in tempList:
            self.addItem(item)

        return


class Video(GraphicRenderable):

    def __init__(self):
        GraphicRenderable.__init__(self)
        return


class Effect(ObjectWrapper):

    def setTarget(self, target):
        return


class GraphicEffect(Effect):
    def setTarget(self, target):
        target.addGraphicEffect(self)
    
    def reset(self):
        pass


class NullEffect(GraphicEffect):

    def __init__(self, target=None):
        if target != None:
            self.setTarget(target)
        return


class Bounce(GraphicEffect):

    def __init__(self, target=None, dx=0, dy=0, x=0, y=0, h=720, w=480):
        self.frame = 0
        self.frozen = False
        self.dx = dx
        self.dy = dy
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Slider(GraphicEffect):

    def __init__(self, target=None, dx=0, dy=0):
        self.frame = 0
        self.frozen = False
        self.dx = dx
        self.dy = dy
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Sizer(GraphicEffect):

    def __init__(self, target=None, percentX=1, percentY=1):
        self.frame = 0
        self.frozen = False
        self.percentX = percentX
        self.percentY = percentY
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Strobe(GraphicEffect):

    def __init__(self, target=None, variance=0.49, step=0.01):
        self.frame = 0
        self.frozen = False
        self.variance = variance
        self.step = step
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Fader(GraphicEffect):
    def __init__(self, target=None, startAlpha=0, endAlpha=1, frames=30):
        self.frame = 0
        self.frozen = False
        self.startAlpha = startAlpha
        self.endAlpha = endAlpha
        self.frames = frames
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Rotate(GraphicEffect):

    def __init__(self, target=None, angle=1, x=0, y=0, xr=0, yr=0, zr=0):
        self.frame = 0
        self.frozen = False
        self.angle = angle
        self.x = x
        self.y = y
        self.xr = xr
        self.yr = yr
        self.zr = zr
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.frame = 0
        self.frozen = False

class Clipper(GraphicEffect):
    CP_LEFT = 0
    CP_RIGHT = 1
    CP_TOP = 2
    CP_BOTTOM = 3

    def __init__(self, target=None, left=None, right=None, top=None, bottom=None):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        if target != None:
            self.setTarget(target)
        self.planeclipper = False
        self.planes = []
        return

    def clip(self, plane, pos, step=0.0):
        self.planes.append([plane, pos, step])
        self.planeclipper = True
        #_renderd.Clipper_clip(self, plane, pos, step)
        return


class Snapshot(GraphicEffect):

    def __init__(self, target=None):
        _renderd.createSnapshot(self)
        if target != None:
            self.setTarget(target)
        return


class SetText(GraphicEffect):

    def __init__(self, str, target=None):
        self.s = str
        self.fired = False
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False


class PropertyEffect(GraphicEffect):
    pass


class SetColor(PropertyEffect):

    def __init__(self, target=None, r=0, g=0, b=0, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.fired = False
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False

class SetColorScale(PropertyEffect):

    def __init__(self, target=None, r=0, g=0, b=0, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        if target != None:
            self.setTarget(target)
        return


class SetSize(PropertyEffect):

    def __init__(self, target=None, w=1, h=1):
        self.w = w
        self.h = h
        self.fired = False
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False

class SetSizeScale(PropertyEffect):

    def __init__(self, target=None, w=1, h=1):
        self.w = w
        self.h = h
        if target != None:
            self.setTarget(target)
        return


class SetPosition(PropertyEffect):

    def __init__(self, target=None, x=0, y=0):
        self.x = x
        self.y = y
        self.fired = False
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False
class SetRotationAngle(PropertyEffect):

    def __init__(self, target=None, angle=1):
        self.angle = angle
        self.fired = False
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False

class SetAnimationState(Effect):

    def __init__(self, target=None, state=1):
        self.state = state
        if target != None:
            self.setTarget(target)
        return


class SetVisibility(Effect):

    def __init__(self, target=None, visible=1):
        self.visible = visible
        self.fired = False
        self.frame = 0
        self.frozen = False
        
        self.fader = None
        if target != None:
            self.setTarget(target)
        return

    def reset(self):
        self.fired = False
        self.frame = 0
        self.frozen = False
#thanks to cctl for being based for this one moment
class FilterPipeline(ObjectWrapper):
    """ A container to apply multiple subsequent filters to image data.
        Methods:
            addFilter: Add another ImageFilter implementation to the pipeline.
            process: Execute the pipeline on the given image, applying filters
                in the order they were added to the pipeline, and return
                a new Image with the result.
    """

    def __init__(self):
        #_renderd.createFilterPipeline(self)
        return

    def addFilter(self, imageFilter):
        """ Add a new filter to the pipeline. Filters will be applied in the
            order they were added.
        """
        #_renderd.FilterPipeline_addFilter(self, imageFilter)
        return

    def process(self, source):
        """ Process the pipeline, applying all the filters to the source Image,
            and return a new Image as the result.
        """
        #return _renderd.FilterPipeline_process(self, source)
        return


class ImageFilter(ObjectWrapper):
    """ Base, abstract image filter.  Derive image filter implementations from this class. """

    def __init__(self):
        #_renderd.createImageFilter(self)
        return


class GaussianBlurImageFilter(ImageFilter):
    """ Image filter to perform a Gaussian blur on an image.
        Uses a set 8px radius blur kernel.
        Parameters:
            x, y, w, h: Region of the image to which the blur will be applied.
    """

    def __init__(self, x=0, y=0, w=0, h=0):
        #_renderd.createGaussianBlurImageFilter(self, x, y, w, h)
        return


class BlendImageFilter(ImageFilter):
    """ Image filter to blend two separate images, or an image and a mask.
        Blend modes are based on formulae here: http://en.wikipedia.org/wiki/Blend_modes
        Parameters:
          topLayer: an Image object representing the top image or mask to blend.
          mode: Blend mode to use, from one of the class properties defined below.
          opacity: (0.0 - 1.0) If less than 1.0, the result of the blend is alpha blended back into
            the bottom layer with the percentage specified.
          useMaskAlpha: If 1 (true), copy the alpha channel value from the mask to the result image.
          x, y, w, h: Region of the image to which the blend will be applied.
    """
    MODE_SOFT_LIGHT = 1

    def __init__(self, topLayer, mode, opacity=1.0, useMaskAlpha=0, x=0, y=0, w=0, h=0):
        #_renderd.createBlendImageFilter(self, topLayer, mode, opacity, useMaskAlpha, x, y, w, h)
        return

class AudioRenderable(Renderable):
    BLEND_OVERWRITE = 0
    BLEND_MIX = 1
    BLEND_ADD = 2

    def setVolLevel(self, level):
        self.level = level
        return

    def setMixLevel(self, level):
        self.mix = level
        return

    def setBlendType(self, type):
        self.btype = type
        return
    
    def addEffectSequencer(self, seq, repeat, loopLimit):
        self.effects.append(seq)

    def unload(self):
        if self.chan:
            self.chan.stop()
        if hasattr(self, "file"):
            if self.file:
                self.file.stop()
                del self.file

class Audio(AudioRenderable):

    def __init__(self):
        _renderd.createAudio(self)
        return


class AudioClip(AudioRenderable):

    def __init__(self, name, evict=0, duration_limit=0, loop_limit=1):
        _renderd.createAudioClip(self, name, evict, duration_limit, loop_limit)
        self.effects = []
        return

    def setLoopLimit(self, limit):
        self.loop_limit = limit
        return

    def duration(self):
        return int(self.file.get_length()*30)
        return

    def size(self):
        return _renderd.AudioClip_getSize(self)
        return


class NullAudioClip(AudioRenderable):

    def __init__(self, duration_limit=0):
        self.duration_limit = duration_limit
        self.evict = 1
        self.loop_limit = 1
        self.level = 1
        self.mix = 1
        self.chan = None
        self.name = ""
        self.effects = []
        #_renderd.createAudioClip(self, "", 1, duration_limit, 1)
        return

    def duration(self):
        return self.duration_limit

    def size(self):
        return _renderd.NullAudioClip_getSize(self)
        return


class MP3_AudioClip(AudioRenderable):

    def __init__(self, name, evict=0, duration_limit=0, loop_limit=1):
        _renderd.createAudioClip(self, name, evict, duration_limit, loop_limit)
        self.effects = []
        return

    def setLoopLimit(self, limit):
        self.loop_limit = limit
        return

    def duration(self):
        return self.file.get_length()*30


class AudioEffect(Effect):
    def setTarget(self, target):
        target.addAudioEffect(self)

import random
class EffectSequencer(Renderable):

    def __init__(self, target, repeat=0, loopLimit=0, debug=False):
        self.effects = []
        self.activeeffects = []
        self.timer = (not getattr(target, "added", True))-1 #+target.seq_start_after #first frame is time 0 but 1 gets added first
        self.timerdefault = (not getattr(target, "added", True))-1
        
        self.total = 0
        self.repeat = repeat
        self.loopLimit = loopLimit
        self.skipped = 0
        
        self.target = target
        
        target.addEffectSequencer(self, repeat, loopLimit)
        return

    def reset(self):
        #renderElog("FEMBOYS", self.effects, self.activeeffects, self.timer, self.timerdefault)
        #self.timer = self.timerdefault+0
        self.timer = 0
        self.activeeffects = []
        for effect in self.effects:
            if type(effect) is tuple:
                effect[0].reset()
            else:
                effect.reset()

    def _eval_fader(self):
        if len(self.effects) > 1:
            for i in range(len(self.effects)-1):
                if (type(self.effects[i][0]) == SetVisibility) and (type(self.effects[i+1][0]) == Fader):
                    self.effects[i][0].fader = self.effects[i+1][0].startAlpha
                elif (type(self.effects[i][0]) == SetVisibility):
                    self.effects[i][0].fader = None
    
    def addEffect(self, effect, duration, confirm=False):
        self.effects.append((effect, duration or 9999999999999999999999)) #band-aid fixes ftw
        self.total += duration
        self._eval_fader()
        return

    def unload(self):
        self.effects = []
        self.activeeffects = []

class ImageSequencer(Renderable):

    def __init__(self, repeat=0):
        self.repeat = repeat
        self.images = []
        return

    def addImage(self, imageFile, duration):
        self.images.append((imageFile, duration))
        return


class AudioSequencer(AudioRenderable):

    def __init__(self, repeat=0):
        self.timer = 0
        self.done = False
        self.playingidx = 0
        self.repeat = repeat
        self.audio = []
        self.effects = []
        self.level = 1
        self.mix = 1
        return

    def addItem(self, child):
        self.audio.append(child)
        return

    def duration(self):
        return sum([e.duration() for e in self.audio])-len(self.audio)
        return

    def size(self):
        return _renderd.AudioSequencer_getSize(self)
        return
    
    def unload(self):
        for a in self.audio:
            a.unload()
        self.audio = []

class AudioFader(AudioEffect):

    def __init__(self, target=None, startMixLevel=0, endMixLevel=1, frames=30):
        self.startMixLevel = startMixLevel
        self.endMixLevel = endMixLevel
        self.frames = frames
        self.frozen = False
        self.frame = 0
        if target != None:
            self.setTarget(target)
        return


class AudioEffectSequencer(Renderable):

    def __init__(self, target, repeat=0):
        self.total = 0
        self.effects = []
        self.activeeffects = []
        self.timer = -1 #first frame is time 0 but 1 gets added first
        self.timerdefault = self.timer
        self.repeat = repeat
        target.addEffectSequencer(self, repeat, 1)
        return

    def addEffect(self, effect, duration):
        self.effects.append((effect, duration))
        self.total += duration
        return

    def reset(self):
        self.timer = -1
        self.activeeffects.clear()

class AudioNullEffect(AudioEffect):

    def __init__(self, target=None):
        if target != None:
            self.setTarget(target)
        return