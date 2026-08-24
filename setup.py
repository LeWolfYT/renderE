import pygame as pg
import requests as r
import tkinter as tk
from tkinter import filedialog
import os
import sys
import json
import subprocess as sp

os.chdir(os.path.dirname(os.path.abspath(__file__)))

root = tk.Tk()
root.withdraw()
root.configure(takefocus=False)

mypath = os.path.dirname(os.path.abspath(__file__))

pg.mixer.init()
bgm = pg.mixer.Sound(os.path.join(mypath, "setup", "groove.ogg"))
bgm.set_volume(0.75)

pg.display.init()
pg.font.init()

rwin = pg.Window("RenderE Setup", (720, 480))
win = rwin.get_surface()
bg = pg.image.load(os.path.join(mypath, "setup", "bg.png"))

bgm.play(-1)

page_vars = {"alreadysetup": False}

apage = "init"
alreadysetup = False

input_mode = "mouse"

config_name_map = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "BA": "Bahamas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UN": "UN",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

def getUniquePath(name):
    p = os.path.join(mypath, name)
    if not os.path.exists(p):
        return p
    else:
        p += "."
        ix = 0
        while os.path.exists(p+str(ix)):
            ix += 1
        return p+str(ix)

def processDS(watt=False):
    dsdat = page_vars["ds1"]
    dsstat = page_vars["ds2"]
    dsdict = {}
    
    for data in [dsdat, dsstat]:

        filepos = 0
        while True:
            fs = "\x1c"
            nameix = data.find(fs, filepos)
            if nameix == -1:
                break
            name = data[filepos:nameix]
            filepos = nameix + 1
            
            valix = data.find(fs, filepos)
            if valix == -1:
                break
            
            val = data[filepos:valix]
            filepos = valix + 1
            
            expireix = data.find("\n", filepos)
            if expireix == -1:
                break
            
            expire = data[filepos:expireix]
            filepos = expireix + 1
            
            dsdict[name] = [val, expire]
    
    with open("ds.json", "w") as f:
        f.write(json.dumps(dsdict, indent=4))
    
    if watt:
        sp.call([sys.executable, "loadSCMTconfig.py", os.path.join(mypath, "domesticpy", "util", "defaultEnhancedPlaylist.py")])

def downloadDS():
    dss = page_vars['dssource']
    brand = page_vars['brand']
    watt = False
    if dss.endswith("#"):
        watt = True
        dss = dss[:-1]
    ds1l = f"https://archive.lewolfyt.cc/{dss+''}/twc/data/datastore/ds.dat"
    ds2l = f"https://archive.lewolfyt.cc/{dss+''}/twc/data/datastore/ds.stat"
    print(ds1l, ds2l)
    if watt:
        dss = "WattLive"
    success = True
    try:
        ds1 = r.get(ds1l).content
        page_vars["ds1"] = ds1.decode("windows-1252")
    except:
        success = False
    if not success:
        page_vars["dsosuccess"] = False
        return

    try:
        ds2 = r.get(ds2l).content
        page_vars["ds2"] = ds2.decode("windows-1252")
    except:
        success = False
    page_vars["dsosuccess"] = success
    with open("servers.json", "w") as f:
        f.write(json.dumps([
            brand,
            f"https://archive.lewolfyt.cc/{dss}/"
        ]))
    pp = os.path.join(mypath, "domesticpy", "conf", "playman.py")
    
    dt = r.get(f"https://archive.lewolfyt.cc/{dss}/twc/conf/playman.py")
    if dt.ok:
        with open(pp, "w") as f:
            f.write(dt.text)
    processDS(watt)

def processDSF():
    page_vars["dsfsuccess"] = True
    try:
        dsf = page_vars["dsfolder"]
        with open(os.path.join(dsf, "ds.dat"), "r", encoding="windows-1252") as f:
            page_vars["ds1"] = f.read()
        with open(os.path.join(dsf, "ds.stat"), "r", encoding="windows-1252") as f:
            page_vars["ds2"] = f.read()
    except:
        page_vars["dsfsuccess"] = False
    processDS()

def determinestate():
    global apage, alreadysetup
    if os.path.exists(os.path.join(mypath, "ds.json")):
        if not os.path.exists(os.path.join(mypath, "setup", ".config_complete")):
            apage = "setup4"
        else:
            apage = "main"
            alreadysetup = True
            page_vars["alreadysetup"] = True
    else:
        apage = "setup1"
        
    if apage == "init":
        apage = "setup1"

def createconfighiddenfile():
    f = open(".config", "x")
    f.close()

pagemap = {}

def downloadconfig(c):
    print(c)
    page_vars["cfgsuccess"] = False
    try:
        cf = r.get(f"https://archive.lewolfyt.cc/i1conf/{c}").content
        with open(os.path.join(mypath, "setup", "tempcfg.py"), "wb") as f:
            f.write(cf)
        runscmt()
        page_vars["cfgsuccess"] = True
    except:
        page_vars["cfgsuccess"] = False

def runscmt():
    c = os.path.join(mypath, "setup", "tempcfg.py")
    rc = sp.call([sys.executable, "loadSCMTconfig.py", c])
    os.remove(c)
    rc = sp.call([sys.executable, "loadSCMTconfig.py", os.path.join(mypath, "domesticpy", "util", "defaultBulletinInfo.py")])
    if rc != 0:
        raise Exception()
    else:
        try:
            f = open(os.path.join(mypath, "setup", ".config_complete"), "x")
            f.close()
        except FileExistsError:
            pass

