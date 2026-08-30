import sys
if __name__ != "__main__":
    print("ggwp")
    import tscard
else:
    print("Adding patches...")
    import patches
    renderElog("Loading renderE...")
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    renderElog("Importing rendereglobals...")
    import rendereglobals as rg
    import pyray as rl
    renderElog("Importing receiverE...")
    import receivere
    renderElog("Importing loadhelpers...")
    import loadhelpers
    import math
    from PIL import Image
    from io import BytesIO
    renderElog("Importing RenderScript...")
    from twc.embedded.renderd.RenderScript import *
    renderElog("Importing RenderControl...")
    import twc.embedded.renderd.RenderControl as RenderControl
    renderElog("Importing renderUtil...")
    import twc.embedded.renderd.renderUtil as renderUtil
    renderElog("Importing renderTools...")
    import domestic.renderTools as renderTools
    renderElog("Importing twc...")
    import twc
    renderElog("Importing twccommon.embedded...")
    import twccommon.embedded
    import domesticpy.conf.receiverd
    #wccommon.embedded.runconfpy(os.path.join(os.path.dirname(__file__), "domesticpy", "conf", "receiverd.py"))
    import socket
    import threading as th
    import time
    import random
    import gc

    import builtins

    renderElog("Importing playman...")
    if twc.personality == "WxScan":
        import wxscanpy.plugin.playman.playCmd.local as pmlc
        import wxscanpy.plugin.playman.playCmd.pm as pm
        import wxscanpy.plugin.playman.playCmd.ldl as pmldl
        import wxscanpy.plugin.playman.playCmd.bulletin as pmbl
    else:
        import domesticpy.plugin.playman.playCmd.local as pmlc
        import domesticpy.plugin.playman.playCmd.pm as pm
        import domesticpy.plugin.playman.playCmd.ldl as pmldl
        import domesticpy.plugin.playman.playCmd.bulletin as pmbl
    import domestic.wxdata
    import json
    import traceback as tb
    from datetime import datetime
    renderElog("Importing dsmarshal...")
    import twc.dsmarshal as dsm
    dsm.server = True
    import pickle
    import argparse
    renderElog("Importing tscard...")
    import tscard
    
    renderElog("Imports done!")

    rg.pg.mixer.init(frequency=48000, size=-16, channels=2)

    DEBUG = False
    SAVECR = False

    vidtex = None

    sdi = False
    music_player = False

    aparse = argparse.ArgumentParser()
    aparse.add_argument("uri", nargs="?", help="Sets a URI for the media player.")
    aparse.add_argument("-t", "--trans", action="store_true", help="Makes the window have a transparent background. This is useful for overlaying the LDL on content without using the built-in video system.")
    aparse.add_argument("-n", "--noframe", action="store_true", help="Removes the window frame.")
    aparse.add_argument("-o", "--offline", action="store_true", help="Disabled network connectivity.")
    aparse.add_argument("-g", "--grateful", action="store_true", help="Signifies that you are grateful for what you already have, and that you wouldn't like any more TWC content.")
    aparse.add_argument("-bgm", "--bgmplayer", action="store_true", help="Enables a music player that shuffles all files in the \"bgm\" folder.")
    aparse.add_argument("-v", "--verbose", action="store_true", help="Adds a lot of additional logging")
    args = aparse.parse_args()

    grateful = args.grateful
    VERBOSE = args.verbose

    import nethandler as nh
    nh.offline = args.offline

    if args.bgmplayer:
        music_player = True
        print("WxScan music player enabled!")
        tscard.DISABLE_AUDIO = True

    if args.uri:
        path = args.uri
        sdi = True
        tscard.SDI_URL = sys.argv[1]
        print(f"Set SDI URL to {sys.argv[1]}")

    fov = 60
    screensize = (720, 480)
    zzz = 1

    if VERBOSE:
        renderElog("Setting window config flags...")
    rl.set_config_flags((rl.ConfigFlags.FLAG_WINDOW_UNDECORATED * args.noframe) | (rl.ConfigFlags.FLAG_WINDOW_TRANSPARENT * args.trans) | rl.ConfigFlags.FLAG_WINDOW_ALWAYS_RUN | rl.ConfigFlags.FLAG_WINDOW_HIGHDPI)
    if VERBOSE:
        renderElog("Binding data socket (localhost:7245)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 7245))

    # im = rl.load_image(os.path.join(os.environ["RENDEREROOT"], "icon.png"))
    # im2 = rl.load_image(os.path.join(os.environ["RENDEREROOT"], "icon.png"))
    # rl.image_resize(im2, 128, 128)
    # im3 = rl.load_image(os.path.join(os.environ["RENDEREROOT"], "icon.png"))
    # rl.image_resize(im3, 64, 64)
    # im4 = rl.load_image(os.path.join(os.environ["RENDEREROOT"], "icon.png"))
    # rl.image_resize(im4, 32, 32)
    # rl.set_window_icons((im, im2, im3, im4), 4)

    def loadtif(filename): 
        im = Image.open(filename)
        arr = BytesIO()
        im.save(arr, format="PNG")
        arr = arr.getvalue()
        im2 = rl.load_image_from_memory('.png', arr, len(arr))
        return (rl.load_texture_from_image(im2), im2.width, im2.height)

    names = ["RenderE" for _ in range(47)] + ["ReReRenderD", "RemixD", "RenderD"]
    windbg = ""

    splashes = [
        "Functioning not guaranteed",
        "From Wikipedia, the free encyclopedia",
        "I'm Southbridge Cable Network, and I approve this message",
        "Brought to you by SpecifiCable Communications",
        "Trusted. Reliable. Accurate.",
        "It could be better with your help!",
        "The original IntelliStrons I",
        "No more ancient hardware now.",
        "I don't want your SVG remakes.",
        "100% Original Recipe!",
        "Thunderstorm card not guaranteed.",
        "The programmer has a nap. Holdout! Programmer!",
        "The letter R has the correct vertical size",
        "specificable.lewolfyt.cc",
        "Weather. Technology. Freedom. SpecifiCable.",
        "I hope your computer is decent!",
        "We call it the CPU fryer 9000.",
        "bash: fortune: command not found",
        "We're gonna take it into overtime",
        "3D was definitely drunk while working on the i1",
        "Remember that greed is one of the seven deadly sins.",
        "Let's put this show together.",
        "The IntelliStar for the common man, woman, or otherwise stated.",
        "We do TWC preservation, the right way.™",
        "Weather coverage you can count on.",
        "Prepare your computer! It's gonna get ugly.",
        "Now you can be the MSO everyone needs.",
        "There is no such thing as the RenderD window.",
        "Run that funky forecast, white boy!",
        "Azmo, brick, biatch, and now.. this. Hello!",
        "Holla Holla get $",
        "R.I.P. NRi1. You will be missed.",
        "The only simulator to have allegedly won three purple hearts!",
        "If the graphics are broken, blow into it and try again."
    ]

    fortune = random.choice(splashes)
    if VERBOSE:
        renderElog("Initializing window...")
    rl.init_window(screensize[0], screensize[1], f"{random.choice(names)} - {fortune}")

    camx = 0
    camy = 0
    zzz = screensize[1] / (2*math.tan(math.radians(fov/2)))
    camera = rl.Camera3D(
        rl.Vector3(camx, camy, zzz),
        rl.Vector3(camx, camy, 0),
        rl.Vector3(0, 1, 0),
        fov,
        rl.CameraProjection.CAMERA_PERSPECTIVE
    )

    planem = rl.gen_mesh_plane(1, 1, 1, 1)

    def frustum_size_at_z(z, fov_y_deg, aspect_ratio):
        fov_y = math.radians(fov_y_deg)
        height = z * math.tan(fov_y / 2)
        width = height * aspect_ratio
        return width, height


    xxx = screensize[0]/2
    yyy = screensize[1]/2
    #xxx, yyy = frustum_size_at_z(zzz, fov, screensize[0]/screensize[1])
    renderElog(xxx, yyy, zzz)
    # xxx = 2.6
    # yyy = 1.72

    plane = rl.load_model_from_mesh(planem)

    defaulttex = plane.materials[0].maps.texture

    rl.rl_disable_backface_culling()

    ee = 0

    def jsontodata(jsond):
        dt = twccommon.Data()
        dt.__dict__ = json.loads(jsond)
        return dt

    runrs = patches.runrs
    runrsc = patches.runrsc

    def sockethandle():
        if VERBOSE:
            renderElog("Socket handler initialized!")
        sock.listen()
        while True:
            conn, addr = sock.accept()
            while True:
                print("waiting time!")
                breaking = False
                expecting = int.from_bytes(conn.recv(4), "big")
                data = bytearray()
                dat = None
                while True:
                    cdata = conn.recv(1024) #i'll have to figure out larger data chunks not-today
                    if not cdata:
                        breaking = True
                        break
                    expecting -= len(cdata)
                    data.extend(cdata)
                    if expecting == 0:
                        break
                if breaking:
                    break
                
                if data.split(b" ")[0].decode() == "rset":
                    args = data.split(b" ")
                    buf = BytesIO(b" ".join(args[4:]))
                    val = pickle.Unpickler(buf).load()
                    res = dsm.set(args[1].decode(), val, float(args[2]), int(args[3]), session=1)
                    conn.send(res.encode())
                    conn.shutdown(socket.SHUT_WR)
                    print(f"remotely set {args[1].decode()} to {val}")
                    continue
                elif data.split(b" ")[0].decode() == "rget":
                    args = data.split(b" ")
                    buf = BytesIO()
                    try:
                        dat = dsm.get(args[1].decode(), session=1)
                    except:
                        dat = None
                    pickle.Pickler(buf).dump(dat)
                    conn.send(buf.getvalue())
                    conn.shutdown(socket.SHUT_WR)
                    print("remotely got")
                    continue
                elif data.split(b" ")[0].decode() == "rcommit":
                    dsm.ds.commit(1)
                    continue
                
                data = data.decode().strip()
                args = data.split(" ")
                if args[0] == "runrs":
                    runrs(args[1])
                elif args[0] == "runrsc":
                    try:
                        runrsc(args[1])
                    except:
                        tb.print_exc()
                elif args[0] == "jsonload":
                    if not grateful:
                        prodType = args[1]
                        dat = jsontodata(" ".join(args[2:]))
                        try:
                            domestic.wxdata.loadData(prodType, dat)
                        except:
                            tb.print_exc()
                elif args[0] == "jsonrun":
                    if grateful:
                        l = Layer()
                        p = Page(300)
                        l.addPage(p)
                        renderTools.dataNotAvailable(page=p, yPos=240+30, displayDuration=300, text="I worked hard to make this program! Get a real i1!")
                        renderTools.dataNotAvailable(page=p, yPos=240, displayDuration=300, text="Be grateful that we even have i1 images!")
                        renderTools.dataNotAvailable(page=p, yPos=240-30, displayDuration=300, text="Some people want to be handed everything in life.")
                        
                        RenderControl.createNamedLayer("Foreground", 51, 0, 1, 0, 0)
                        RenderControl.setLayer("Foreground", l, time.time(), 0)
                        RenderControl.activateLayer("Foreground", time.time(), 0)
                    else:
                        prodType = args[1]
                        dat = jsontodata(" ".join(args[2:]))
                        try:
                            domestic.wxdata.runData(prodType, dat)
                        except:
                            tb.print_exc()
                elif args[0] == "setbulletin":
                    print("setbulletin")
                    dat = jsontodata(" ".join(args[2:]))
                    domestic.wxdata.setBulletin(args[1], dat, dat.expiration)
                elif args[0] == "togglenat":
                    print("togglenat")
                    dat = json.loads(" ".join(args[1:]))
                    try:
                        domestic.wxdata.toggleNationalLDL(*dat)
                    except:
                        tb.print_exc()
                elif args[0] == "activatel":
                    RenderControl.activateLayer(args[1], 0)
                elif args[0] == "deactivatel":
                    RenderControl.deactivateLayer(args[1], 0)
                elif args[0] == "createtest":
                    RenderControl.destroyNamedLayer("Foreground", 0)
                    producttest()
                else:
                    print(args)
            conn.close()

    tth = th.Thread(target=sockethandle, daemon=True)
    tth.start()
    if VERBOSE:
        renderElog("Socket handler thread started.")

    #prodloader = pm._ProdLoader()

    def fsplash():
        l = Layer()
        p = Page()
        l.addPage(p)

        gr = Box()
        gr.setSize(720,480)
        r,g,b,a = renderUtil.rgbaConvert(235,235,235)
        gr.setColor(r,g,b,a)
        p.addItem(gr)

        quad2 = TIFF_Image("/rsrc/images/renderELogo")
        quad2.setSize(360, 240)
        quad2.setPosition(180, 120)

        Rotate(quad2, .9, xr=1)
        Rotate(quad2, .8, yr=1)
        Rotate(quad2, .7, zr=1)

        gr = Box()
        gr.setSize(720, 110)
        r, g, b, a = renderUtil.rgbaConvert(20, 20, 20)
        gr.setColor(r, g, b, a)
        p.addItem(gr)

        # gr = TIFF_Image()
        # gr.setSize(720, 110)
        # r, g, b, a = renderUtil.rgbaConvert(20, 20, 20)
        # gr.setColor(r, g, b, a)
        # p.addItem(gr)

        p.addItem(quad2)

        f = TTFont("/rsrc/fonts/Frutiger_Bold", 16, shadow = 0)
        r,g,b,a = renderUtil.rgbaConvert(255, 212,  14)
        gr = Text(f, 'headend Id: 322737')
        gr.setPosition(70,92)
        gr.setColor(r,g,b,a)
        p.addItem(gr)
        gr = Text(f, 'serial number: N/A')
        gr.setPosition(70,76)
        gr.setColor(r,g,b,a)
        p.addItem(gr)
        gr = Text(f, 'location name: Minneapolis')
        gr.setPosition(70,60)
        gr.setColor(r,g,b,a)
        p.addItem(gr)
        gr = Text(f, 'affiliate name: XFINITY TV')
        gr.setPosition(70,44)
        gr.setColor(r,g,b,a)
        p.addItem(gr)
        
        cr = CompositeRenderable()

        filename = "/rsrc/logos/twcLogo"
        gr = TIFF_Image(filename)
        gr.setPosition(600, 62)
        #p.addItem(gr)
        cr.addItem(gr)
        filename = "/rsrc/logos/wxScanLogo"
        gr = TIFF_Image(filename)
        gr.setPosition(490, 44)
        #p.addItem(gr)
        cr.addItem(gr)
        
        p.addItem(cr)

        #name, layer, time, frameOffset, depth, repeat, x, y, w, h, sx, sy, tx, ty, activated
        rg.layers.append(["Foreground", l, 0, 0, 10, 0, 0, 0, *screensize, 1, 1, 0, 0, False])

    def ebucolorbars():
        RenderControl.createNamedLayer("Video", 25, 0, 0, 0, 0)
        l = Layer()
        p = Page()
        l.addPage(p)
        im = JPEG_Image(rg.newjoin(os.environ["RENDEREROOT"], "ebu"))
        im.setSize(*screensize)
        im.setPosition(0, 0)
        p.addItem(im)
        RenderControl.appendLayer("Video", l)
        RenderControl.activateLayer("Video")

    #ebucolorbars()

    def producttest():
        l = Layer()
        p = Page(0)
        l.addPage(p)
        
        print("loadedbg")

        ru = renderUtil

        gr = TIFF_Image("/rsrc/backgrounds/domestic")
        gr.setPosition(0, 0)
        p.addItem(gr)
        
        scroll = -10
        
        c = Clipper(gr)
        c.clip(Clipper.CP_TOP, 480, scroll)
        
        cr = CompositeRenderable()
        r,g,b,a = ru.rgbaConvert(212,212,50)
        ff = TTFont('/rsrc/fonts/Interstate-Bold', 24, t=50)
        tt = Text(ff, "WINNERS DON'T USE DRUGS")
        tt.setPosition(50, 50)
        tt.setColor(r,g,b,a)
        cr.addItem(tt)
        tt = Text(ff, "i can feel teh epic duck power")
        tt.setPosition(100, 75)
        tt.setColor(r,g,b,a)
        cr.addItem(tt)
        p.addItem(cr)
        
        es = EffectSequencer(cr, repeat=1)
        es.addEffect(Clipper(None, 10, 10, 10, 10), 1)
        p.addItem(es)
        
        gr = Box()
        gr.setSize(*cr.size())
        gr.setColor(1, 0, 0, 0.5)
        gr.setPosition(50, 50)
        p.addItem(gr)
            
        #new test pattern
        
        back = Box()
        back.setSize(250, 250)
        back.setColor(1, 0, 0, 1)
        back.setPosition(50, 100)
        p.addItem(back)
        
        ###
        l2cr = CompositeRenderable()
        mid1 = Box()
        mid1.setColor(0, 1, 1, 1)
        mid1.setSize(225, 225)
        mid1.setPosition(25, 25)
        Clipper(mid1, 0, 25, 0, 0)
        mid2 = Box()
        mid2.setColor(1, 1, 0, 0.5)
        mid2.setSize(225, 225)
        mid2.setPosition(0, 0)
        Clipper(mid2, 0, 0, 0, 25)
        l2cr.addItem(mid1)
        l2cr.addItem(mid2)
        l2cr.setPosition(50, 100)
        Clipper(l2cr, 25, 0, 25, 0)
        p.addItem(l2cr)
        ###
        
        blue_template = Box()
        blue_template.setColor(0, 0, 1, 0.5)
        blue_template.setSize(150, 150)
        blue_template.setPosition(100, 150)
        p.addItem(blue_template)
        
        blue_template = Box()
        blue_template.setColor(0, 0, 1, 0.25)
        blue_template.setSize(175, 175)
        blue_template.setPosition(75, 125)
        p.addItem(blue_template)
        
        ######
        l3_cont = CompositeRenderable()
        l3_cont.setPosition(50, 100)
        l3cr = CompositeRenderable()
        l3cr.setPosition(25, 25)
        blue = Box()
        blue.setColor(0, 0, 1, 1)
        blue.setSize(175, 175)
        blue.setPosition(0, 0)
        Clipper(l3cr, 25, 0, 0, 25)
        l3cr.addItem(blue)
        
        fourth = CompositeRenderable()
        fourth.setPosition(25, 25)
        red = Box()
        red.setSize(150, 150)
        red.setPosition(0, 0)
        red.setColor(1, 0, 0, 1)
        Clipper(red, 75, 0, 0, 0)
        
        fourth.addItem(red)
        l3cr.addItem(fourth)
        
        l3_cont.addItem(l3cr)
        p.addItem(l3_cont)
        ######
        
        ###
        l2cr = CompositeRenderable()
        mid1 = Box()
        mid1.setColor(0, 1, 1, 1)
        mid1.setSize(225, 225)
        mid1.setPosition(25, 25)
        Clipper(mid1, 0, 25, 0, 0)
        mid2 = Box()
        mid2.setColor(1, 1, 0, 0.5)
        mid2.setSize(225, 225)
        mid2.setPosition(0, 0)
        Clipper(mid2, 0, 0, 0, 25)
        l2cr.addItem(mid1)
        l2cr.addItem(mid2)
        l2cr.setPosition(450, 100)
        Clipper(l2cr, 25, 0, 25, 0)
        p.addItem(l2cr)
        Clipper(l2cr).clip(Clipper.CP_TOP, 240)
        ###
        
        ######
        l3_cont = CompositeRenderable()
        l3_cont.setPosition(450, 100)
        l3cr = CompositeRenderable()
        l3cr.setPosition(25, 25)
        blue = Box()
        blue.setColor(0, 0, 1, 1)
        blue.setSize(150, 150)
        l3cr.addItem(blue)
        Clipper(blue).clip(Clipper.CP_TOP, 240)
        
        blue = Box()
        blue.setColor(0, 0, 1, 1)
        blue.setSize(150, 150)
        blue.setPosition(50, 0)
        l3cr.addItem(blue)
        Clipper(blue).clip(Clipper.CP_TOP, 240)
        l3_cont.addItem(l3cr)
        p.addItem(l3_cont)
        ######
        
        ic = Icon("/media/icons/medium/Ts")
        ic.setPosition(300, 300)
        ic.setColor(1, 1, 1, 1)
        p.addItem(ic)
        ic = Icon("/media/icons/medium/Ts")
        ic.setPosition(350, 300)
        ic.setColor(1, 1, 1, 0.5)
        p.addItem(ic)
        
        #c = Clipper(testCR)
        #c.clip(Clipper.CP_TOP, 480, scroll)
        
        c = Clipper(gr)
        c.clip(Clipper.CP_TOP, 480, scroll)
        
        # es = EffectSequencer(testCR, repeat=1)
        # es.addEffect(Clipper(None, 10, 10, 10, 10), 1)
        # p.addItem(es)
        
        r,g,b,a = renderUtil.rgbaConvert(20, 20, 20)
        darkLayer2 = Box()
        darkLayer2.setColor(r,g,b,.1)
        darkLayer2.setSize(620, 263)
        darkLayer2.setPosition(50, 117)
        p.addItem(darkLayer2)
        
        topBarPos = ( 50, 401 )

        #logo = TIFF_Image(twc.findRsrc('/logos/TWC-LogoBlack', 'tif'))
        logo = TIFF_Image(twc.findRsrc('/logos/TWC-LogoBlack', 'tif'))
        logo.setPosition( *topBarPos )
        topBarProds = CompositeRenderable()
        topBarProds.addItem(logo)
        p.addItem(topBarProds)
        es = EffectSequencer(topBarProds, repeat=1)
        es.addEffect(Clipper(None, topBarPos[0], 0, 0, 401), 1)
        p.addItem(es)
        
        headlineFont = TTFont ('/rsrc/fonts/AkkoPro-Light', 25, shadow=1, sr=0.039, sg=0.039, sb=0.039, sa=0.5, sx=1, sy=1, t=-10)
        headlinesCR = CompositeRenderable()
        hl = "Test Headline"
        headline = Text(headlineFont, hl)
        r,g,b,a = renderUtil.rgbaConvert(235, 235, 235)
        headline.setColor(r,g,b,a)
        headline.setPosition(60, 356)
        headlinesCR.addItem(headline)
        es = EffectSequencer(headline, repeat=0)
        es.addEffect(NullEffect(None), 120 - 16)
        es.addEffect(Slider(None, 0, 2), 16)
        p.addItem(es)
        
        nhl = "Next Headline"
        nextHeadline = Text(headlineFont, nhl)
        nextHeadline.setPosition(headline.position()[0], headline.position()[1] - 32)
        nextHeadline.setColor(r,g,b,a)
        headlinesCR.addItem(nextHeadline)

        es = EffectSequencer(nextHeadline, repeat = 0)
        es.addEffect(NullEffect(None), 120 - 16)
        es.addEffect(Slider(None, 0, 2), 16)
        p.addItem(es)
        
        p.addItem(headlinesCR)
        tt = Text(ff, repr(headlinesCR.bounds()))
        tt.setPosition(200, 400)
        tt.setColor(r,g,b,a)
        p.addItem(tt)
        
        b = Box()
        b.setColor(0, 1, 0, 0.5)
        b.setSize(*headlinesCR.size())
        b.setPosition(60, 356)
        p.addItem(b)
        
        es = EffectSequencer(headlinesCR, repeat=1)
        es.addEffect(Clipper(None, 0, 0, 0, (headlinesCR.size()[1] - 32) + ((32 - headline.size()[1]) / 2.0)), 1)
        p.addItem(es)
        
        def clipCR(cr, clipLeft=-2, clipRight=0, clipTop=0, clipBottom=0):
            es = EffectSequencer(cr, repeat=1)
            es.addEffect(Clipper(None, clipLeft, clipRight, clipTop, clipBottom), 1)
            p.addItem(es)
        
        def slideOn(txt, timeOn):
            if timeOn != None:
                waitFrames = (timeOn - 3)
                es = EffectSequencer(txt, repeat=1)
                es.addEffect(SetPosition(None, txt.position()[0], txt.position()[1]), 2)
                if waitFrames > 0:
                    # Do we need to wait for a certain frame to begin animation?
                    es.addEffect(NullEffect(None), timeOn - 3)
                es.addEffect(Slider(None, 10, 0), 10)
                es.addEffect(NullEffect(None), 120 - 2 + 3 - 10)
                p.addItem(es)

                timeOn += 2

                Fader(txt, 0, 0, 1)
                es = EffectSequencer(txt, repeat=1)
                if waitFrames > 0:
                    es.addEffect(NullEffect(None), timeOn - 2)
                es.addEffect(Fader(None, 0, 1, 10), 10)
                es.addEffect(NullEffect(None), 120 - 2 - 10)
                p.addItem(es)
            else:
                #es = EffectSequencer(txt, repeat=1)
                #es.addEffect(SetPosition(None, txt.position()[0] + 100, txt.position()[1]), 2)
                #es.addEffect(NullEffect(None), <%-prod.getDuration()%> - 1)
                #p.addItem(es)

                es = EffectSequencer(txt, repeat=1)
                es.addEffect(Fader(None, 1, 1, 1), 1)
                es.addEffect(SetPosition(None, txt.position()[0] + 100, txt.position()[1]), 1)
                es.addEffect(NullEffect(None), 120 - 2)
                p.addItem(es)

        def slideOff(txt, timeOff):
            es = EffectSequencer(txt, repeat=1)
            es.addEffect(NullEffect(None), timeOff - 2)
            es.addEffect(SetPosition(None, txt.position()[0] + 100, txt.position()[1]), 1) 
            es.addEffect(Slider(None, 10, 0), 120 - timeOff + 1)
            p.addItem(es)

            timeOff -=2

            #Fader(txt, 0, 0, 1)
            es = EffectSequencer(txt, repeat=1)
            es.addEffect(NullEffect(None), timeOff - 1)
            es.addEffect(Fader(None, 1, 0, 10), 10)
            es.addEffect(NullEffect(None), 120 - timeOff + 1 - 10)
            #es.addEffect(Fader(None, 0, 1, 1), 1)
            p.addItem(es)
        
        def makeField(crList, xpos, font=None, txtTop=None, tTimeIn=None, tTimeOut=None,
                txtBottom=None, bTimeIn=None, bTimeOut=None, other=None, oTimeIn=None, 
                oTimeOut=None, yOther=None, alpha=None):
            # Consider splitting this up - 14 parameters is quite a few, and this
            # function definitely has more than one responsibility
            newCR = CompositeRenderable()
            
            r,g,b,a = renderUtil.rgbaConvert(235, 235, 235)
            
            if txtTop is not None:    
                txtTop = Text(font, txtTop)
                txtTop.setPosition(0, 55)
                txtTop.setColor(r, g, b, a)
                newCR.addItem(txtTop)
                
            if txtBottom is not None:
                txtBottom = Text(font, txtBottom)
                txtBottom.setPosition(0, 38)
                if alpha is None:
                    a = 1.0
                else:
                    a = alpha
                txtBottom.setColor(r,g,b,a)
                newCR.addItem(txtBottom)
                
            if other is not None:
                other.setPosition(0, yOther)
                newCR.addItem(other)
            
            newCR.setPosition(xpos, 0)
            if True:
                if txtTop is not None:
                    txtTop.setPosition(txtTop.position()[0] - 100, txtTop.position()[1])
                    #slideFX(txtTop, tTimeIn, tTimeOut)
                    slideOn(txtTop, tTimeIn)
                    if tTimeOut is not None:
                        slideOff(txtTop, tTimeOut)
                
                if txtBottom is not None:
                    txtBottom.setPosition(txtBottom.position()[0] - 100, txtBottom.position()[1])
                    #slideFX(txtBottom, bTimeIn, bTimeOut)
                    slideOn(txtBottom, bTimeIn)
                    if bTimeOut is not None:
                        slideOff(txtBottom, bTimeOut)

                if other is not None:
                    other.setPosition(other.position()[0] - 100, other.position()[1])
                    #slideFX(other, oTimeIn, oTimeOut)
                    slideOn(other, oTimeIn)
                    slideOff(other, oTimeOut)

            clipCR(newCR)
            crList.append(newCR)
        
        fieldList = []
        tempFont = TTFont('/rsrc/fonts/AkkoPro-Light', 44, shadow=1, sr=0.039, sg=0.039, sb=0.039, sa=0.5, sx=1, sy=1)
        makeField(fieldList, 289, tempFont, None, None, None, "420" + u'\xb0', 19, 290)
        
        while len(fieldList) > 0:
            p.addItem(fieldList.pop())

        RenderControl.createNamedLayer("Foreground2", 10)
        RenderControl.setLayer("Foreground2", l, 0, 0)

    #producttest()
    #RenderControl.queueCommand(ActivateLayerCmd("Foreground2"), 0)

    if VERBOSE:
        renderElog("Generating debug images...")
    whiteimg = rl.gen_image_color(1, 1, rl.WHITE)
    white = rl.load_texture_from_image(whiteimg)
    redimg = rl.gen_image_color(1, 1, rl.RED)
    red = rl.load_texture_from_image(redimg)
    orangeimg = rl.gen_image_color(1, 1, rl.ORANGE)
    orange = rl.load_texture_from_image(orangeimg)
    blueimg = rl.gen_image_color(1, 1, rl.Color(0, 20, 40, 40))
    blue = rl.load_texture_from_image(blueimg)
    once = True

    def mod2(a, b=720):
        if a == 0:
            return a
        return ((abs(a) % b) * (a/abs(a)))

    def updateseq(seq : EffectSequencer):
        if len(seq.effects) == 0:
            return
        seq.timer += 1
        if seq.timer >= seq.total and seq.repeat:
            seq.reset()
            # seq.timer = seq.timerdefault+0
            # for ef in seq.effects:
            #     if hasattr(ef[0], "timer"):
            #         ef[0].timer = 0
            #     if hasattr(ef[0], "frame"):
            #         ef[0].frame = 0
            #     if hasattr(ef[0], "frozen"):
            #         ef[0].frozen = False
            #     if hasattr(ef[0], "fired"):
            #         ef[0].fired = False
            # seq.activeeffects = []
        
        al = []
        al.append(seq.effects[0][1])
        
        if len(seq.effects) > 0:
            for i in seq.effects[1:]:
                al.append(al[-1]+i[1])
        
            al2 = 0
            al2n = seq.effects[0][1]
            for i, v in enumerate(seq.effects):
                if hasattr(seq.effects[i][0], "fired"):
                    #renderElog("al2 check", seq.timer, type(seq.effects[i][0]).__name__, al2, seq.effects[i][0].fired)
                    if seq.timer >= al2 and seq.timer < al2n:
                        seq.effects[i][0].fired = True
                al2 += v[1]
                if len(seq.effects) > (i+1):
                    al2n += seq.effects[i+1][1]
                else:
                    al2n += 999
        
        ea = 0
        for i in range(len(seq.effects)):
            ea += 1
            if seq.timer < al[i]:
                break
        # if len(seq.activeeffects) < ea:
        #     effects_required = ea+0
        #     adding = effects_required-len(seq.activeeffects)
        #     renderElog("need to add", adding, "effects")
        #     for i in range(adding):
        #         seq.activeeffects.append(seq.effects[len(seq.activeeffects)+i][0])
        
        if ea == len(seq.effects):
            seq.activeeffects = [a[0] for a in seq.effects]
        else:
            seq.activeeffects = [a[0] for a in seq.effects[:ea]]
        
        for i in range(ea-1):
            seq.activeeffects[i].frozen = True
        for i in range(len(seq.activeeffects)):
            if hasattr(seq.effects[i], "fired"):
                seq.activeeffects[i].fired = seq.effects[i].fired
        if seq.timer >= seq.total:
            if not seq.repeat:
                for ef in seq.effects:
                    ef[0].frozen = True

    activedrawlayer = None

    drawlevel = 0

    setposition_absolute = (twc.personalityCode > 2)

    if VERBOSE:
        renderElog("Creating transformation matrices...")
    ident = rl.matrix_identity()
    r90 = rl.matrix_rotate_xyz((math.radians(90), 0, math.radians(0)))
    xyt = rl.matrix_translate(-xxx, -yyy, 0)
    def calceffects(quad):
        qqx, qqy = quad._position
        effects = quad.effects
        qqx = round(qqx)
        qqy = round(qqy)
        if drawlevel == 0:
            qqx *= activedrawlayer[10]
            qqy *= activedrawlayer[11]
        qx, qy = qqx*1, qqy*1
        xw = quad._size[0]
        yw = quad._size[1]
        
        mat = r90
        mat = rl.matrix_multiply(mat, rl.matrix_scale(xw, yw, 1))
        fader = 1
        visible = not not quad.visible
        def applyeffect(effect : GraphicEffect):
            nonlocal mat, xxw, yyw, fader, qx, qy, visible
            if hasattr(effect, "frame"):
                if not effect.frozen:
                    effect.frame += 1
            if type(effect) == Rotate:
                mat = rl.matrix_multiply(mat, rl.matrix_scale(1/1.2, 1, 1))
                if effect.xr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_x(math.radians(effect.angle*effect.frame)))
                if effect.yr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_y(math.radians(effect.angle*effect.frame)))
                if effect.zr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_z(math.radians(effect.angle*effect.frame)))
                mat = rl.matrix_multiply(mat, rl.matrix_scale(1.2, 1, 1))
            elif type(effect) == Slider:
                #xxw -= (effect.dx*effect.frame/720*(xxx*2))
                #yyw -= (effect.dy*effect.frame/480*(yyy*2))
                qx += effect.dx*effect.frame
                qy += effect.dy*effect.frame
            elif type(effect) == Fader:
                if effect.frames == 1:
                    fader = effect.endAlpha
                else:
                    dist = (effect.frame/effect.frames)
                    dist = min(dist, 1)
                    fader = effect.startAlpha*(1-dist) + effect.endAlpha*dist
            elif type(effect) == SetPosition:
                #xxw -= (effect.x)/720*(xxx*2)
                #yyw -= (effect.y)/480*(yyy*2)
                #qx = effect.x
                #qy = effect.y
                if effect.fired:
                    if setposition_absolute:
                        qx = effect.x
                        qy = effect.y
                    else:
                        qx += effect.x
                        qy += effect.y
            elif type(effect) == SetSize:
                quad._size = (effect.w, effect.h)
            elif type(effect) == SetText:
                if isinstance(quad, Text):
                    quad.s = effect.s
            elif type(effect) == SetVisibility:
                visible = effect.visible
                if effect.fader is not None:
                    fader = effect.fader
            elif type(effect) == Clipper:
                if effect.planeclipper:
                    for i, p in enumerate(effect.planes):
                        plane, pos, step = p
                        effect.planes[i][1] += step
            # if hasattr(effect, "frame"):
            #     if not effect.frozen:
            #         effect.frame += 1
            
        def loopover(eflist):
            for effect in eflist:
                if type(effect) == EffectSequencer:
                    updateseq(effect)
                    loopover(effect.activeeffects)
                else:
                    applyeffect(effect)
        loopover(effects)
        # xxw = (-qx-quad._size[0]/2)/720*(xxx*2)
        # yyw = (-qy-quad._size[1]/2)/480*(yyy*2)
        xxw = -round(qx)
        yyw = -round(qy)
        mat = rl.matrix_multiply(mat, xyt)
        if drawlevel == 0:
            xxw -= ((activedrawlayer[6]+activedrawlayer[12]))*activedrawlayer[10]
            yyw -= ((activedrawlayer[7]+activedrawlayer[13]))*activedrawlayer[11]
        
        # if drawlevel == 0:
        #     xxw = (-qx-(quad._size[0]/2*activedrawlayer[10])-activedrawlayer[6]-activedrawlayer[12])/720*(xxx*2)
        #     yyw = (-qy-(quad._size[1]/2*activedrawlayer[11])-activedrawlayer[7]-activedrawlayer[13])/480*(yyy*2)
        # else:
        #     xxw = (-qx-quad._size[0]/2)/720*(xxx*2)
        #     yyw = (-qy-quad._size[1]/2)/480*(yyy*2)
        return xxw, yyw, mat, fader, round(qx), round(qy)

    ps = """
    #version 330

    in vec3 vertexPosition;
    in vec2 vertexTexCoord;
    in vec4 vertexColor;

    out vec2 fragTexCoord;
    out vec4 fragColor;

    uniform mat4 mvp;

    void main() {
        fragTexCoord = vertexTexCoord;
        fragColor = vertexColor;
        
        gl_Position = mvp * vec4(vertexPosition, 1.0);
    }
    """

    lclipfs = """
    #version 330

    in vec2 fragTexCoord;
    in vec4 fragColor;

    uniform sampler2D texture0;
    uniform vec4 colDiffuse;
    uniform vec2 resolution;

    uniform float xx;
    uniform float yy;
    uniform float ww;
    uniform float hh;


    uniform float xx2;
    uniform float yy2;
    uniform float ww2;
    uniform float hh2;

    uniform float ll;
    uniform float rr;
    uniform float tt;
    uniform float bb;

    uniform int disablelayerclip;

    uniform float renderw;
    uniform float renderh;

    out vec4 finalColor;

    void main() {
        vec2 pos = gl_FragCoord.xy / vec2(renderw, renderh) * vec2(720, 480);

        if (((
            (pos.x < xx) ||
            (pos.x > (xx + ww)) ||
            (pos.y < yy) ||
            (pos.y > (yy + hh))
        ) && (disablelayerclip == 0)) ||
        (
            (pos.x < xx2) ||
            (pos.x > (xx2 + ww2)) ||
            (pos.y < yy2) ||
            (pos.y > (yy2 + hh2))
        ) ||
        (
            (pos.x < ll) ||
            (pos.x > rr) ||
            (pos.y < bb) ||
            (pos.y > tt)
        )) {
            discard;
            //finalColor = vec4(pos.x/720, pos.y/480, 0, 1);
        } else {
            vec4 texelColor = texture(texture0, fragTexCoord);
            finalColor = texelColor * colDiffuse * fragColor;
        }
    }"""

    fs = """
    #version 330

    in vec2 fragTexCoord;
    in vec4 fragColor;
    uniform sampler2D texture0;
    uniform vec4 colDiffuse;
    out vec4 finalColor;
    void main() {
        finalColor = texture(texture0, fragTexCoord) * fragColor * colDiffuse;
    }
    """

    if VERBOSE:
        renderElog("Loading shaders...")
    lclipshader = rl.load_shader_from_memory(ps, lclipfs)
    defaultshader = rl.load_shader_from_memory(ps, fs)

    bloc = rl.get_shader_location(lclipshader, "xx")
    bloc2 = rl.get_shader_location(lclipshader, "yy")
    bloc3 = rl.get_shader_location(lclipshader, "ww")
    bloc4 = rl.get_shader_location(lclipshader, "hh")

    bloc5 = rl.get_shader_location(lclipshader, "xx2")
    bloc6 = rl.get_shader_location(lclipshader, "yy2")
    bloc7 = rl.get_shader_location(lclipshader, "ww2")
    bloc8 = rl.get_shader_location(lclipshader, "hh2")

    blocT = rl.get_shader_location(lclipshader, "tt")
    blocB = rl.get_shader_location(lclipshader, "bb")
    blocL = rl.get_shader_location(lclipshader, "ll")
    blocR = rl.get_shader_location(lclipshader, "rr")

    renw = rl.get_shader_location(lclipshader, "renderw")
    renh = rl.get_shader_location(lclipshader, "renderh")

    disablelc = rl.get_shader_location(lclipshader, "disablelayerclip")

    if VERBOSE:
        renderElog("Setting shader defaults...")

    rl.set_shader_value(lclipshader, bloc5, rl.ffi.new('float *', float(0)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, bloc6, rl.ffi.new('float *', float(0)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, bloc7, rl.ffi.new('float *', float(screensize[0])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, bloc8, rl.ffi.new('float *', float(screensize[1])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

    rl.set_shader_value(lclipshader, blocL, rl.ffi.new('float *', float(0)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, blocB, rl.ffi.new('float *', float(0)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, blocT, rl.ffi.new('float *', float(screensize[0])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, blocR, rl.ffi.new('float *', float(screensize[1])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

    renderwidth = rl.ffi.new('float *', rl.get_render_width())
    renderheight = rl.ffi.new('float *', rl.get_render_height())
    screenwidth = rl.ffi.new('float *', screensize[0])
    screenheight = rl.ffi.new('float *', screensize[1])
    
    rl.set_shader_value(lclipshader, renw, renderwidth, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    rl.set_shader_value(lclipshader, renh, renderheight, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

    rl.set_shader_value(lclipshader, disablelc, rl.ffi.new("int *", 0), rl.ShaderUniformDataType.SHADER_UNIFORM_INT)

    toff = [0, 0]
    ancestry_dna = [0, 0]
    def draw_quad(quad : TIFF_Image, tex=white, debug=False, se=False, off=(0, 0), premult=False, clipoverride=None, skip=False, forcebilinear=False, se2=False, ho=(0, 0), hw=None, clo=0, crb=None, crxy=(0, 0)):
        effects = quad.effects
        #rl.set_texture_filter(tex, rl.TextureFilter.TEXTURE_FILTER_POINT)
        plane.materials[0].maps.texture = tex
        if isinstance(quad, Icon):
            rl.set_texture_filter(tex, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
        qqx, qqy = quad._position
        
        clipoverride_override = False
        clipx = 0
        clipy = 0
        clipw = screensize[0]
        cliph = screensize[1]
        
        
        forcebilinear = ((getattr(quad, "optimal_size", quad._size) != quad._size) and isinstance(quad, Icon))
        
        # if isinstance(quad, Clock):
        #     if not skip:
        #         qqy += quad.descent
        #     else:
        #         qqy += 2
        #     #print(quad.ascent-quad.descent, quad.cimg.height)
        #     qqy -= quad.s.count("\n")*quad.fnt.reallineheight
        #     if quad.fnt.shadow:
        #         #qqx -= quad.fnt.sx
        #         qqy -= abs(quad.fnt.sy)+1
        x_offset = 0
        
        qxbase = qqx + x_offset
        qybase = qqy * 1
        if clipoverride:
            qxbase = clipoverride[0]
            qybase = clipoverride[1]
        qqx = qqx+off[0]+x_offset
        qqy = qqy+off[1]
        
        wbase = quad.size()[0]
        hbase = quad.size()[1]
        
        if drawlevel == 0:
            qqx = round(qqx * activedrawlayer[10])
            qqy = round(qqy * activedrawlayer[11])
            qxbase = round(qxbase * activedrawlayer[10])
            qybase = round(qybase * activedrawlayer[11])
        else:
            qqx = round(qqx)
            qqy = round(qqy)
            qxbase = round(qxbase)+toff[0]
            qybase = round(qybase)+toff[1]
            #renderElog(qqx, qqy, qxbase, qybase, wbase, hbase)
        
        qx, qy = qqx*1, qqy*1
        
        #if hw:
        #    wbase, hbase = hw
        if clipoverride:
            wbase = clipoverride[2]
            hbase = clipoverride[3]
        
        if drawlevel == 0:
            wbase *= activedrawlayer[10]
            hbase *= activedrawlayer[11]
        
        absclip_left = 0
        absclip_right = screensize[0]
        absclip_top = screensize[1]
        absclip_bottom = 0
        
        
        
        mat = ident
        fader = 1
        visible = quad.visible*1
        total_angle_x = 0
        total_angle_y = 0
        total_angle_z = 0
        
        q_width = quad._size[0]
        q_height = quad._size[1]
        
        x_off = 0
        y_off = 0
        
        def applyeffect(effect : GraphicEffect):
            if hasattr(effect, "frame"):
                if not effect.frozen and not se and not se2:
                    effect.frame += 1
            nonlocal x_off, y_off, q_width, q_height, mat, xxw, yyw, fader, qx, qy, visible, clipx, clipy, clipw, cliph, absclip_left, absclip_right, absclip_top, absclip_bottom, total_angle_x, total_angle_y, total_angle_z, clipoverride_override, forcebilinear
            if type(effect) == Rotate:
                if effect.xr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_x(math.radians(effect.angle*effect.frame)))
                    total_angle_x += effect.angle*effect.frame
                if effect.yr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_y(math.radians(effect.angle*effect.frame)))
                    total_angle_y += effect.angle*effect.frame
                if effect.zr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_z(math.radians(effect.angle*effect.frame)))
                    total_angle_z += effect.angle*effect.frame
            elif type(effect) == Slider:
                if not se:
                    # xxw -= (effect.dx*effect.frame/720*(xxx*2))
                    # yyw -= (effect.dy*effect.frame/480*(yyy*2))
                    qx += round(effect.dx*effect.frame)
                    qy += round(effect.dy*effect.frame)
            elif type(effect) == Fader:
                dist = (effect.frame/effect.frames)
                if effect.frames == 1:
                    fader = effect.endAlpha
                else:
                    if dist >= 1:
                        fader = effect.endAlpha
                    else:
                        dist = min(dist, 1)
                        fader = effect.startAlpha*(1-dist) + effect.endAlpha*dist
            elif type(effect) == Sizer:
                pX = effect.frame*effect.percentX
                pY = effect.frame*effect.percentY
                
                q_width *= (1+pX)
                q_height *= (1+pY)
                forcebilinear = True
                if crb:
                    qx -= crb[4] * pX
                    qy -= crb[5] * pY
            elif type(effect) == SetPosition:
                if not se:
                    #xxw = (-quad._size[0]/2-effect.x)/720*(xxx*2)
                    # xxw -= (effect.x)/720*(xxx*2)
                    # yyw -= (effect.y)/480*(yyy*2)
                    #qx = effect.x
                    #qy = effect.y
                    if effect.fired:
                        if setposition_absolute:
                            qx = effect.x+ho[0]
                            qy = effect.y+ho[1]
                            if clo:
                                qx -= clo
                        else:
                            qx += effect.x
                            qy += effect.y
            elif type(effect) == SetSize:
                if not se:
                    quad._size = (effect.w, effect.h)
            elif type(effect) == SetText:
                if not se:
                    if isinstance(quad, Text):
                        quad.s = effect.s
            elif type(effect) == SetVisibility:
                #if effect.frozen or effect.frame > 0:
                visible = effect.visible
                if effect.fader is not None:
                    fader = effect.fader
            elif type(effect) == Clipper:
                if effect.planeclipper:
                    for i, p in enumerate(effect.planes):
                        plane, pos, step = p
                        if (not se) and (not se2):
                            effect.planes[i][1] += step
                        pos = effect.planes[i][1]
                        if plane == Clipper.CP_LEFT:
                            absclip_left = pos + crxy[0]
                        if plane == Clipper.CP_RIGHT:
                            absclip_right = pos + crxy[0]
                        if plane == Clipper.CP_TOP:
                            absclip_top = screensize[1]-pos - crxy[1]
                        if plane == Clipper.CP_BOTTOM:
                            absclip_bottom = pos + crxy[1]
                else:
                    el = (effect.left or 0)
                    eb = (effect.bottom or 0)
                    if crb:
                        if type(quad) is ScrollingCompositeRenderable:
                            return
                        #renderElog(toff, "toff", crb)
                        x_o = crxy[0]
                        y_o = crxy[1]
                        clipx = qxbase + el + x_o
                        clipy = qybase + eb + y_o
                        clipw = (crb[2]) - el - (effect.right or 0)
                        cliph = (crb[3]) - eb - (effect.top or 0)
                        clipoverride_override = True
                        return
                    clipoverride_override = True
                    clipx = qxbase + el
                    clipy = qybase + eb
                    
                    clipw = wbase - el - (effect.right or 0)
                    cliph = hbase - eb - (effect.top or 0)
                
            # if hasattr(effect, "frame"):
            #     if not effect.frozen and not se:
            #         effect.frame += 1
        
        def loopover(eflist):
            for effect in eflist:
                if type(effect) == EffectSequencer:
                    if (not se) and (not se2):
                        updateseq(effect)
                    loopover(effect.activeeffects)
                else:
                    applyeffect(effect)
        loopover(effects)
        
        xw = q_width*1
        yw = q_height*1
        if drawlevel == 0:
            xw *= activedrawlayer[10]
            yw *= activedrawlayer[11]
        mat = rl.matrix_multiply(rl.matrix_scale(xw, yw, 1), mat)
        mat = rl.matrix_multiply(r90, mat)
        
        if total_angle_x % 360 != 0 or total_angle_y % 360 != 0 or total_angle_z % 360 != 0:
            forcebilinear = True
        mat = rl.matrix_multiply(mat, xyt)
        if drawlevel == 0:
            xxw = (-qx-(q_width/2*activedrawlayer[10])-activedrawlayer[6]-activedrawlayer[12])
            yyw = (-qy-(q_height/2*activedrawlayer[11])-activedrawlayer[7]-activedrawlayer[13])
        else:
            xxw = (-qx-q_width/2)
            yyw = (-qy-q_height/2)
        plane.transform = mat
        c1, c2, c3, c4 = quad._color
        correct = ((c1 > 1) or (c2 > 1) or (c3 > 1) or (c4 > 1))
        if correct:
            c1 /= 255
            c2 /= 255
            c3 /= 255
            c4 /= 255
        pfader = (1 if not premult else fader)
        if type(quad) in [Box, Icon]: #try expanding to all types if it works
            pfader *= c4
        try:
            col = rl.Color(min(round(quad._color[0]*255*pfader), 255), min(round(quad._color[1]*255*pfader), 255), min(round(quad._color[2]*255*pfader), 255), min(round(quad._color[3]*fader*255), 255))
        except Exception as e:
            print(c1, c2, c3, c4)
            raise e
        if isinstance(quad, Text):
            col = rl.Color(int(255*pfader), int(255*pfader), int(255*pfader), int(255*fader))
        rl.rl_disable_depth_test()
        rl.rl_disable_depth_mask()
        
        rl.set_shader_value(lclipshader, disablelc, rl.ffi.new("int *", int(drawlevel > 0)), rl.ShaderUniformDataType.SHADER_UNIFORM_INT)
        
        if isinstance(quad, DummyQuad) and quad.clipping_override and not clipoverride_override:
            clx, cly, clw, clh = quad.clipping_override
            rl.set_shader_value(lclipshader, bloc5, rl.ffi.new('float *', float(clx)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc6, rl.ffi.new('float *', float(cly)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc7, rl.ffi.new('float *', float(clw)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc8, rl.ffi.new('float *', float(clh)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        else:
            rl.set_shader_value(lclipshader, bloc5, rl.ffi.new('float *', float(clipx)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc6, rl.ffi.new('float *', float(clipy)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc7, rl.ffi.new('float *', float(clipw)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, bloc8, rl.ffi.new('float *', float(cliph)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

        rl.set_shader_value(lclipshader, blocT, rl.ffi.new('float *', float(absclip_top)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value(lclipshader, blocB, rl.ffi.new('float *', float(absclip_bottom)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value(lclipshader, blocL, rl.ffi.new('float *', float(absclip_left)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        rl.set_shader_value(lclipshader, blocR, rl.ffi.new('float *', float(absclip_right)), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        
        if drawlevel == 0:
            rl.set_shader_value(lclipshader, renw, renderwidth, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, renh, renderheight, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
        else:
            rl.set_shader_value(lclipshader, renw, screenwidth, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
            rl.set_shader_value(lclipshader, renh, screenheight, rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
    
        #print(clipx, clipy, clipw, cliph)
        
        if visible:
            plane.materials[0].shader = lclipshader
            rl.set_texture_filter(tex, rl.TextureFilter.TEXTURE_FILTER_BILINEAR if ((drawlevel == 0 and (activedrawlayer[10] != 1 or activedrawlayer[11] != 1))) else (rl.TextureFilter.TEXTURE_FILTER_POINT if not isinstance(quad, Icon) else rl.TextureFilter.TEXTURE_FILTER_BILINEAR))
            rl.draw_model_ex(plane, rl.Vector3(-xxw, -yyw, 0), rl.Vector3(0, 0, 0), 0, rl.Vector3(1, 1, 1), col)

    class DummyQuad():
        def __init__(self, x, y, w, h, effects=[], visible=True, seq_start_after=False, added=False, clipping_override=None):
            self._position = (x, y)
            self._size = (w, h)
            self.effects = effects
            self._color = (1, 1, 1, 1)
            self.visible = visible
            self.seq_start_after = seq_start_after
            self.added = added
            self.clipping_override = clipping_override
        def size(self):
            return self._size
        def position(self):
            return self._position

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

    skip_drawing = False

    def draw_poly(quad : Polygon, tex=white):
        global drawlevel
        effects = quad.effects
        visible = not not quad.visible
        plane.materials[0].maps.texture = tex
        qx, qy = quad._position
        
        mat = rl.matrix_identity()
        fader = 1
        pts2 = quad.vertices
        def applyeffect(effect : GraphicEffect):
            nonlocal mat, xxw, yyw, fader, pts2, visible
            if type(effect) == Rotate:
                mat = rl.matrix_multiply(mat, rl.matrix_scale(1/1.2, 1, 1))
                if effect.xr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_x(math.radians(effect.angle*effect.frame)))
                if effect.yr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_y(math.radians(effect.angle*effect.frame)))
                if effect.zr:
                    mat = rl.matrix_multiply(mat, rl.matrix_rotate_z(math.radians(effect.angle*effect.frame)))
                mat = rl.matrix_multiply(mat, rl.matrix_scale(1.2, 1, 1))
            elif type(effect) == Slider:
                #xxw -= (effect.dx*effect.frame/720*(xxx*2))
                #yyw -= (effect.dy*effect.frame/480*(yyy*2))
                qx += effect.dx*effect.frame
                qy += effect.dy*effect.frame
            elif type(effect) == Fader:
                if effect.frames == 1:
                    fader = effect.endAlpha
                else:
                    dist = (effect.frame/effect.frames)
                    dist = min(dist, 1)
                    fader = effect.startAlpha*(1-dist) + effect.endAlpha*dist
            elif type(effect) == Sizer:
                pX = effect.frame*effect.percentX
                if pX == 0:
                    pX = 1
                pY = effect.frame*effect.percentY
                pts2 = [(rl.Vector3(p[0].x*pX, p[0].y*pY, p[0].z), p[1], p[2], p[3], p[4]) for p in pts2]
            elif type(effect) == SetVisibility:
                visible = effect.visible
                if effect.fader is not None:
                    fader = effect.fader
            if hasattr(effect, "frame"):
                if not effect.frozen:
                    effect.frame += 1
        
        def loopover(eflist):
            for effect in eflist:
                if type(effect) == EffectSequencer:
                    updateseq(effect)
                    loopover(effect.activeeffects)
                else:
                    applyeffect(effect)
        loopover(effects)
        
        if not visible:
            return
        
        xxw = (-qx)
        yyw = (-qy)
        mat = rl.matrix_multiply(mat, rl.matrix_translate(-xxx, -yyy, 0))
        
        # if drawlevel == 0:
        #     xxw -= activedrawlayer[6]
        #     yyw -= activedrawlayer[7]
        mat = rl.matrix_multiply(mat, rl.matrix_translate(-xxw, -yyw, 0))
        
        pts = []
        
        c = quad._color
        for p in pts2:
            a=p[4]*c[3]*fader
            pts.append((rl.vector3_transform(p[0], mat), p[1]*c[0]*a, p[2]*c[1]*a, p[3]*c[2]*a, a))
        
        #pts = pts2
        #rl.rl_enable_smooth_lines()
        rl.rl_begin(rl.RL_TRIANGLES)
        
        for i in range(1, len(pts) - 1):
            # Triangle 1: Vertex 0, i, i+1
            # Setting color per vertex
            rl.rl_color4f(pts[0][1], pts[0][2], pts[0][3], pts[0][4])
            rl.rl_vertex3f(pts[0][0].x, pts[0][0].y, pts[0][0].z)
            
            rl.rl_color4f(pts[i][1], pts[i][2], pts[i][3], pts[i][4])
            rl.rl_vertex3f(pts[i][0].x, pts[i][0].y, pts[i][0].z)
            
            rl.rl_color4f(pts[i+1][1], pts[i+1][2], pts[i+1][3], pts[i+1][4])
            rl.rl_vertex3f(pts[i+1][0].x, pts[i+1][0].y, pts[i+1][0].z)
        rl.rl_end()

    audio_chans = []
    audio_vols = []
    global audio_mixes

    last_sec = []

    def update_audio(item, activeeffects=None):
        if not item.chan and not isinstance(item, NullAudioClip) and item.file:
            item.chan = item.file.play()
        effects = item.effects
        ae = False
        if activeeffects:
            ae = True
            effects = activeeffects
        mixl = item.mix
        def applyeffect(effect : AudioEffect):
            nonlocal mixl
            if type(effect) == AudioFader:
                dist = (effect.frame/effect.frames)
                dist = min(dist, 1)
                mixl = effect.startMixLevel*(1-dist) + effect.endMixLevel*dist
            if not ae:
                if hasattr(effect, "frame"):
                    if not effect.frozen:
                        effect.frame += 1
            
        def loopover(eflist):
            for effect in eflist:
                if type(effect) == AudioEffectSequencer:
                    updateseq(effect)
                    loopover(effect.activeeffects)
                else:
                    applyeffect(effect)
        
        loopover(effects)
        
        if item.chan:
            audio_chans.append(item.chan)
            audio_vols.append(item.level)
            audio_mixes.append(mixl)

    def update_audioseq(seq : AudioSequencer, ex={"mix": None}):
        global windbg
        if len(seq.audio) == 0:
            return
        if seq.done:
            return
        seq.timer += 1
        al = []
        al.append(seq.audio[0].duration())
        if len(seq.audio) > 0:
            for i in seq.audio[1:]:
                al.append(al[-1]+i.duration())
        ea = 0
        for i in range(len(seq.audio)):
            if seq.timer < al[i]:
                break
            ea += 1
        if seq.playingidx != ea:
            if type(seq.audio[seq.playingidx]) not in (NullAudioClip, AudioSequencer):
                seq.audio[seq.playingidx].file.stop()
            seq.playingidx = ea
        if seq.playingidx >= len(seq.audio):
            seq.done = True
            return
        
        effects = seq.effects
        
        
        if type(seq.audio[ea]) == AudioSequencer:
            mixl = seq.mix
            def applyeffect(effect : AudioEffect):
                nonlocal mixl
                if type(effect) == AudioFader:
                    dist = (effect.frame/effect.frames)
                    dist = min(dist, 1)
                    mixl = effect.startMixLevel*(1-dist) + effect.endMixLevel*dist
                if hasattr(effect, "frame"):
                    if not effect.frozen:
                        effect.frame += 1
                
            def loopover(eflist):
                for effect in eflist:
                    if type(effect) == AudioEffectSequencer:
                        updateseq(effect)
                        loopover(effect.activeeffects)
                    else:
                        applyeffect(effect)
            
            loopover(effects)
            
            update_audioseq(seq.audio[ea], {"mix": mixl})
        else:
            item = seq.audio[ea]
            mixl = item.mix
            def applyeffect(effect : AudioEffect):
                nonlocal mixl
                if type(effect) == AudioFader:
                    dist = (effect.frame/effect.frames)
                    dist = min(dist, 1)
                    mixl = effect.startMixLevel*(1-dist) + effect.endMixLevel*dist
                if hasattr(effect, "frame"):
                    if not effect.frozen:
                        effect.frame += 1
                
            def loopover(eflist):
                for effect in eflist:
                    if type(effect) == AudioEffectSequencer:
                        updateseq(effect)
                        loopover(effect.activeeffects)
                    else:
                        applyeffect(effect)
            
            loopover(effects)
            if hasattr(item, "file"):
                if not item.chan and item.file:
                    item.chan = item.file.play()
                audio_chans.append(item.chan)
                audio_vols.append(item.level)
                audio_mixes.append(ex["mix"] if ex["mix"] is not None else mixl)

    mode_3d_tracker = 0

    last_sec = []
    def unload_tree(item):
        print(f"Unloading item of type {type(item).__name__}")
        if hasattr(item, "unload"):
            item.unload()
            last_sec.append(30)
        if hasattr(item, "items"):
            for i in item.items:
                unload_tree(i)
        if hasattr(item, "elements"):
            for i in item.elements:
                unload_tree(i)
        if hasattr(item, "effects"):
            for i in item.effects:
                unload_tree(i)

    iiix = 0
    def page_getter(page_times, timer):
        page_offsets = [0]
        for time in page_times[:-1]:
            if time == 0:
                break
            page_offsets.append(page_offsets[-1]+time)

        page = 0
        for i, o in enumerate(page_offsets):
            if timer >= o:
                page = i
        return page

    ft = 0
    def print_effects(eflist):
        for effect in eflist:
            if type(effect) == EffectSequencer:
                renderElog("ES EFFECTS")
                print_effects(effect.effects)
                renderElog("ACTIVE")
                print_effects(effect.activeeffects)
                renderElog("END ES")
            elif type(effect) is tuple:
                renderElog(effect[0], effect[1])
            else:
                renderElog(type(effect).__name__)
    
    def reset_effects_tree(ef, debug=False):
        if type(ef) in [CompositeRenderable, ScrollingCompositeRenderable]:
            for item in ef.items:
                reset_effects_tree(item)
        if type(ef) is EffectSequencer:
            return
        if type(ef) is AudioEffectSequencer:
            return
        if not hasattr(ef, "effects"):
            return
        for effect in ef.effects:
            effect.reset()
    
    def draw_item(item, extra={"tex": None, "cam": None, "off": (0, 0), "lloop": 0}, scr=False):
        global mode_3d_tracker
        global once
        global drawlevel
        global windbg
        global iiix
        global ft
        if type(item) == Layer:
            #this whole section has been cleaned up because the old one looked like a rat's nest
            item.timer += 1
            if len(item.pages) == 0:
                return
        
            last_forever = (item.pages[-1][1] == 0)
            page_times = [p[1] for p in item.pages]
            total_time = sum(page_times)
            
            if activedrawlayer[5]:
                if (item.timer >= total_time) and (total_time > 0):
                    renderElog("layer reset:", activedrawlayer[0], total_time)
                    item.timer = 0
                    for p in item.pages:
                        for it in p[0]._elements:
                            if type(it) == ScrollingCompositeRenderable:
                                it.scroll = 0
                            reset_effects_tree(it, debug=(len(item.pages) > 2))
            
            current_page = page_getter(page_times, item.timer)
            last_frame_page = page_getter(page_times, item.timer-1)
            next_frame_page = page_getter(page_times, item.timer+1)
        
            # if skip_drawing:
            #     return
        
            
            #print(len(al))
            
            
            
            if item.timer < total_time:
                if item.timer > 0:
                    if next_frame_page != current_page:
                        for cmd in item.pages[current_page][0]._onEndCommands:
                            RenderControl.actuallyRunAQueuedCommand(cmd)
                    if last_frame_page != current_page:
                        #if not activedrawlayer[5]:
                        #    item.pages[last_frame_page] = (None, item.pages[last_frame_page][1])
                        for cmd in item.pages[current_page][0]._onStartCommands:
                            RenderControl.actuallyRunAQueuedCommand(cmd)
                else:
                    for cmd in item.pages[0][0]._onStartCommands:
                        RenderControl.actuallyRunAQueuedCommand(cmd)
            elif item.timer == total_time:
                if not last_forever:
                    for cmd in item.pages[current_page][0]._onEndCommands:
                        RenderControl.actuallyRunAQueuedCommand(cmd)
                    #item.pages[cpage][0].__del__()
            elif item.timer > total_time:
                if not last_forever:
                    return
            
            for cmd in item.pages[current_page][0]._onFrameCommands:
                if item.timer == cmd[1]:
                    RenderControl.actuallyRunAQueuedCommand(cmd[0])
            
            draw_item(item.pages[current_page][0], extra)
        elif type(item) == Page:
            for el in item._elements:
                draw_item(el, extra)
        elif isinstance(item, Icon):
            if item.textures is None:
                item.textures = [None for f in item._ims]
            else:
                item.idx += 1
                if item.loop:
                    item.idx %= item.framect
                else:
                    item.idx = min(item.idx, item.framect-1)
            if item.textures[item.idx] is None:
                item.textures[item.idx] = rl.load_texture_from_image(item._ims[item.idx])
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            draw_quad(item, item.textures[item.idx], off=extra["off"], premult=True)
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif isinstance(item, QTMovie):
            item.idx += 1
            if item.loop:
                item.idx %= len(item.images)
            else:
                item.idx = min(item.idx, len(item.images)-1)
            
            if item.textures[item.idx] is None:
                item.textures[item.idx] = rl.load_texture_from_image(item.images[item.idx])
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            draw_quad(item, item.textures[item.idx], off=extra["off"], premult=True)
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif type(item) is Box:
            #the og quad
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            draw_quad(item, off=extra["off"], premult=True)
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif type(item) is Video:
            if vidtex:
                draw_quad(item, vidtex, off=extra["off"])
        elif isinstance(item, DummyQuad):
            draw_quad(item)
        elif isinstance(item, (Text, Clock)):
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            xo = 0
            if type(item) == Marquee:
                item.pos += item.step
                item.pos %= ((item.ksize or get_text_size(item.s, tuple([round(c*255) for c in item._color]), item.fnt, item))[0]+(720 if not item.bounds else item.bounds[0]))
                xo = round(item.pos-(720 if not item.bounds else item.bounds[0]))
            
            queued = False
            if item.rtex is None:
                item.process()
            if item.rtex is not None:
                sc = (scr and (twc.personalityCode > 1))
                tex = item.rtex.texture
                ho = (0, 0)
                clo = 0
                if type(item) == Clock:
                    if item.justification == Clock.CENTER:
                        xo = item.rtex.texture.width/2
                        clo = item.rtex.texture.width
                    if item.justification == Clock.RIGHT:
                        xo = item.rtex.texture.width
                        clo = item.rtex.texture.width
                #renderElog(item.draw_off)
                #renderElog("has rtex", item._position)
                
                draw_quad(item, tex, off=(item.draw_off[0]+extra["off"][0]-xo, item.draw_off[1]+extra["off"][1]+item.top_offset*sc), premult=True, clo=clo)
            
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
            if isinstance(item, Clock):
                new_s = item.get_format()
                if item.lasts != new_s:
                    item.s = new_s
                    item.lasts = new_s
                    item.processed = False
                    rl.unload_render_texture(item.rtex)
                    item.rtex = None
                    item.process()
            if item.rtex is None:
                rg.text_queue.append(item)
        elif isinstance(item, RichText):
            for i in item.items:
                draw_item(i, {"off": item._position})
        elif type(item) in (CompositeRenderable, ScrollingCompositeRenderable, RichText, CompositedImage):
            drawlevel += 1
            #print(drawlevel)
            if not item.rtex:
                item.rtex = rg.rl.load_render_texture(*screensize)
            if not item.ftex:
                item.ftex = rg.rl.load_render_texture(*screensize)
            rl.end_mode_3d()
            mode_3d_tracker -= 1
            rl.begin_texture_mode(item.rtex)
            rl.clear_background(rl.Color(0, 0, 0, 0))
            rl.rl_set_clip_planes(0.01, 10000)
            
            xx2, yy2, transfo, fader, xx2p, yy2p = calceffects(item)
            
            if DEBUG:
                rl.draw_rectangle_lines(round(-xx2p), round(-yy2p), *screensize, rl.RED)
            
            #print(xx2, yy2)
            #xx2, yy2 = 0, 0
            
            if isinstance(item, ScrollingCompositeRenderable):
                item.scroll -= item.step
                
            
            camera2 = rl.Camera3D(
                rl.Vector3(camx+xx2, camy+yy2, zzz),
                rl.Vector3(camx+xx2, camy+yy2, 0),
                rl.Vector3(0, 1, 0),
                fov,
                rl.CameraProjection.CAMERA_PERSPECTIVE
            )
            # if isinstance(item, RichText):
            #     rl.begin_mode_3d(camera)
            # else:
                
            rl.begin_mode_3d(camera2)
            mode_3d_tracker += 1
            rl.rl_disable_depth_test()
            rl.rl_disable_depth_mask()
            
            camoff = (0, 0)
            xx = 0
            
            global toff
            global ancestry_dna
            old_toff = toff.copy()
            for iii, ch in enumerate(item.items):
                toff = [old_toff[0]+xx2p, old_toff[1]+yy2p]#[old_toff[0]+xx2p,old_toff[1]+yy2p]
                if isinstance(item, ScrollingCompositeRenderable):
                    camoff = (720+xx+item.scroll, 0)
                    #if isinstance(ch, Text):
                    xx += ch.size()[0]
                if isinstance(ch, CompositeRenderable) and not (type(ch) is RichText):
                    #if VERBOSE and (xx2p != 0 or yy2p != 0):
                    #    renderElog(xx2p, yy2p)
                    #renderElog("ancestry dna", ancestry_dna)
                    #renderElog("expect", item._position, ch._position)
                    draw_item(ch, extra={"tex": item.rtex, "cam": camera2, "off": camoff})
                    #ancestry_dna[0] -= xx2p
                    #ancestry_dna[1] -= yy2p
                    #renderElog("ancestry dna2", ancestry_dna)
                    rl.begin_texture_mode(item.rtex)
                    rl.rl_set_clip_planes(0.01, 10000)
                    # if isinstance(item, RichText):
                    #     rl.begin_mode_3d(camera)
                    # else:
                        
                    rl.begin_mode_3d(camera2)
                    mode_3d_tracker += 1
                    rl.rl_disable_depth_test()
                    rl.rl_disable_depth_mask()
                else:
                    draw_item(ch, {"off": camoff, "cam": extra["cam"], "tex": extra["tex"]}, scr=(type(item) is (ScrollingCompositeRenderable)))
            toff = old_toff.copy()
            
            rl.end_mode_3d()
            mode_3d_tracker -= 1
            rl.end_texture_mode()
            
            iiix += 1
            if SAVECR:
                rl.export_image(rl.load_image_from_texture(item.rtex.texture), f"iiimg{iiix}.png")
            
            rl.begin_texture_mode(item.ftex)
            rl.clear_background(rl.Color(0, 0, 0, 0))
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            rl.draw_texture(item.rtex.texture, 0, 0, rl.WHITE)
            rl.end_texture_mode()
            
            drawlevel -= 1
            
            if not extra["tex"]:
                rl.rl_set_clip_planes(0.01, 10000)
                rl.begin_mode_3d(camera)
                mode_3d_tracker += 1
                rl.rl_disable_depth_test()
                rl.rl_disable_depth_mask()
                #rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
                #draw_quad_nocal(DummyQuad(0, 0, 720, 480), item.ftex.texture, transfo, fader)
                
                # if type(item) == RichText:
                #     xxr, yyr = item._position
                #     draw_quad(DummyQuad(xxr, yyr, 720, 480, effects=item.effects), item.ftex.texture, se=True)
                # el
                #rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                b = item.bounds()
                clo = None if not type(item) is ScrollingCompositeRenderable else (*item._position, *item.bbox)
                draw_quad(DummyQuad(0, 0, *screensize, effects=item.effects, visible=item.visible, added=item.added), item.ftex.texture, se=True, premult=True, clipoverride=clo, crb=b, crxy=(xx2p, yy2p))
                rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
            else:
                #rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                rl.begin_texture_mode(extra["tex"])
                rl.rl_set_clip_planes(0.01, 10000)
                rl.begin_mode_3d(extra["cam"])
                mode_3d_tracker += 1
                rl.rl_disable_depth_test()
                rl.rl_disable_depth_mask()
                drawlevel += 1
                b = item.bounds()
                clo = None
                draw_quad(DummyQuad(0, 0, *screensize, effects=item.effects, visible=item.visible, added=item.added), item.ftex.texture, se=True, premult=True, clipoverride=clo, crb=b, crxy=(xx2p, yy2p))
                drawlevel -= 1
                rl.end_mode_3d()
                mode_3d_tracker -= 1
                rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
            if DEBUG:
                rl.draw_rectangle_lines(0, 0, *screensize, rl.BLUE)
                rl.draw_rectangle(0, 470, 10, 10, rl.RED)
            if item.debug or (DEBUG and type(item) is RichText):
                renderElog("crdebug", xx2p, yy2p, setposition_absolute, item.added)
                print_effects(item.effects)
        elif isinstance(item, Image):
            if type(item) is not CompositedImage:
                if not item.texture:
                    if item.im2 is not None:
                        item.texture = rl.load_texture_from_image(item.im2)
                if item.texture:
                    rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                    draw_quad(item, item.texture, off=extra["off"], premult=True)
                    rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif type(item) is Polygon:
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            draw_poly(item)
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif isinstance(item, AudioSequencer):
            update_audioseq(item)
        elif type(item) in (AudioClip, MP3_AudioClip):
            if not item.single_play:
                item.single_play = True
                item.chan = item.file.play()
            update_audio(item)
        elif isinstance(item, PageCommand):
            item.timer += 1
            if item.timer == item.activeFrame():
                RenderControl.actuallyRunAQueuedCommand(item)
        elif isinstance(item, VectorImage):
            if item.polys:
                if item.im:
                    if not item.tx:
                        item.tx = rg.rl.load_texture_from_image(item.im)
                    rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
                    draw_quad(item, item.tx)
                    rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA)
        elif isinstance(item, LineRenderer):
            if not item.vertices:
                return
            if not item.cached:
                item.drawLines()
                item.tx = rl.load_texture_from_image(item.cached)
            draw_quad(item, item.tx)
        else:
            pass
            #print("drawing unrecognized type: ", type(item))

    if VERBOSE:
        renderElog("Initializing playman...")
    import playmaninit
    if VERBOSE:
        renderElog("Playman initialized!...")

    vimg = rl.gen_image_checked(*screensize, 40, 40, rl.BLACK, rl.WHITE)
    vtex = rl.load_texture_from_image(vimg)

    vl = Layer()
    p = Page(0)
    v = Video()
    v.setPosition(0, 0)
    v.setSize(*screensize)
    p.addItem(v)
    vl.addPage(p)
    RenderControl.createNamedLayer("Video", 25, 0, 0)
    RenderControl.setLayer("Video", vl)
    RenderControl.activateLayer("Video")

    trans = False

    starid = dsm.defaultedGet("starId", "StarID Unavailable")

    MUTE = False

    if sdi:
        renderElog("Waiting for SDI...")
        sdih = tscard.Handler(tscard.SDI_URL)

    if twc.personality == "WxScan":
        if VERBOSE:
            renderElog("Initializing WxScan ticker...")
        import wxscanpy.plugin.playman.playCmd.rsload as pmrs
        def wxsloadthread():
            #sendSignal('playman', 'playCmd.backgroundMusic.load', ""),
            pmrs.load('/usr/twc/wxscan/products/misc','setupLayers')
            pmrs.load('/twc/products/ext/ticker', 'CityTicker')
        th.Thread(target=wxsloadthread).start()
        import wxsclock
        th.Thread(target=wxsclock.main).start()
        

    # bloc = rl.get_shader_location(lclipshader, "box")
    # rl.set_shader_value(lclipshader, bloc, rl.Vector4(20, 20, 680, 440), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)

    #rl.set_target_fps(30)
    fclock = rg.pg.Clock()
    def musicplayer():
        global lms
        import random
        while True:
            print("Music looped!")
            files = [f for f in os.listdir("bgm") if os.path.isfile(os.path.join("bgm", f)) and not f.startswith(".")]
            random.shuffle(files)
            for file in files:
                rg.pg.mixer.music.load(os.path.join("bgm", file))
                rg.pg.mixer.music.play()
                while rg.pg.mixer.music.get_busy():
                    time.sleep(0.1)

    if music_player:
        if VERBOSE:
            renderElog("Starting music player...")
        th.Thread(target=musicplayer).start()
    
    select_layer = -1
    SELECT_ENABLE = False
    if VERBOSE:
        renderElog("Starting main loop!")
    while not rl.window_should_close():
        ft = 0
        pmbl.idle()
        fclock.tick_busy_loop(29.25 if twc.personality == "WxScan" else 30)
        iiix = 0
        if sdi:
            if not vidtex and sdih.size != (0, 0):
                timg = rl.gen_image_color(*sdih.size, rl.BLACK)
                vidtex = rl.load_texture_from_image(timg)
                print("vidtex")
            
            if sdih.frame and vidtex:
                sdif = rl.ffi.new("char []", sdih.frame)
                rl.update_texture(vidtex, sdif)
        audio_chans = []
        audio_mixes = []
        audio_vols = []
        remove = []
        
        
        for i, cmdlist in enumerate(rg.queuedcommands):
            cmd, tm, fo, estimated = cmdlist
            #if time.time() > (tm+fo/30):
            if time.time() + RenderControl.rctf/30 >= tm+fo/30:
                print("runcmd", tm, fo, estimated, type(cmd).__name__)
                RenderControl.actuallyRunAQueuedCommand(cmd)
                remove.append(cmdlist)
        #RenderControl.rctf += 1
        for i in remove:
            rg.queuedcommands.remove(i)
        sortedLayers = sorted(rg.layers, key=lambda layer: layer[4])
        ee += 1
        rl.begin_drawing()
        #let's look at the text queue
        for item in rg.text_queue:
            if item.rtex is not None:
                continue
            ccol = tuple([round(c*255) for c in item._color])
            glist, clist, ctg, top_o = build_glyph_list(0, 0, item.s, ccol, item.fnt)
            
            vv = list(ctg.values())
            try:
                x_min = min([min(x, key=lambda val: val[0]) for x in vv], key=lambda val: val[0])[0]
            except:
                continue
            y_min = min([min(y, key=lambda val: val[1]) for y in vv], key=lambda val: val[1])[1]
            x_mx = max([max(x, key=lambda val: val[0]+val[2]) for x in vv], key=lambda val: val[0]+val[2])
            y_mx = max([max(y, key=lambda val: val[1]+val[3]) for y in vv], key=lambda val: val[1]+val[3])
            x_max = x_mx[0]+x_mx[2]
            y_max = y_mx[1]+y_mx[3]
            x_off = min(
                x_min,
                0
            )
            y_off = min(
                y_min,
                0
            )
            rtw = abs(x_max-x_min)
            rth = abs(y_max-y_min)
            item.rtex = rl.load_render_texture(rtw, rth)
            item.text_bounds = (rtw, rth)
            item._size = (rtw, rth)
            item.draw_off = (x_min, y_min)
            item.top_offset = top_o
            rl.begin_texture_mode(item.rtex)
            rl.rl_set_blend_mode(rl.BlendMode.BLEND_ALPHA_PREMULTIPLY)
            rl.clear_background(rl.BLANK)
            for l in glist:
                if l not in clist:
                    continue
                char : Character = clist[l]
                char.load()
                for c in ctg[l]:
                    rl.draw_texture_pro(char.texture, rl.Rectangle(0, 0, char.texture.width, -char.texture.height), rl.Rectangle(c[0]-x_min, c[1]-y_min, char.texture.width, char.texture.height), (0, 0), 0, rl.WHITE)
                #renderElog(c[0]-x_min, c[1]-y_min)
            rl.end_texture_mode()
            #im = rl.load_image_from_texture(item.rtex.texture)
            #rl.export_image(im, "imm.png")
            #renderElog(rtw, rth, x_min, y_min, x_max, y_max, item.s, ctg)
            #exit()
            
        rg.text_queue.clear()
        
        #end text queue
        rl.clear_background(rl.BLANK)
        rl.rl_set_clip_planes(0.01, 10000)
        rl.begin_mode_3d(camera)
        mode_3d_tracker += 1
        rl.rl_disable_depth_test()
        rl.rl_disable_depth_mask()
        
        audio_depths = []
        audnames = []
        
        rt = time.perf_counter
        
        ii = 0
        for l in sortedLayers:
            lastaud = 0
            if l[-1]:
                activedrawlayer = l
                
                #rl.set_shader_value(lclipshader, bloc, rl.Vector4(l[6], l[7], l[8], l[9]), rl.ShaderUniformDataType.SHADER_UNIFORM_VEC4)
                rl.set_shader_value(lclipshader, bloc, rl.ffi.new('float *', float(l[6])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
                rl.set_shader_value(lclipshader, bloc2, rl.ffi.new('float *', float(l[7])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
                rl.set_shader_value(lclipshader, bloc3, rl.ffi.new('float *', float(l[8])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
                rl.set_shader_value(lclipshader, bloc4, rl.ffi.new('float *', float(l[9])), rl.ShaderUniformDataType.SHADER_UNIFORM_FLOAT)
                if not (select_layer >= 0 and ii != select_layer and SELECT_ENABLE):
                    draw_item(l[1])
            for _ in range(len(audio_chans)-lastaud):
                audio_depths.append(l[4])
                audnames.append(l[0])
            lastaud = len(audio_chans)
            ii += 1
        
        sorted_audio = sorted(zip(audio_chans, audio_mixes, audio_vols, audio_depths, audnames), key = lambda x: x[3])
        audio_finalvols = []
        video_audio_level = 1
        if sorted_audio:
            audio_chans, audio_mixes, audio_vols, audio_depths, audnames = zip(*sorted_audio)
            
            audio_finalvols = list(audio_vols).copy()
            
            for i, mix in enumerate(audio_mixes):
                video_audio_level *= (1 - mix)
                for j in range(len(audio_finalvols)):
                    if j <= i:
                        if j == i:
                            audio_finalvols[j] *= mix
                        else:
                            audio_finalvols[j] *= (1 - mix)
            
            i = 0
            for chan, vol in zip(audio_chans, audio_finalvols):
                #chan.set_volume(vol if not MUTE else 0)
                snd = chan.get_sound()
                if snd:
                    snd.set_volume(vol if not MUTE else 0)
                i += 1
            #print(video_audio_level)
            
        if sdi:
            sdih.set_volume(video_audio_level)
            #print("set volume", vol)
        if music_player:
            if MUTE:
                rg.pg.mixer.music.set_volume(0)
            else:
                rg.pg.mixer.music.set_volume(video_audio_level)
        
        rl.end_mode_3d()
        mode_3d_tracker -= 1
        if DEBUG:
            def getnpages(layer):
                if not isinstance(layer[1], Layer):
                    return 0
                if not isinstance(layer[1].pages, list):
                    return 0
                return len(layer[1].pages)
            layer_list = "\n".join([f"Info {rl.get_render_width()} {rl.get_render_height()}"] + [f"{'### '*(iii==select_layer)}{l[0]} (depth {l[4]}) (transforms: x y {l[6]} {l[7]} w h {l[8]} {l[9]} sx sy {l[10]} {l[11]} tx ty {l[12]} {l[13]}) (Loops: {l[5]}) (Pages: {getnpages(l)}) (Active: {l[14]})" for iii, l in enumerate(sortedLayers)])
            #layer_list = "\n".join(["QC Info:"] + [f"{type(cmd).__name__} {tm} {fo} {round(time.time()+RenderControl.rctf/30-tm-fo/30)}" for cmd, tm, fo, whatevss in rg.queuedcommands])
            #itemz = sorted(list(load_stuff.items()), key=lambda x: x[1], reverse=True)
            #layer_list = "\n".join(["Loaded Items:"] + [f"{k}: {v}" for k, v in itemz])
            
            lines = windbg.split("\n")
            if len(lines) > 12:
                lines = lines[-12:]
            rl.draw_fps(10, 10)
            rl.draw_text(f"StarID: {starid} Personality {twc.personality}", 10, 40, 20, rl.WHITE)
            rl.draw_text(f"Audio Playing: {len(audio_chans)} QC {len(rg.queuedcommands)}", 10, 70, 20, rl.WHITE)
            vlist = '\n'.join([str(round(vol*100))+'%\n' for vol in audio_finalvols])
            rl.draw_text(layer_list, 10, 100, 10, rl.WHITE)
            #sorry box thing, but your service is no longer needed. you will remain here in our memory-leaking hearts
            #at least, until some OTHER freaky memory leak rears its ugly head
            #if rl.is_key_pressed(rl.KeyboardKey.KEY_F):
            #    renderElog([type(f) for f in gc.get_referrers(rg.__dict__["box_thing"])])
                # for f in gc.get_referrers(rg.__dict__["box_thing"]):
                #     if type(f) != dict:
                #         renderElog(f)
            #    import objgraph
            #    objgraph.show_backrefs(rg.__dict__["box_thing"], max_depth=3, filename="obj.png")
        for i in range(len(last_sec)):
            last_sec[i] -= 1
        
        while True:
            try:
                last_sec.remove(0)
            except:
                break
        rl.end_drawing()
        for i in rg.unloadqueue:
            unload_tree(i)
        rg.unloadqueue = []
        
        if rl.is_key_pressed(rl.KeyboardKey.KEY_D):
            DEBUG = not DEBUG
        
        if rl.is_key_pressed(rl.KeyboardKey.KEY_R):
            skip_drawing = not skip_drawing
        
        if rl.is_key_pressed(rl.KeyboardKey.KEY_M):
            MUTE = not MUTE
        
        if rl.is_key_pressed(rl.KeyboardKey.KEY_GRAVE):
            SAVECR = not SAVECR

        if rl.is_key_pressed(rl.KeyboardKey.KEY_F):
            rl.toggle_fullscreen()
        
        if DEBUG:
            if rl.is_key_pressed(rl.KeyboardKey.KEY_X):
                SELECT_ENABLE = not SELECT_ENABLE
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_W):
                select_layer = max(select_layer-1, -1)
            
            if rl.is_key_pressed(rl.KeyboardKey.KEY_S):
                select_layer = select_layer+1