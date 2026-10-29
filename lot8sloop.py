import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import subprocess
import argparse
import sys
import time
import threading as th

root = tk.Tk()
running = False
encodEing = False
reallot8stype = "D" # Fallback in case something decides to break
stop_event = th.Event()
stop_encodE_event = th.Event()

# Set the window properties
root.title("Lot8s Looper")

# Manual debugging toggle
DEBUG = False
#DEBUG = True

if DEBUG == True:
    print("Debugging mode enabled.")

parser = argparse.ArgumentParser(description="Loops LFs and encodes data.")
parser.add_argument("item", nargs="?", default="", help="The item to encode data for. Leave blank to encode all data except tag data.")
parser.add_argument("-ns", "--nosensor", action="store_true", help="Excludes sensor data for CC.")
parser.add_argument("-wxs", "--weatherscan", action="store_true", help="Enables Weatherscan data mode.")
parser.add_argument("-nt", "--notraffic", action="store_true", help="Disables traffic data.")
parser.add_argument("-nb", "--nobulletins", action="store_true", help="Only encode non-bulletin things.")
parser.add_argument("-a", "--automatic", action="store_true", help="Encodes new data every 20 minutes.")
parser.add_argument("-c", "--calm", action="store_true", help="Runs data encoding sequentially instead of all at once.")

args = parser.parse_args()

preroll = tk.IntVar(root, 8)

# Lot8s run function
def run():
    while running:
        # Here is where the run the actual lot8s commands, FINALLY!!!!!!!!!
        if DEBUG == True:
            print("Running presentation with flavor: {}".format(reallot8stype))
        subprocess.run([sys.executable, "load.py", "local", reallot8stype])
        time.sleep(preroll.get())
        subprocess.run([sys.executable, "run.py", "local"])
        if reallot8stype in ["D", "E", "S"]:
            if stop_event.wait(60):
                break
        if reallot8stype in ["K", "O"]:
            if stop_event.wait(90):
                break
        if reallot8stype in ["N", "L", "M"]:
            if stop_event.wait(90):
                break

def encodE():
    while encodEing:
        if DEBUG == True:
            print("Running encodE with arguments: {}".format(args))
        subprocess.run([sys.executable, "encodE.py", *sys.argv[1:]])
        if stop_encodE_event.wait(600):
            break

# Command for start button
def startbuttoncommand():
    if DEBUG == True:
        print("Flavor: {}".format(value_inside.get()[0]))
        print("Preroll time: {}".format(preroll.get()))
    global reallot8stype
    global running
    reallot8stype = value_inside.get()[0]
    if value_inside.get() == "Select an Option":
        messagebox.showwarning("Please select an option!", "Please select an option for what presentation to run! Defaulting to D.")
        reallot8stype = "D"
    if value_inside.get()[0] not in ["D", "E", "K", "O", "N", "L", "M", "S"]:
        print("Lot8s selector broken. Real value is: {}".format(value_inside.get()[0]))
        messagebox.showerror("Unknown presentation type", "Welp, it seems something has broken with the presentation type selector!")
    if preroll.get() <= int("-1"):
        messagebox.showerror("Preroll time is less than 0!", "Please set the preroll time to 0 or something higher!")
    else:
        if running == False:
            running = True
            run_th = th.Thread(target=run)
            run_th.start()
            stop_event.clear()
        else:
            messagebox.showerror("Already running presentation!", "The presentation is already running, go check renderE!")

# Command for stop button
def stopbuttoncommand():
    global running
    if running == True:
        running = False
        stop_event.set()
    else:
        messagebox.showerror("Presentation isn't running!", "Not running a presentation, start it first!")

def startencodEcommand():
    global encodEing
    if encodEing == False:
        encodEing = True
        encodE_th = th.Thread(target=encodE)
        encodE_th.start()
        stop_event.clear()
    else:
        messagebox.showerror("Already running encodE!", "Already encodEing!")

def stopencodEcommand():
    global encodEing
    if encodEing == True:
        encodEing = False
        stop_encodE_event.set()
    else:
        messagebox.showerror("encodE isnt running!", "Not encodEing, start it first!")

# All lot8s flavors
lot8s_options = ["Select an Option", "D - 60 seconds", "E - 60 seconds", "K - 90 seconds", "O - 90 seconds", "N - 120 seconds", "L - 120 seconds", "M - 120 seconds", "S - Squeezeback", "Z - LOT8S LDL (WATT ONLY)"]

# Set blank option string
value_inside = tk.StringVar(root)
value_inside.set("Select an Option")

# you are cordially invited to have a giant slice of my style
style = ttk.Style(root)

style.configure("my.TLabel", font=("Helvetica", 20, "bold"))

# Create a title (this is already annoying)
ttk.Label(root, text="Lot8s Looper", style="my.TLabel").pack(pady=(15, 0), padx=10)
ttk.Label(root, text="by AlexBartles").pack(pady=(0, 10))

# Ask to choose a flavor
lot8stype = ttk.Label(root, text="Choose a flavor below")
lot8stype.pack(pady=5)

# Further questioning continues
question_menu = ttk.OptionMenu(root, value_inside, *lot8s_options)
question_menu.pack(pady=5)

# Preroll time
lot8stype = ttk.Label(root, text="Preroll time (seconds)")
lot8stype.pack(pady=5)

preroll_box = ttk.Spinbox(root, from_=1, to=10, textvariable=preroll)
preroll_box.set(8)
preroll_box.pack(pady=5, padx=10)

# Create start button
startbutton = ttk.Button(root, text="Start presentation", style="my.TButton", command=startbuttoncommand)
startbutton.pack(pady=5)

# Create stop button
stopbutton = ttk.Button(root, text="Stop presentation", style="my.TButton", command=stopbuttoncommand)
stopbutton.pack(pady=5)

# Create start encodE button
startencodEbutton = ttk.Button(root, text="Start encodEing", style="my.TButton", command=startencodEcommand)
startencodEbutton.pack(pady=5)

# Create stop encodE button
stopencodEbutton = ttk.Button(root, text="Stop encodEing", style="my.TButton", command=stopencodEcommand)
stopencodEbutton.pack(pady=(5, 15))

root.mainloop()