import shutil as sh
def processCFG():
    page_vars["cfgsuccess"] = True
    try:
        dsf = page_vars["cfgfile"]
        sh.copy(dsf, os.path.join(mypath, "setup", "tempcfg.py"))
        runscmt()
    except:
        page_vars["cfgsuccess"] = False

def buildconfigmap():
    try:
        cj = r.get("https://archive.lewolfyt.cc/configs.json").json()
        keys = sorted(list(cj.keys()), key=lambda x : config_name_map[x])
        pagemap["setup4A"] = {
            "type": "textpage",
            "title": "Configuration Repository",
            "desc": None,
            "options": ["Back"]+[config_name_map[k] for k in keys],
            "actions": [{"type": "alt", "setup": "setup4", "main": "setup4_alt"}]+[{"type": "page", "destination": f"setup4A/{k}"} for k in keys]
        }
        for k in keys:
            pagemap[f"setup4A/{k}"] = {
                "type": "textpage",
                "title": f"Configuration Repository",
                "desc": f"Viewing configs for {config_name_map[k]}",
                "options": ["Back"]+[n[0] for n in sorted(cj[k], key=lambda e : e[0])],
                "actions": [{"type": "page", "destination": "setup4A"}]+[{"type": "multi", "actions": [{"type": "var", "key": "setpath", "val": f"{k}/{n[1]}"}, {"type": "page", "destination": "setup4Aset"}]} for n in sorted(cj[k], key=lambda e : e[0])]
            }
    except Exception as e:
        print(e)
        pagemap["setup4A"] = {
            "type": "textpage",
            "title": "Configuration Repository",
            "desc": "An error occurred while loading the configuration repository! Would you like to try again or go back?",
            "options": [
                "Try Again",
                "Back"
            ],
            "actions": [
                {"type": "page", "destination": "setup4Aload"},
                {"type": "page", "destination": "setup4"}
            ]
        }

def serverchange(sv):
    servers = [["PerrisLive"], ["FlatRockLive"], ["WxScanLive"], ["WattLive"]]
    brands = ["Perris", "FlatRock", "WxScan", "Watt"]
    serversel = [f"https://archive.lewolfyt.cc/{i}/" for i in servers[sv]]
    with open(os.path.join(mypath, "servers.json"), "r") as f:
        last_brand = json.loads(f.read())[0]
    with open(os.path.join(mypath, "servers.json"), "w") as f:
        f.write(json.dumps([brands[sv]]+serversel, indent=4))
    
    page_vars["newbrand"] = brands[sv]
    page_vars["newsvr"] = servers[sv][-1]
    
    page_vars["netalt"] = os.path.exists(os.path.join(mypath, "net"+brands[sv]))
    page_vars["net_dest"] = getUniquePath(os.path.join(mypath, "net"+last_brand))
    page_vars["net_swap"] = os.path.join(mypath, "net"+brands[sv])
    
    page_vars["playmanalt"] = os.path.exists(os.path.join(mypath, "domesticpy", "conf", "playman"+brands[sv]+".py"))
    page_vars["playman_dest"] = getUniquePath(os.path.join(mypath, "domesticpy", "conf", "playman"+last_brand+".py"))
    page_vars["playman_swap"] = os.path.join(mypath, "domesticpy", "conf", "playman"+brands[sv]+".py")

def move_ass():
    np = os.path.join(mypath, "net")
    if os.path.exists(np):
        sh.move(np, page_vars["net_dest"])

def swap_ass():
    np = os.path.join(mypath, "net")
    if os.path.exists(np):
        sh.move(np, page_vars["net_dest"])
        sh.move(page_vars["net_swap"], np)

def move_pm():
    pp = os.path.join(mypath, "domesticpy", "conf", "playman.py")
    if os.path.exists(pp):
        sh.move(pp, page_vars["playman_dest"])
        
        dt = r.get(page_vars["newsvr"] + "twc/domestic/conf/playman.py")
        if dt.ok:
            with open(pp, "w") as f:
                f.write(dt.text)

def swap_pm():
    pp = os.path.join(mypath, "domesticpy", "conf", "playman.py")
    if os.path.exists(pp):
        sh.move(pp, page_vars["playman_dest"])
        sh.move(page_vars["playman_swap"], pp)

serveropts = [pg.image.load(os.path.join(mypath, "setup", f"server{i+1}.png")) for i in range(4)]
serveracts = []
i = 0
for _ in range(4):
    j = i*1
    serveracts.append({"type": "multi", "actions": [{"type": "func", "func": serverchange, "args": [int(i*1)]}, {"type": "valt", "var": "netalt", "main": "netmove", "alt": "netmove_alt"}]})
    i += 1

def clearrs():
    try:
        sh.rmtree(os.path.join(mypath, "temp"))
        os.mkdir(os.path.join(mypath, "temp"))
    except:
        pass

def clearna():
    try:
        sh.rmtree(os.path.join(mypath, "net"))
        os.mkdir(os.path.join(mypath, "net"))
    except:
        pass

custom_playlists = []

def load_play():
    global custom_playlists
    try:
        with open(os.path.join(mypath, "custom_playlists.json"), "r") as f:
            custom_playlists = json.loads(f.read())
    except:
        custom_playlists = []
    #so that i don't forget, the normal playlist format is this:
    #prodName, prodInst, opt, max, min, step, pri, exclusive, cPlysts
    
    #prodName: you get it
    #prodInst: not a clue always zeero
    #opt: optimal time
    #max: max time
    #min: min time
    #step: step time interval
    #pri: priority
    #exclusive: if another product has the same value, it becomes an either/or
    #cPlysts: idk what, usually it's ["tag1", "bkgMusic1", "ldl1"]
    
    pagemap["pedit_menu"] = {
        "type": "textpage",
        "title": "Playlist Editor",
        "desc": "Choose a playlist you would like to edit, or create a new one!",
        "options": (["Back"] + [c[0] for c in custom_playlists] + ["Create New"]),
        "actions": ([{"type": "page", "destination": "main"}, []])
    }

