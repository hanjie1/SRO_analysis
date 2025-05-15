import numpy as np
import matplotlib.pyplot as plt

nevents=1500
chan=0
slot=0

waveforms = np.load('output/fadc_waveforms.npy',allow_pickle=True)
fadc_info = np.load('output/fadc_info.npy',allow_pickle=True)

#for i in fadc_info[:]['slot_id']:
#    if i!=4:
#        print(i)
for i in range(nevents):
    a_wave = waveforms[i,slot,chan]
    if a_wave[0]!=0:
       xx = range(len(a_wave))
       plt.plot(xx,a_wave, label=f"event {i}")

print(len(xx))
plt.xlabel("samples")
plt.ylabel("ADC value")
plt.title(f"Channel {chan} waveforms")
plt.legend()
plt.grid(True)
plt.show()
