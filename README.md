# SRO_analysis

## FADC_waveform directory
* Decode the trigger path FADC data:
```
pyhton analyze_roc_trig_fadc250.py <data file> 
```
The default output numpy arrays are saved at "output/fadc_waveforms_{run_number}.npy" and "output/fadc_info_{run_number}.npy"

fadc_waveforms_{run number}.npy --- numpy array: event, slot, chan, waveform sample data

fadc_info_{run_number}.npy --- number array: event, slot_id, evt_num, time, channels, widths, integrals, peaks, overs 

* Plot FADC waveforms:
```
pyhton plot_waveform.py <numpy file>
```
It can plot the raw waveforms for a given slot, channal, event range into one figure;

It can plot the raw waveforms for a given slot, channel, event range into seperate figures;

It can plot the raw waveforms for a given slot, event range, all 16 channels into seperate figures;

* Use Jupyter Notebook to plot the waveforms
1. To make the jupyter book point to the default configuration, add this to the login shell script:
```
export JUPYTER_CONFIG_DIR="/home/hatdaq/.jupyter"
```
2. run jupter notebook from command line:
```
jupter notebook
```
3. channel_waveform.ipynb:
Load the numpy array files "fadc_waveforms.npy" and "fadc_info.npy" to plot the raw waveforms of a given channel

## FADC_SRO directory
* Decode the streaming FADC data
```
python analyze_sro_fadc250.py <data file>
```
This decodes the evio data file. The output is saved at "output/fadc_sro_data_run<run_number>.json"
```
python plot_sro_data.py
```
Load the json file and plot the charge for each channel.

## FADC_ersap directory
* The ERSAP output is a list of FADC hits within each time frame; It's saved at ersap/install/user-data/data/output/\*.data. Needs to rename it as a ".csv" file to run the python script below to get the numpy array.
```
python csv2npy.py <csv file>
```
* Make plots from the numpy file:
```
python plot_sro_hits.py <npy file>
```