crawls = []


def add_crawl():
    global crawls
    crawls.append((0, 9999999999, [(0, 23)], page_vars["newcrawl"]))
    #crawls.append((page_vars["newcrawlt1"], page_vars["newcrawlt2"], page_vars["newcrawlrange"], page_vars["newcrawl"]))

def modify_crawl():
    global crawls
    crawls[page_vars["mcrawl"]][3] = page_vars["newcrawl"]

def delete_crawl():
    global crawls
    crawls.pop(page_vars["mcrawl"])

def remove_mcrawl():
    page["options"][0][1] = page["options"][0][0]

def save_crawls():
    global crawls
    global crawldata
    import twc.dsmarshal as dsm
    crawldata.crawls = crawls
    dsm.set("Config.0.Ldl_LASCrawl", crawldata, 0)

def load_crawls(reload=False):
    global crawls
    global crawldata
    if not reload:
        import twc.dsmarshal as dsm
        crawldata = dsm.defaultedConfigGet("Ldl_LASCrawl", [])
        crawls = [list(c) for c in crawldata.crawls]
    pagemap["crawl"] = {
        "type": "textpage",
        "title": "RCMT Crawl Editor",
        "desc": "Choose the crawl you would like to modify",
        "options": ["Back"] + [c[3] for c in crawls] + ["Create New", "Save"],
        "actions": [{"type": "page", "destination": "rcmt"}] + [{"type": "page", "destination": f"crawl{i}"} for i in range(len(crawls))] + [{"type": "page", "destination": "newcrawl"}, {"type": "func", "func": save_crawls}]
    }
    for i, c in enumerate(crawls):
        pagemap[f"crawl{i}"] = {
            "type": "richpage",
            "title": "RCMT Crawl Editor",
            "desc": "Type in a new crawl in the textbox",
            "options": [
                [c[3], c[3]],
                "Delete",
                "Save",
                "Back"
            ],
            "optiontypes": [
                "text",
                "button",
                "button",
                "button"
            ],
            "actions":[
                "newcrawl",
                {"type": "multi", "actions": [
                    {"type": "var", "key": "mcrawl", "val": i},
                    {"type": "func", "func": delete_crawl},
                    {"type": "func", "func": reload_crawls},
                    {"type": "page", "destination": "crawl"}
                ]},
                {"type": "multi", "actions": [
                    {"type": "var", "key": "mcrawl", "val": i},
                    {"type": "func", "func": modify_crawl},
                    {"type": "func", "func": reload_crawls},
                    {"type": "page", "destination": "crawl"}
                ]},
                {"type": "multi", "actions": [
                    {"type": "func", "func": remove_mcrawl},
                    {"type": "page", "destination": "crawl"}
                ]}
            ]
        }

def reload_crawls():
    load_crawls(True)

def check_essential_data():
    with open(os.path.join(mypath, "servers.json"), "r") as f:
        data = json.load(f)
    efurl = os.path.join(data[1], "essentialFiles.txt")
    page_vars["hasEF"] = efurl if r.head(efurl).ok else False
    if bool(page_vars["hasEF"]):
        pagemap["dessential_confirm"] = {
            "type": "textpage",
            "title": "Download Essential Data",
            "desc": f"Would you like to download essential data for {data[0]}? This may fix bugs, but it may overwrite modifications you have made!",
            "options": [
                "Yes",
                "No"
            ],
            "actions": [
                {"type": "page", "destination": "dessential"},
                {"type": "page", "destination": "main"}
            ]
        }

def download_essential_data():
    efurl = page_vars["hasEF"]
    url_base = os.path.dirname(efurl)
    for file in r.get(efurl).text.strip().split("\n"):
        try:
            out_name = os.path.join(mypath, "net", file)
            out_dir = os.path.dirname(out_name)
            os.makedirs(out_dir, exist_ok=True)
            data = r.get(os.path.join(url_base, file)).content
            if data:
                with open(out_name, "wb") as f:
                    f.write(data)
        except Exception as e:
            print(f"Error downloading {file}: {e}")

