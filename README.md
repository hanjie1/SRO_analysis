# SRO_analysis

## FADC_waveform directory
* Decode the trigger path data:
```
pyhton analyze_roc_trig_fadc250.py <data file> 
```
The default output numpy arrays are saved at "output/fadc_waveforms_{run_number}.npy" and "output/fadc_info_{run_number}.npy"
	* fadc_waveforms_{run number}.py --- numpy array: event, slot, chan, waveform sample data
	* fadc_info_{run_number}.py --- number array: event, slot_id, evt_num, time, channels, widths, integrals, peaks, overs 
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
