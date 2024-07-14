# A program to generate graphs for the TAPR RM3100 3-axis magnetometer
# The program colection included here reads log files from the TAPR sensor which are in a json
# format established by Dave Witten, KD0EAG
# Author:      Bob Stricklin, N5BRG
# Date:        July 4, 2024
# License:     GPL 3.0


import os
from tkinter import messagebox, ttk
import tkinter as tk
from tkinter import font as tkFont 
import numpy as np
import configparser


parser = configparser.ConfigParser(allow_no_value=True)
parser.read('./configure_mag_graph')

latitude  = parser['location']['lattitude']
longitude  = parser['location']['longitude']
#latitude = 33.4679
#longitude = -97.081
logfiles = parser['directories']['logfiles']
chop = 60
filelist = np.empty([1], dtype = str)
#filename = ""
#plot_type = ""
from graph_mag_log import graph_magnetic_day
v = np.empty([60], dtype = int)

#Read in file log
# Get the list of all files and directories
path = logfiles
dir_list = os.listdir(path)
for names in dir_list:
    if names.endswith(".log"):
        filelist = np.append(filelist,names)
    filelist.sort()
    sorted(filelist)


def display_selection():
    # Get the selected value.
    selection = combo_1.get()
    filename = combo_1.get()
    plot_type = combo_2.get()
    messagebox.showinfo(
        message=f"The selected value is: {selection}",
        title="Selection"
    )

def plot_graph():
	tr_show = ''
	tl_show = ''
	filename = combo_1.get()
	plot_type = combo_2.get()
	chop = combo_3.get()
	if (var1.get() == 1):
		tl_show=1
	elif (var1.get() == 0):
		tl_show=0
	if (var2.get() == 1):
		tr_show=1
	elif (var2.get() == 0):
		tr_show=0
	graph_magnetic_day(latitude,longitude, logfiles, filename, plot_type, chop, tr_show, tl_show)

# Setup the window
main_window = tk.Tk()
#main_window.config(width=600, height=400)
main_window.geometry("600x400")
main_window.title("Magnetic Plot Parameters               Rev 1.0  7/24")
main_window.pack_propagate(False)


### Window boxes

# label 
ttk.Label(main_window, text = "Select log file:", 
	font = ("Times New Roman", 18)).grid(column = 0, 
	row = 20, padx = 10, pady = 25) 

ttk.Label(main_window, text = "Select plot type:",
        font = ("Times New Roman", 18)).grid(column = 0,
        row = 25, padx = 10, pady = 25)

ttk.Label(main_window, text = "Group by Seconds:",
        font = ("Times New Roman", 18)).grid(column = 0,
        row = 30, padx = 10, pady = 25)

combo_1 = ttk.Combobox(
    state="readonly",
    width = 30,
    values=filelist
)
combo_1.place(x=190, y=30)

combo_2 = ttk.Combobox(
    state="readonly",
    width = 20,
    values=["last_value", "average", "mean", "rms", "std", "maximum","minimum"]
)
combo_2.place(x=190, y=110)

combo_3 = ttk.Combobox(
	state="readonly",
	width = 3,
	values = [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60]
)
combo_3.place(x=210, y=190)

### Buttons and check boxes

button = ttk.Button(text="Plot Graph", command=plot_graph)
button.place(x=100, y=300)

# Button for closing 
button = ttk.Button(text="Quit", command=main_window.destroy)
button.place(x=400, y=350)

#Check boxes
var1 = tk.IntVar()
var2 = tk.IntVar()
c1 = tk.Checkbutton(main_window, text='Show Local Temp',variable=var1, onvalue=1, offvalue=0)
c1.place(x=400,y=125)
#c1.pack()
c2 = tk.Checkbutton(main_window, text='Show Remote Temp',variable=var2, onvalue=1, offvalue=0)
c2.place(x=400,y=175)
#c2.pack()


main_window.mainloop()
main_window.mainloop()