pagemap = {
    "init": {
        "type": "autopage",
        "title": "Loading...",
        "desc": None,
        "actions": [
            {"type": "func", "func": determinestate}
        ]
    },
    "setup1": {
        "type": "textpage",
        "title": "Welcome to RenderE Setup!",
        "desc": "These pages will guide you through setup. Press space or return to continue, and use the up and down arrows to change options.",
        "options": [
            "Next"
        ],
        "actions": [
            {"type": "page", "destination": "setup2"}
        ]
    },
    "setup2": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Which way would you like to set up the datastore?",
        "options": [
            "Download from the internet",
            "Load from a datastore folder"
        ],
        "actions": [
            {"type": "page", "destination": "setup3A"},
            {"type": "page", "destination": "setup3B"}
        ]
    },
    "setup2_alt": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Which way would you like to set up the new datastore?",
        "options": [
            "Download from the internet",
            "Load from a datastore folder",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "setup3A_alt"},
            {"type": "page", "destination": "setup3B"},
            {"type": "page", "destination": "main"}
        ]
    },
    "setup3A": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Choose which initial i1 package to use. This can be changed later, but for the best experience you should start with the one you will be using most.",
        "options": [
            "Perris",
            "Flat Rock",
            "Weatherscan",
            "Flat Rock + WATT Patches",
            "Back"
        ],
        "actions": [
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "PerrisLive"}, {"type": "var", "key": "brand", "val": "Perris"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "FlatRockLive"}, {"type": "var", "key": "brand", "val": "FlatRock"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "WxScanLive"}, {"type": "var", "key": "brand", "val": "WxScan"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "FlatRockLive#"}, {"type": "var", "key": "brand", "val": "Watt"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "page", "destination": "setup2"}
        ]
    },
    "setup3A_alt": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Choose which initial i1 datastore to use. Perris support is currently the best! Weatherscan requires additional outside setup, along with Flat Rock.",
        "options": [
            "Perris",
            "Flat Rock",
            "Weatherscan",
            "Flat Rock + WATT Patches",
            "Back"
        ],
        "actions": [
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "PerrisLive"}, {"type": "var", "key": "brand", "val": "Perris"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "FlatRockLive"}, {"type": "var", "key": "brand", "val": "FlatRock"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "WxScanLive"}, {"type": "var", "key": "brand", "val": "WxScan"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "multi", "actions": [{"type": "var", "key": "dssource", "val": "FlatRockLive#"}, {"type": "var", "key": "brand", "val": "Watt"}, {"type": "page", "destination": "setup3Aload"}]},
            {"type": "page", "destination": "setup2_alt"}
        ]
    },
    "setup3Aload": {
        "type": "autopage",
        "title": "Datastore Setup",
        "desc": "Downloading... Setup may stop responding for a moment.",
        "actions": [
            {"type": "func", "func": downloadDS},
            {"type": "cond", "key": "dsosuccess", "true": {"type": "page", "destination": "setup4"}, "false": {"type": "alt", "setup": "setup3Afail", "main": "setup3Bfail_alt"}}
        ]
    },
    "setup3Afail": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Online datastore downloading has failed! Would you like to try again, use a folder, or quit setup?",
        "options": [
            "Try again",
            "Load from a datastore folder",
            "Quit"
        ],
        "actions": [
            {"type": "page", "destination": "setup3A"},
            {"type": "page", "destination": "setup3B"},
            {"type": "quit"}
        ]
    },
    "setup3Afail_alt": { #if we are already setup
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "Online datastore downloading has failed! Would you like to try again, use a folder, or go back to the main menu?",
        "options": [
            "Try again",
            "Load from a datastore folder",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "setup3A_alt"},
            {"type": "page", "destination": "setup3B"},
            {"type": "page", "destination": "main"}
        ]
    },
    "setup3B": {
        "type": "autopage",
        "title": "Datastore Setup",
        "desc": "Choose your folder containing ds.dat and ds.stat from the popup.",
        "actions": [
            {"type": "picker", "ptype": "folder", "var": "dsfolder"},
            {"type": "cond", "key": "dsfolder", "true": {"type": "multi", "actions": [
                {"type": "func", "func": processDSF},
                {"type": "cond", "key": "dsfsuccess", "true": {"type": "page", "destination": "setup4"}, "false": {"type": "alt", "setup": "setup3Bfail", "main": "setup3Bfail_alt"}}
            ]}, "false": {"type": "page", "destination": "setup2"}}
        ]
    },
    "setup3Bfail": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "An error occurred while processing the datastore folder! Would you like to try again, download the datastore from online, or quit setup?",
        "options": [
            "Try again",
            "Download from the internet",
            "Quit"
        ],
        "actions": [
            {"type": "page", "destination": "setup3B"},
            {"type": "page", "destination": "setup3A"},
            {"type": "quit"}
        ]
    },
    "setup3Bfail_alt": {
        "type": "textpage",
        "title": "Datastore Setup",
        "desc": "An error occurred while processing the datastore folder! Would you like to try again, download the datastore from online, or go back to the main menu?",
        "options": [
            "Try again",
            "Download from the internet",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "setup3B"},
            {"type": "page", "destination": "setup3A_alt"},
            {"type": "page", "destination": "main"}
        ]
    },
    "setup4": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "Here, you can determine the location of your i1. Would you like to browse our configuration repository, or load a configuration from a file?\nIf you skip this step, you can come back to it in the main menu.",
        "options": [
            "Browse Repository",
            "Load from file",
            "Skip",
            "Quit"
        ],
        "actions": [
            {"type": "page", "destination": "setup4Aload"},
            {"type": "page", "destination": "setup4Bwarn"},
            {"type": "page", "destination": "setup4skip"},
            {"type": "quit"}
        ]
    },
    "setup4_alt": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "Would you like to browse our configuration repository, or load a configuration from a file?",
        "options": [
            "Browse Repository",
            "Load from file",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "setup4Aload"},
            {"type": "page", "destination": "setup4Bwarn"},
            {"type": "page", "destination": "main"}
        ]
    },
    "setup4Aload": {
        "type": "autopage",
        "title": "Configuration Repository",
        "desc": "Loading...",
        "actions": [
            {"type": "func", "func": buildconfigmap},
            {"type": "page", "destination": "setup4A"}
        ]
    },
    "setup4Aset": {
        "type": "autopage",
        "title": "Configuration Repository",
        "desc": "Running configuration scripts...",
        "actions": [
            {"type": "func", "func": (lambda : downloadconfig(page_vars["setpath"]))},
            {"type": "cond", "key": "cfgsuccess", "true": {"type": "alt", "setup": "setup4S", "main": "setup4S_alt"}, "false": {"type": "page", "destination": "setup4Afail"}}
        ]
    },
    "setup4Bwarn": {
        "type": "textpage",
        "title": "Warning",
        "desc": "Custom configuration scripts can be used to execute malicious code! Are you sure that you would like to run a custom configuration script?",
        "options": [
            "Continue",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "setup4B"},
            {"type": "alt", "setup": "setup4", "main": "setup4_alt"}
        ]
    },
    "setup4Afail": {
        "type": "textpage",
        "title": "Configuration Repository",
        "desc": "An error has occurred while loading the configuration script. Would you like to try again, go back, or skip?",
        "options": [
            "Try Again",
            "Back",
            "Skip"
        ],
        "actions": [
            {"type": "page", "destination": "setup4A"},
            {"type": "alt", "setup": "setup4", "main": "setup4_alt"},
            {"type": "multi", "actions": [{"type": "var", "key": "alreadysetup", "val": True}, {"type": "page", "destination": "main"}]}
        ]
    },
    "setup4B": {
        "type": "autopage",
        "title": "Configuration Setup",
        "desc": "Choose your configuration file from the popup.",
        "actions": [
            {"type": "picker", "ptype": "file", "var": "cfgfile"},
            {"type": "cond", "key": "cfgfile", "true": {"type": "multi", "actions": [
                {"type": "func", "func": processCFG},
                {"type": "cond", "key": "cfgsuccess", "true": {"type": "alt", "setup": "setup4S", "main": "setup4S_alt"}, "false": {"type": "page", "destination": "setup4Bfail"}}
            ]}, "false": {"type": "alt", "setup": "setup4", "main": "setup4_alt"}}
        ]
    },
    "setup4Bfail": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "An error has occurred while loading the configuration script. Would you like to try again, go back, or skip?",
        "options": [
            "Try Again",
            "Back",
            "Skip"
        ],
        "actions": [
            {"type": "page", "destination": "setup4B"},
            {"type": "alt", "setup": "setup4", "main": "setup4_alt"},
            {"type": "multi", "actions": [{"type": "var", "key": "alreadysetup", "val": True}, {"type": "page", "destination": "main"}]}
        ]
    },
    "setup4S": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "Your configuration has loaded successfully. Initial setup has been completed! You can now use the other included setup tools.",
        "options": [
            "Main menu",
            "Quit"
        ],
        "actions": [
            {"type": "multi", "actions": [{"type": "var", "key": "alreadysetup", "val": True}, {"type": "page", "destination": "main"}]},
            {"type": "quit"}
        ]
    },
    "setup4skip": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "Initial setup has been completed! You can now use the other included setup tools.",
        "options": [
            "Main menu",
            "Quit"
        ],
        "actions": [
            {"type": "multi", "actions": [{"type": "var", "key": "alreadysetup", "val": True}, {"type": "page", "destination": "main"}]},
            {"type": "quit"}
        ]
    },
    "setup4S_alt": {
        "type": "textpage",
        "title": "Configuration Setup",
        "desc": "Your configuration has loaded successfully!",
        "options": [
            "Main menu"
        ],
        "actions": [
            {"type": "page", "destination": "main"}
        ]
    },
    "main": {
        "type": "textpage",
        "title": "Setup Tools",
        "desc": None,
        "options": [
            "Reset Datastore",
            "Load Configuration",
            "Change package",
            "Download Essential Data",
            "RCMT",
            #"Playlist editor",
            "Clear temporary files",
            "Quit"
        ],
        "actions": [
            {"type": "page", "destination": "setup2_alt"},
            {"type": "page", "destination": "setup4_alt"},
            {"type": "page", "destination": "dataservers"},
            {"type": "page", "destination": "checkessential"},
            {"type": "page", "destination": "rcmt"},
            #{"type": "page", "destination": "pedit_load"},
            {"type": "page", "destination": "cleartemp"},
            {"type": "quit"}
        ]
    },
    "checkessential": {
        "type": "autopage",
        "title": "Download Essential Data",
        "desc": "Loading...",
        "actions": [
            {"type": "func", "func": check_essential_data},
            {"type": "cond", "key": "hasEF", "true": {"type": "page", "destination": "dessential_confirm"}, "false": {"type": "page", "destination": "noessential"}}
        ]
    },
    "noessential": {
        "type": "textpage",
        "title": "Download Essential Data",
        "desc": "There is no essential data defined for the current data server.",
        "options": [
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "main"},
        ]
    },
    "dessential": {
        "type": "autopage",
        "title": "Download Essential Data",
        "desc": "Downloading files...",
        "actions": [
            {"type": "func", "func": download_essential_data},
            {"type": "page", "destination": "main"}
        ]
    },
    "rcmt": {
        "type": "textpage",
        "title": "RenderE Configuration/Management",
        "desc": "Tools for configuring your STAR",
        "options": [
            "Back",
            "Crawl Editor"
        ],
        "actions": [
            {"type": "page", "destination": "main"},
            {"type": "page", "destination": "crawl_load"}
        ]
    },
    "crawl_load": {
        "type": "autopage",
        "title": "RCMT Crawl Editor",
        "desc": "Loading...",
        "actions": [
            {"type": "func", "func": load_crawls},
            {"type": "page", "destination": "crawl"}
        ]
    },
    "newcrawl": {
        "type": "richpage",
        "title": "RCMT Crawl Editor",
        "desc": "Type in a new crawl in the textbox",
        "options": [
            ["Example Text", "Example Text"],
            "Add",
            "Back"
        ],
        "optiontypes": [
            "text",
            "button",
            "button"
        ],
        "actions":[
            "newcrawl",
            {"type": "multi", "actions": [
                {"type": "func", "func": add_crawl},
                {"type": "func", "func": reload_crawls},
                {"type": "page", "destination": "crawl"}
            ]},
            {"type": "page", "destination": "crawl"}
        ]
    },
    "dataservers": {
        "type": "imagepage",
        "title": "Choose Package",
        "desc": "This will affect the graphics used, products, and more.",
        "options": serveropts,
        "actions": serveracts
    },
    "netmove": {
        "type": "textpage",
        "title": "Asset Folder",
        "desc": "Changing to another package requires new assets to be downloaded in a separate folder to avoid conflicts.\nYou do not have an asset folder for this package yet. What would you like to do with your current asset folder?",
        "options": ["Move (recommended)", "Keep current"],
        "actions": [
            {"type": "multi", "actions": [{"type": "func", "func": move_ass}, {"type": "valt", "var": "playmanalt", "main": "playmanmove", "alt": "playmanmove_alt"}]},
            {"type": "multi", "actions": [{"type": "valt", "var": "playmanalt", "main": "playmanmove", "alt": "playmanmove_alt"}]}
        ]
    },
    "netmove_alt": {
        "type": "textpage",
        "title": "Asset Folder",
        "desc": "You have a previously-used asset folder for this package. What would you like to do with your current asset folder?",
        "options": ["Swap for existing (recommended)", "Store current, create new asset folder", "Keep"],
        "actions": [
            {"type": "multi", "actions": [{"type": "func", "func": swap_ass}, {"type": "valt", "var": "playmanalt", "main": "playmanmove", "alt": "playmanmove_alt"}]},
            {"type": "multi", "actions": [{"type": "func", "func": move_ass}, {"type": "valt", "var": "playmanalt", "main": "playmanmove", "alt": "playmanmove_alt"}]},
            {"type": "multi", "actions": [{"type": "valt", "var": "playmanalt", "main": "playmanmove", "alt": "playmanmove_alt"}]}
        ]
    },
    "playmanmove": {
        "type": "textpage",
        "title": "Playman Config",
        "desc": "What would you like to do with the playman config file? (This manages things like slide names and internal playlists)",
        "options": ["Move current and download new (recommended)", "Keep current"],
        "actions": [
            {"type": "multi", "actions": [{"type": "func", "func": move_pm}, {"type": "page", "destination": "main"}]},
            {"type": "multi", "actions": [{"type": "page", "destination": "main"}]}
        ]
    },
    "playmanmove_alt": {
        "type": "textpage",
        "title": "Asset Folder",
        "desc": "You already have a copy of the correct playman config for this package. What would you like to do with your current playman config?",
        "options": ["Swap (recommended)", "Store current, manually add new", "Keep current"],
        "actions": [
            {"type": "multi", "actions": [{"type": "func", "func": swap_pm}, {"type": "page", "destination": "main"}]},
            {"type": "multi", "actions": [{"type": "func", "func": move_pm}, {"type": "page", "destination": "main"}]},
            {"type": "multi", "actions": [{"type": "page", "destination": "main"}]}
        ]
    },
    "pedit_load": {
        "type": "autopage",
        "title": "Custom Playlists",
        "desc": "Loading...",
        "actions": [
            {"type": "func", "func": load_play},
            {"type": "page", "destination": "pedit_menu"}
        ]
    },
    "cleartemp": {
        "type": "textpage",
        "title": "Clear Temporary Files",
        "desc": "Choose which files you would like to clear.",
        "options": [
            "Temporary Renderscripts",
            "Network Assets",
            "Back"
        ],
        "actions": [
            {"type": "page", "destination": "cleartempRS"},
            {"type": "page", "destination": "cleartempNA"},
            {"type": "page", "destination": "main"}
        ]
    },
    "cleartempRS": {
        "type": "autopage",
        "title": "Clear Temporary Files",
        "desc": "Clearing old renderscripts...",
        "actions": [
            {"type": "func", "func": clearrs},
            {"type": "page", "destination": "main"}
        ]
    },
    "cleartempNA": {
        "type": "autopage",
        "title": "Clear Temporary Files",
        "desc": "Clearing old network assets...",
        "actions": [
            {"type": "func", "func": clearna},
            {"type": "page", "destination": "main"}
        ]
    }
}

