import json
import numpy as np
import matplotlib.pyplot as plt

# Read the list from the JSON file
filename = 'output/fadc_sro_data.json'
with open(filename, 'r') as file:
    loaded_data = json.load(file)

nevent=len(loaded_data)
evt_frame_number=[]
evt_timestamp=[]
slot3_data=[]
slot5_data=[]

for ii in range(16): # initialize 16 channels
    slot3_data.append({"frame":[],"timestamp":[],'time':[], 'charge': []})
    slot5_data.append({"frame":[],"timestamp":[],'time':[], 'charge': []})

for event in loaded_data:
    evt_frame_number.append(event['sib_frame_number'])
    evt_timestamp.append(event['sib_timestamp'])

    nn = len(event['payload_id'])
    if nn>0:
       for ii in range(nn):
           payload_id = event['payload_id'][ii]
           if payload_id==15:
              chan = event['payload_ch'][ii]

              slot3_data[chan]['frame'].append(event['sib_frame_number'])
              slot3_data[chan]['timestamp'].append(event['sib_timestamp'])
              slot3_data[chan]['time'].append(event['payload_timestamp'][ii])
              slot3_data[chan]['charge'].append(event['payload_charge'][ii])

           if payload_id==13:
              chan = event['payload_ch'][ii]

              slot5_data[chan]['frame'].append(event['sib_frame_number'])
              slot5_data[chan]['timestamp'].append(event['sib_timestamp'])
              slot5_data[chan]['time'].append(event['payload_timestamp'][ii])
              slot5_data[chan]['charge'].append(event['payload_charge'][ii])

plt.figure(figsize=(12, 10))
plt.plot(evt_frame_number,evt_timestamp)
plt.xlabel("frame number")
plt.ylabel("time stamp")

fig1, axs1 = plt.subplots(nrows=4, ncols=4,figsize=(12, 10))
for xx in range(4):
    for yy in range(4):
        chan = xx*4+yy
        axs1[xx,yy].hist(slot3_data[chan]['time'],bins=100)
        axs1[xx,yy].set_title(f'Chan {chan}')
fig1.suptitle("SLOT 3 Hit time")
plt.tight_layout()

fig2, axs2 = plt.subplots(nrows=4, ncols=4,figsize=(12, 10))
for xx in range(4):
    for yy in range(4):
        chan = xx*4+yy
        axs2[xx,yy].hist(slot3_data[chan]['charge'],bins=100)
        axs2[xx,yy].set_title(f'Chan {chan}')
fig2.suptitle("SLOT 3 Charge")
plt.tight_layout()

fig3, axs3 = plt.subplots(nrows=4, ncols=4,figsize=(12, 10))
for xx in range(4):
    for yy in range(4):
        chan = xx*4+yy
        axs3[xx,yy].hist(slot5_data[chan]['time'],bins=100)
        axs3[xx,yy].set_title(f'Chan {chan}')
fig3.suptitle("SLOT 5 Hit time")
plt.tight_layout()

fig4, axs4 = plt.subplots(nrows=4, ncols=4,figsize=(12, 10))
for xx in range(4):
    for yy in range(4):
        chan = xx*4+yy
        axs4[xx,yy].hist(slot5_data[chan]['charge'],bins=100)
        axs4[xx,yy].set_title(f'Chan {chan}')
fig4.suptitle("SLOT 5 Charge")
# Adjust layout to prevent overlapping titles/labels
plt.tight_layout()




plt.show()
