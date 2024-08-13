# A program to generate graphs for the TAPR RM3100 3-axis magnetometer
# The program colection included here reads log files from the TAPR sensor which are in a json
# format established by Dave Witten, KD0EAG
# Author:      Bob Stricklin, N5BRG
# Date:        July 4, 2024
# License:     GPL 3.0


import pandas as pd
import json
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
import configparser
from math import cos,sin,acos,asin,tan
from math import degrees,radians
#from io import StringIO

# To Determin Sun Zenith Time and more ....
from sunrisesunsetcalculator import sunrise_sunset
from sunrisesunsetcalculator import time_until_next_sunrise_sunset
from sunrisesunsetcalculator import time_of_next_sunrise_sunset
from sunrisesunsetcalculator import rounded_hours_until_next_sunrise_sunset


def setup(ax1, ax3, title, roll_count, List_length, x_limit, t, x, y, z, rt, lt, tr_show, tl_show, raw, H, E, Z, vmag):
	"""Set up common parameters for the Axes in the example."""
	# only show the bottom spine
	#ax1.yaxis.set_major_locator(ticker.NullLocator())
	ax1.spines[['left', 'right', 'top']].set_visible(True)

	t_len = len(t)
	t_adj = np.empty([t_len], dtype = float)
	for n in range(t_len-1):
		t_adj[n] = (t[n]/86400) * (86400/roll_count) # 86400 is seconds in one day

	if int(raw) == 1:	# When plotting raw values plotabsolute value of field strength
		x = np.abs(x)
		y = np.abs(y)
		z = np.abs(z)
	if int(vmag) == 1:
		vector_mag = np.sqrt(np.power(x,2) + np.power(y,2) + np.power(z,2))
		ax1.plot(t_adj,vector_mag,'.', label="Vector Magnitude", color="orange")

	if (roll_count > 1) and (int(vmag) == 0):
		# Will normalize values to 24 hours but set plot to fit a full 24 hours of roll_length data.
		# May have missed a block of time during the day.
		# FIX t_adj[n] = (t[n]/float(8600/List_length)) * 24.0
		# Plot the XYZ values
		if int(Z) == 1:
			ax1.plot(t_adj,x,'.', label="Z (x) axis", color="red")
		if int(E) == 1:
			ax1.plot(t_adj,y,'.', label="E (y) axis", color="blue")
		if int(H) == 1:
			ax1.plot(t_adj,z,'.', label="H (z) axis", color="black")
	else: # Plot all values available, every second
		if int(Z) == 1:
			ax1.plot(t,x,'.', label="Z (x) axis", color="red")
		if int(H) == 1:
			ax1.plot(t,y,'.', label="E (y) axis", color="blue")
		if int(Z) == 1:
			ax1.plot(t,z,'.', label="H (z) axis", color="black")
	# define tick positions
	ax1.xaxis.set_major_locator(ticker.MultipleLocator((84600/roll_count)/24))
	ax1.xaxis.set_minor_locator(ticker.MultipleLocator(86400/roll_count))
	xlabel = "{} second increment(s)".format(roll_count)
	ax1.set_xlabel(xlabel)

	ax1.xaxis.set_ticks_position('bottom')
	ax1.tick_params(which='major', width=1.00, length=5)
	ax1.tick_params(which='minor', width=0.75, length=2.5, labelsize=10)
	ax1.set_xlim(xmin=0, xmax=x_limit)
	if int(raw) == 1:
		ax1.set_ylabel('Magnetic Flux (uT)')
	else:
		ax1.set_ylabel('Differential Magnetic Flux (nT)')
	ax1.legend(frameon=False, loc='lower center', ncol=3, fontsize=20)
	ax1.set_yticks([0.2, 0.6, 0.8], minor=True)
	ax1.set_yticks([0.3, 0.55, 0.7], minor=True)
	ax1.yaxis.grid(True, which='major')
	ax1.yaxis.grid(True, which='minor')

	if int(tl_show) == 1 or int(tr_show) == 1:
		if int(tr_show) == 1:
			ax3.plot(t_adj,rt,'.', label="Sensor Temp", color="green")
		if int(tl_show) == 1:
			ax3.plot(t_adj,lt,'.', label="RPi Temp", color="brown")
		ax3.set_xlim(xmin=0, xmax=x_limit)
		ax3.set_ylabel('Temperature (C)')
		ax3.legend(frameon=False, loc='lower center', ncol=3, fontsize=20)
		#ax3.set_yticks([0.2, 0.6, 0.8], minor=True)
		#ax3.set_yticks([0.3, 0.55, 0.7], minor=True)
		ax3.yaxis.grid(True, which='major')
		#ax3.yaxis.grid(True, which='minor')
		ax3.set_ylim(0,50)
		#ax3.set_yticks(new_tick_locations)
		#ax3.set_yticklabels(tick_function(new_tick_locations))
		ax3.legend(loc=0)
	else:
		ax3.yaxis.set_tick_params(labelright=False)
		ax3.set_yticks([])

	# Determin max and min values to setup Y axis extreams in plot so plot is filled.
	max_value = 0
	min_value = 200
	if int(vmag) == 1:
		max_value = np.max(abs(vector_mag))
		min_value = np.min(abs(vector_mag))
		ax1.set_ylim(min_value, max_value )
	if int(raw) == 1:
		max_x = np.max(abs(x))
		max_y = np.max(abs(y))
		max_z = np.max(abs(z))
		min_x = np.min(abs(x))
		min_y = np.min(abs(y))
		min_z = np.min(abs(z))
		if int(H) == 1:
			max_value = max_z 
			min_value = min_z 
		if int(E) == 1:
			if max_value < max_y:
				max_value = max_y
			if min_value > min_y:
				min_value = min_y
		if int(Z) == 1:
			if max_value < max_x:
				max_value = max_x
			if min_value > min_x:
				min_value = min_x
			if max_value < max_x:
				max_value = max_x
			if min_value > min_x:
				min_value = min_x
		ax1.set_ylim(min_value, max_value )
	else:
		max_value = np.max([np.max(x),np.max(y),np.max(z),-(np.min(x)),-(np.min(y)),-(np.min(z))])
		ax1.set_ylim(-(max_value), (max_value))
	if int(vmag) == 1:
		max_value = np.max(abs(vector_mag))
		min_value = np.min(abs(vector_mag))
		ax1.set_ylim(min_value, max_value )
	ax1.text(0.250, 1.1, title, transform=ax1.transAxes,
	 fontsize=14, fontname='Monospace', color='tab:blue')