tfn = pg.font.Font(os.path.join(mypath, "Interstate-Bold.ttf"), 40)
fn = pg.font.Font(os.path.join(mypath, "Interstate-Regular.ttf"), 30)

cool_title_effect = False

shifty = 0

buf = pg.surface.Surface((720, 480), pg.SRCALPHA)

def draw_textpage(title, options, selected, desc):
    global shifty, sel
    
    shifty = max(min(shifty, (len(options)-6)*40), 0)
    
    if input_mode == "keyboard":
        if sel > 5:
            shifty = shifty*0.9+0.1*(sel-5)*40
        else:
            shifty = shifty*0.9
    
    bl = tfn.render(title, True, (0, 0, 0))
    yl = tfn.render(title, True, (255, 255, 0))
    buf.blit(bl, (12+2*cool_title_effect, 12-shifty))
    buf.blit(yl, (10+2*cool_title_effect, 10-shifty))
    
    if cool_title_effect:
        pg.draw.line(buf, (0, 0, 0), (10, 12-shifty), (10, 53-shifty), 3)
        pg.draw.line(buf, (0, 0, 0), (12, 52-shifty), (12+bl.get_width(), 52-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (8, 10-shifty), (8, 51-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (10, 50-shifty), (10+bl.get_width(), 50-shifty), 3)
    yy = 0
    if desc:
        d1 = fn.render(desc, True, (0, 0, 0), wraplength=700)
        d2 = fn.render(desc, True, (255, 255, 255), wraplength=700)
        yy = d1.height+40
        buf.blit(d1, (12, 72-shifty))
        buf.blit(d2, (10, 70-shifty))
    
    
    mx, my = pg.mouse.get_pos()
    if input_mode == "mouse":
        for i, opt in enumerate(options):
            yyy = i*40+70+yy-shifty
            if yyy-5 < my < yyy+35:
                sel = i
    for i, opt in enumerate(options):
        optx = "> "*(i==selected)+opt
        buf.blit(fn.render(optx, True, (0, 0, 0)), (12, i*40+72+yy-shifty))
        buf.blit(fn.render(optx, True, (255, 255, 255) if not (i == selected) else (255, 255, 0)), (10, i*40+70+yy-shifty))

def draw_richpage(title, options, selected, desc, types, actions):
    global shifty, sel
    
    shifty = max(min(shifty, (len(options)-6)*40), 0)
    
    if input_mode == "keyboard":
        if sel > 5:
            shifty = shifty*0.9+0.1*(sel-5)*40
        else:
            shifty = shifty*0.9
    
    bl = tfn.render(title, True, (0, 0, 0))
    yl = tfn.render(title, True, (255, 255, 0))
    buf.blit(bl, (12+2*cool_title_effect, 12-shifty))
    buf.blit(yl, (10+2*cool_title_effect, 10-shifty))
    
    if cool_title_effect:
        pg.draw.line(buf, (0, 0, 0), (10, 12-shifty), (10, 53-shifty), 3)
        pg.draw.line(buf, (0, 0, 0), (12, 52-shifty), (12+bl.get_width(), 52-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (8, 10-shifty), (8, 51-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (10, 50-shifty), (10+bl.get_width(), 50-shifty), 3)
    yy = 0
    if desc:
        d1 = fn.render(desc, True, (0, 0, 0), wraplength=700)
        d2 = fn.render(desc, True, (255, 255, 255), wraplength=700)
        yy = d1.height+40
        buf.blit(d1, (12, 72-shifty))
        buf.blit(d2, (10, 70-shifty))
    
    
    mx, my = pg.mouse.get_pos()
    if input_mode == "mouse":
        for i, opt in enumerate(options):
            yyy = i*40+70+yy-shifty
            if yyy-5 < my < yyy+35:
                sel = i
    for i, opt in enumerate(options):
        opt_type = types[i]
        if opt_type == "button":
            optx = "> "*(i==selected)+opt
            buf.blit(fn.render(optx, True, (0, 0, 0)), (12, i*40+72+yy-shifty))
            buf.blit(fn.render(optx, True, (255, 255, 255) if not (i == selected) else (255, 255, 0)), (10, i*40+70+yy-shifty))
        elif opt_type == "text":
            opti = fn.render(opt[1], True, (0, 0, 0))
            textxx = min(720-10-opti.width, 10) if (i == selected) else 10
            buf.blit(opti, (textxx+2, i*40+72+yy-shifty))
            col = (255, 255, 255) if not (i == selected) else (255, 255, 0)
            buf.blit(fn.render(opt[1], True, col), (textxx, i*40+70+yy-shifty))
            yo = 26
            pg.draw.line(buf, (0, 0, 0), (14, i*40+72+yy-shifty+2+yo), (722-12, i*40+72+yy-shifty+2+yo), 2)
            pg.draw.line(buf, col, (12, i*40+72+yy-shifty+yo), (720-12, i*40+72+yy-shifty+yo), 2)
            
            pg.draw.line(buf, (0, 0, 0), (textxx+opti.width+2, i*40+72+yy-shifty+2), (textxx+opti.width+2, i*40+72+yy-shifty+2+yo-4), 2)
            pg.draw.line(buf, col, (textxx+opti.width, i*40+72+yy-shifty), (textxx+opti.width, i*40+72+yy-shifty+2+yo-6), 2)
            page_vars[actions[i]] = opt[1]

def draw_impage(title, options, selected, desc):
    global shifty, sel
    
    shifty = max(min(shifty, (len(options)-2)*125), 0)
    
    if input_mode == "keyboard":
        if sel > 1:
            shifty = shifty*0.9+0.1*(sel-1)*125
        else:
            shifty = shifty*0.9
    
    bl = tfn.render(title, True, (0, 0, 0))
    yl = tfn.render(title, True, (255, 255, 0))
    buf.blit(bl, (12+2*cool_title_effect, 12-shifty))
    buf.blit(yl, (10+2*cool_title_effect, 10-shifty))
    
    if cool_title_effect:
        pg.draw.line(buf, (0, 0, 0), (10, 12-shifty), (10, 53-shifty), 3)
        pg.draw.line(buf, (0, 0, 0), (12, 52-shifty), (12+bl.get_width(), 52-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (8, 10-shifty), (8, 51-shifty), 3)
        pg.draw.line(buf, (255, 255, 0), (10, 50-shifty), (10+bl.get_width(), 50-shifty), 3)
    yy = 0
    
    if desc:
        d1 = fn.render(desc, True, (0, 0, 0), wraplength=700)
        d2 = fn.render(desc, True, (255, 255, 255), wraplength=700)
        yy = d1.height+40
        buf.blit(d1, (12, 72-shifty))
        buf.blit(d2, (10, 70-shifty))
    
    mx, my = pg.mouse.get_pos()
    if input_mode == "mouse":
        for i, opt in enumerate(options):
            yyy = i*125+70+yy-shifty
            if yyy < my < yyy+125:
                sel = i
    
    for i, opt in enumerate(options):
        s = opt.copy()
        if i != selected:
            s.fill((255, 255, 255, 127), special_flags=pg.BLEND_RGBA_MULT)
        buf.blit(s, (10, i*125+70+yy-shifty))


sel = 0
running = True

def doaction(action):
    global apage, page_vars, running
    if isinstance(action, str):
        return
    if action["type"] == "page":
        apage = action["destination"]
    elif action["type"] == "multi":
        for a in action["actions"]:
            doaction(a)
    elif action["type"] == "func":
        arg = []
        if "args" in action:
            arg = action["args"]
        action["func"](*arg)
    elif action["type"] == "var":
        page_vars[action["key"]] = action["val"]
    elif action["type"] == "cond":
        if page_vars[action["key"]]:
            doaction(action["true"])
        else:
            doaction(action["false"])
    elif action["type"] == "alt":
        if page_vars["alreadysetup"]:
            apage = action["main"]
        else:
            apage = action["setup"]
    elif action["type"] == "valt":
            if page_vars[action["var"]]:
                apage = action["alt"]
            else:
                apage = action["main"]
    elif action["type"] == "quit":
        running = False
    elif action["type"] == "picker":
        if action["ptype"] == "folder":
            page_vars[action["var"]] = filedialog.askdirectory(initialdir=mypath, mustexist=True)
        elif action["ptype"] == "file":
            page_vars[action["var"]] = filedialog.askopenfilename(initialdir=mypath)
        rwin.focus()

cl = pg.time.Clock()
transitioning = False
transition_in = False
transition_time = 0
invert_transition = False

snapshot = None

while running:
    cl.tick(60)
    page = pagemap[apage]
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            input_mode = "keyboard"
            if transitioning:
                continue
            if event.key in [pg.K_UP, pg.K_DOWN]:
                if page["type"] in ["textpage", "imagepage", "richpage"]:
                    sel = (sel + (1 if event.key == pg.K_DOWN else -1)) % len(page["options"])
                    if page["type"] in ["textpage", "imagepage"]:
                        while page["options"][sel] == "":
                            sel = (sel + (1 if event.key == pg.K_DOWN else -1)) % len(page["options"])
                    else:
                        while page["options"][sel] == "" and page["optiontypes"][sel] == "button":
                            sel = (sel + (1 if event.key == pg.K_DOWN else -1)) % len(page["options"])
            elif event.key in [pg.K_SPACE, pg.K_RETURN]:
                if event.key == pg.K_SPACE and page["type"] == "richpage" and page["optiontypes"][sel] == "text":
                    page["options"][sel][1] += " "
                    continue
                if page["type"] in ["textpage", "imagepage", "richpage"]:
                    doaction(page["actions"][sel])
                    if page["actions"][sel]["type"] != "quit":
                        invert_transition = (page["options"][sel] == "Back")
                        sel = 0
                        shifty = 0
                        transitioning = True
                        transition_in = False
                        transition_time = 10
                        snapshot = buf.copy()
            elif event.key in [pg.K_BACKSPACE, pg.K_DELETE]:
                if page["type"] == "richpage" and page["optiontypes"][sel] == "text":
                    if len(page["options"][sel][1]) > 0:
                        page["options"][sel][1] = page["options"][sel][1][:-1]
            else:
                if page["type"] == "richpage" and page["optiontypes"][sel] == "text":
                    if event.unicode.isprintable():
                        page["options"][sel][1] += event.unicode
        elif event.type == pg.MOUSEBUTTONDOWN:
            input_mode = "mouse"
            if transitioning:
                continue
            if event.button == pg.BUTTON_LEFT:
                if page["type"] in ["textpage", "imagepage", "richpage"]:
                    doaction(page["actions"][sel])
                    if page["actions"][sel]["type"] != "quit":
                        invert_transition = (page["options"][sel] == "Back")
                        sel = 0
                        shifty = 0
                        transitioning = True
                        transition_in = False
                        transition_time = 10
                        snapshot = buf.copy()
        elif event.type == pg.MOUSEWHEEL:
            input_mode = "mouse"
            if transitioning:
                continue
            shifty = max(shifty+(event.y*2)*(int(event.flipped)*2-1), 0)
        elif event.type == pg.MOUSEMOTION:
            input_mode = "mouse"
    if not running:
        break
    page = pagemap[apage]
    win.fill((0, 0, 0))
    win.blit(bg, (0, 0))
    buf.fill((0, 0, 0, 0))
    if transitioning:
        transition_time -= 1
        if transition_time < 0:
            if not transition_in:
                transition_in = True
                transition_time = 9
            else:
                transitioning = False
                transition_time = 0
                transition_in = False
    if transitioning and not transition_in:
        win.blit(snapshot, ((-720+transition_time*72)*((not invert_transition)*2-1), 0))
    else:
        if page["type"] == "textpage":
            draw_textpage(page["title"], page["options"], sel, page["desc"])
        elif page["type"] == "richpage":
            draw_richpage(page["title"], page["options"], sel, page["desc"], page["optiontypes"], page["actions"])
        elif page["type"] == "imagepage":
            draw_impage(page["title"], page["options"], sel, page["desc"])
        elif page["type"] == "autopage":
            draw_textpage(page["title"], [], sel, page["desc"])
        if transitioning:
            win.blit(buf, (transition_time*72*((not invert_transition)*2-1), 0))
        else:
            win.blit(buf, (0, 0))
    #pg.display.flip()
    rwin.flip()
    if page["type"] == "autopage" and not transitioning:
        for action in page["actions"]:
            doaction(action)