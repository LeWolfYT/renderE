import requests as r
import os
import json
from pathlib import PurePath
import urllib.parse

personality = "Perris"

servers = [
    "https://archive.lewolfyt.cc/PerrisLive/",
    "https://archive.lewolfyt.cc/FlatRockLive/",
#    "https://archive.lewolfyt.cc/WxScanLive/"
]

offline = False

def newjoin(*args):
    pp = PurePath(*args).as_posix()
    jp = os.path.join(*args)
    if jp.endswith("/") or jp.endswith("\\") and not (pp.endswith("/")):
        pp = pp + "/"
    return pp.replace("\\", "/")

fj = newjoin(os.path.dirname(os.path.abspath(__file__)), "fails.json")
if os.path.exists(fj):
    with open(fj, "r") as f:
        fails = set(json.load(f))
else:
    fails = set()

try:
    with open(newjoin(os.path.dirname(os.path.abspath(__file__)), "servers.json")) as f:
        elems = json.loads(f.read())
        personality = elems[0]
        servers = elems[1:]
except:
    import traceback
    traceback.print_exc()
    pass

temp = newjoin(
    os.path.dirname(os.path.abspath(__file__)),
    "net"
)

def _socksend(sock, data):
    dlen = len(data).to_bytes(4, "big")
    sock.sendall(dlen+data)

def e(a):
    return a.replace("https:\\a","https://a").replace("https:/a", "https://a")

def requestNetAsset(path : str, extensions, check=False):
    fonts = ["ttf", "otf"]
    gfx = ["tif", "jpg", "tiff", "jpeg", "png"]
    aud = ["wav", "mp3"]
    all = fonts + gfx + aud
    emap = {"font": fonts, "gfx": gfx, "audio": aud, "all": all}
    for ex in emap[extensions]:
        out = newjoin(temp, path.strip("/"))+"."+ex
        if os.path.exists(out):
            return out
    if check:
        return
    for ex in emap[extensions]:
        out = os.path.join(temp, path.strip("/"))+"."+ex
        for server in servers:
            spath = e(urllib.parse.urljoin(server, path.strip("/")))+"."+ex
            if os.path.exists(spath):
                return spath
            print(spath)
            if offline:
                continue
            if spath in fails:
                continue
            if r.head(spath).ok:
                os.makedirs(os.path.dirname(out), exist_ok=True)
                f = open(out, "wb")
                f.write(r.get(spath, allow_redirects=True).content)
                f.close()
                return out
            else:
                fails.add(spath)
    print(f"NET ERROR: couldn't find anything for {path}")
    return None

def requestNetAssetExt(path : str, ext=None, check=False):
    if os.path.exists(path):
        return path
    if os.path.exists("net"+path):
        return "net"+path
    out = newjoin(temp, path.strip("/"))+("."+ext if ext else "")
    if os.path.exists(out):
        return out
    if check:
        return
    for server in servers:
        spath = e(urllib.parse.urljoin(server, path.strip("/")))+("."+ext if ext else "")
        if os.path.exists(spath):
            return spath
        print(spath)
        if offline:
            continue
        if spath in fails:
            continue
        if r.head(spath).ok:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            f = open(out, "wb")
            f.write(r.get(spath, allow_redirects=True).content)
            f.close()
            return out
        else:
            fails.add(spath)
    print(f"NET ERROR: couldn't find anything for {path}"+("."+ext if ext else ""))
    return None