def graph_magnetic_day(lat,long, logfiles, filename, plot_type, roll_count_str, tr_show, tl_show, raw, H, E, Z, vmag):
	latitude = float(lat)
	longitude = float(long)
	filename = filename.replace("'","")  #Remove quotes from filename added by combo.get()
	filename = filename.replace("]","")  #Remove ] if added by combo.get()
	#filename = filename.strip()
	roll_count = int(roll_count_str)    # combo.get() provides string value so convert
	if(roll_count == 1):
		plot_type = "single"  # If plotting every value the stats do not matter so call it single

	#Allocate storage memory for our data of interest
	vector_day = np.empty([int((86400/roll_count)+.5),6], dtype = float)
	vector_subtract = np.arange(6.0).reshape((1,6))
	new_tick_locations = np.empty([1], dtype = float)
	temp = np.empty([60,6], dtype = float)

	# Read in test file. Need to expand this to support slecting the file of interest...
	#df = pd.read_json("/home/bstricklin/n5brg-20240606-runmag.log",lines=True)
	logfiles_len = len(logfiles)
	path = logfiles
	df = pd.read_json((path + filename),lines=True)

	#df.info()

	#Convert TM from datetime to unixtime
	#Pull out the data we want
	i=0
	j = 0;
	first = 1
	for index, row in df.iterrows():
		temp[j,0] = float(row ['x'])
		temp[j,1] = float(row ['y'])
		temp[j,2] = float(row ['z'])
		temp[j,4] = float(row ['rt'])
		temp[j,5] = float(row ['lt'])
		j += 1
		if i==0 and first == 1:
			dt_utc = datetime.datetime.strptime((row ['ts']),'%d %b %Y %H:%M:%S')
			start_time = dt_utc
			start_time_str = row ['ts']
			start_epoch = int(dt_utc.timestamp())
			first = 0
		if roll_count == 1:	# Select the current reading for value
			vector_day[i,0]=temp[0,0]
			vector_day[i,1]=temp[0,1]
			vector_day[i,2]=temp[0,2]
			vector_day[i,4]=temp[0,4]
			vector_day[i,5]=temp[0,5]
			dt_utc = datetime.datetime.strptime((row ['ts']),'%d %b %Y %H:%M:%S')
			vector_day[i,3] = float(dt_utc.timestamp()) - start_epoch
			j = 0  # Starts inter loop again
			i += 1

		if (j >= ((roll_count)) or (index == (len(df)-1))) and (roll_count > 1):
			dt_utc = datetime.datetime.strptime((row ['ts']),'%d %b %Y %H:%M:%S')
			vector_day[i,3] = float(dt_utc.timestamp()) - start_epoch

			if plot_type == "last_value" and roll_count > 1:	# Select the current reading for value
				vector_day[i,0]=temp[(roll_count-1),0]
				vector_day[i,1]=temp[(roll_count-1),1]
				vector_day[i,2]=temp[(roll_count-1),2]
				vector_day[i,4]=temp[(roll_count-1),4]
				vector_day[i,5]=temp[(roll_count-1),5]

			if plot_type == "average" and roll_count > 1:	# Select the average reading 
				vector_day[i,0]= np.average(temp[:,0])
				vector_day[i,1]= np.average(temp[:,1])
				vector_day[i,2]= np.average(temp[:,2])
				vector_day[i,4]= np.average(temp[:,4])
				vector_day[i,5]= np.average(temp[:,5])

			if plot_type == "meane" and roll_count > 1:	# Select the mean reading 
				vector_day[i,0]= np.mean(temp[:,0])
				vector_day[i,1]= np.mean(temp[:,1])
				vector_day[i,2]= np.mean(temp[:,2])
				vector_day[i,4]= np.mean(temp[:,4])
				vector_day[i,5]= np.mean(temp[:,5])

			if plot_type == "std" and roll_count > 1:	# Select the standard deveation reading 
				vector_day[i,0]= np.std(temp[:,0])
				vector_day[i,1]= np.std(temp[:,1])
				vector_day[i,2]= np.std(temp[:,2])
				vector_day[i,4]= np.std(temp[:,4])
				vector_day[i,5]= np.std(temp[:,5])

			if plot_type == "max" and roll_count > 1:	# Select the maximum reading 
				vector_day[i,0]= np.max(temp[:,0])
				vector_day[i,1]= np.max(temp[:,1])
				vector_day[i,2]= np.max(temp[:,2])
				vector_day[i,4]= np.max(temp[:,4])
				vector_day[i,5]= np.max(temp[:,5])

			if plot_type == "min" and roll_count > 1:	# Select the minimum reading 
				vector_day[i,0]= np.min(temp[:,0])
				vector_day[i,1]= np.min(temp[:,1])
				vector_day[i,2]= np.min(temp[:,2])
				vector_day[i,4]= np.min(temp[:,4])
				vector_day[i,5]= np.min(temp[:,5])

			if plot_type == "rms and roll_count > 1":	# Select the root mean squared reading 
				vector_day[i,0]= np.sqrt(np.mean(temp[:,0]**2))
				vector_day[i,1]= np.sqrt(np.mean(temp[:,1]**2))
				vector_day[i,2]= np.sqrt(np.mean(temp[:,2]**2))
				vector_day[i,4]= np.sqrt(np.mean(temp[:,4]**2))
				vector_day[i,5]= np.sqrt(np.mean(temp[:,5]**2))

			if i == 150:
				print(vector_day[i,0],"average Z or  x\n")
				print(vector_day[i,1],"average E or  y\n")
				print(vector_day[i,2],"average H or  z\n")

			j = 0  # Starts inter loop again
			i += 1
	List_length = i -1 # Adjust List_length to match number of elements in data set.
	# If raw equals 1 we will not do differential otherwise we will
	if int(raw) == 0:
		# Determine mean value and time value needed to subtract from readings to move the results to zero reference
		vector_subtract[0,0] = np.mean(vector_day[:,0])
		vector_subtract[0,1] = np.mean(vector_day[:,1])
		vector_subtract[0,2] = np.mean(vector_day[:,2])
		vector_subtract[0,3] = 0
		vector_subtract[0,4] = 0
		vector_subtract[0,5] = 0
		# Subtract the mean value from all the df values to make the results differential about zero
		# This adjust all values to be about zero.
		vector_day = np.subtract(vector_day,vector_subtract) 
		vector_day[:,0] = vector_day[:,0] * 1000 #convert from uT to nT
		vector_day[:,1] = vector_day[:,1] * 1000 #convert from uT to nT
		vector_day[:,2] = vector_day[:,2] * 1000 #convert from uT to nT

	#now = datetime.datetime.now(timezone.utc)
	z_time = sunrise_sunset(latitude, longitude, datetime.datetime.now(), 0.5,-2).get("solarNoon").get("solarNoon_time")
	r_time = sunrise_sunset(latitude, longitude, datetime.datetime.now(), 0.5,-2).get("sunrise").get("sunrise_time")
	s_time = sunrise_sunset(latitude, longitude, datetime.datetime.now(), 0.5,-2).get("sunset").get("sunset_time")

	# Adjust sun zenith time to time in seconds for this day.
	zenith_time = start_time
	zenith_time = zenith_time.replace(hour=z_time.hour)
	zenith_time = zenith_time.replace(minute=z_time.minute)
	zenith_time = zenith_time.replace(second=z_time.second)
	zenith = float(zenith_time.timestamp()) - start_epoch
	zenith = (zenith/86400) * List_length     # seconds at noon of the zun zenith for this day
	# Calculate the time in seconds for midnight. Adjust to it falls before 0 seconds to end of day.
	zenith_12 = float(zenith_time.timestamp()) - start_epoch - 43200 
	zenith_12 = (zenith_12/86400) * List_length 
	if zenith_12 < 0:
		zenith_12 = zenith_12 + 86400 / (roll_count)

	# Calculate sun rise time in seconds for this day
	rise_time = start_time
	rise_time = rise_time.replace(hour=r_time.hour)
	rise_time = rise_time.replace(minute=r_time.minute)
	rise_time = rise_time.replace(second=r_time.second)
	rise = float(rise_time.timestamp()) - start_epoch
	rise = (rise/86400) * List_length     # seconds at noon of the zun rise for this day

	# Calculate sun set time in seconds for this day
	set_time = start_time
	set_time = set_time.replace(hour=s_time.hour)
	set_time = set_time.replace(minute=s_time.minute)
	set_time = set_time.replace(second=s_time.second)
	set = float(set_time.timestamp()) - start_epoch
	set = (set/86400) * List_length     # seconds at noon of the sunset for this day

	# PLOTTING
	fig = plt.figure()
	ax1 = fig.add_subplot(111)
	ax2 = ax1.twiny()
	ax3 = ax1.twinx()

	fig.set_size_inches(16, 8)   # Define the size of the plot
	i=0
	began = 0
	end = len(vector_day[:,0])    #Number of time divisins that we need to plot
	title = 'TAPR Magnatometer @ N5BRG Lat=' + str(latitude) + ' Log=' + str(longitude) + '\n ' +  'Plot Type: ' + str(plot_type) + '  ' + start_time_str  
	x_limit = List_length
	if(end > List_length):
		end  = List_length
	# This function call  sets up plot and builds the main plot image
	setup(ax1, ax3, title, roll_count, List_length, x_limit, vector_day[began:end,3],vector_day[began:end,0],vector_day[began:end,1],vector_day[began:end,2],vector_day[began:end,4],vector_day[began:end,5], tr_show, tl_show, raw, H, E, Z, vmag)
	i=0

	# Now for the top x_axis ticks and lables hours and seconds of the day
	for i in range(0,int(x_limit+roll_count),int(((x_limit+roll_count)/25)+0.5)):
		if i == 0:
			new_tick_locations[0] = 0
		else:
			new_tick_locations = np.append(new_tick_locations,[i])

	X = vector_day[began:end,0]
	def tick_function(X):
	    #V = (x/float(x_limit)) * x_limit
	    V = (X/List_length) * 24
	    return ["%2.0f" % z for z in V]
	ax2.set_xlim(ax1.get_xlim())
	ax2.set_xticks(new_tick_locations)
	ax2.set_xticklabels(tick_function(new_tick_locations))
	ax2.set_xlabel(r"UTC Hour of Day")



	plt.axvline(x=zenith, color='gray', linestyle='-', linewidth=2)
	plt.text((zenith/List_length), 0.80, 'Sun Zenith Noon', rotation=90, transform=plt.gca().transAxes)
	plt.axvline(x=zenith_12, color='gray', linestyle='-', linewidth=2)
	plt.text((zenith_12/List_length), 0.85, 'Midnight', rotation=90, transform=plt.gca().transAxes)

	plt.axvline(x=rise, color='gray', linestyle='-', linewidth=2)
	plt.text((rise/List_length), 0.85, 'Sunrise', rotation=90, transform=plt.gca().transAxes)

	plt.axvline(x=set, color='gray', linestyle='-', linewidth=2)
	plt.text((set/List_length), 0.85, 'Sunset', rotation=90, transform=plt.gca().transAxes)

	plt.grid()
	plt.savefig('mag.png')
	#Image.open('mag.png').save('mag.pdf','PDF')
	plt.show()

