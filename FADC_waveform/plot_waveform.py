import sys
import numpy as np
import matplotlib.pyplot as plt

#nevents=1500
#chan=0
#slot=0
#
#waveforms = np.load('output/fadc_waveforms.npy',allow_pickle=True)
#fadc_info = np.load('output/fadc_info.npy',allow_pickle=True)
#
##for i in fadc_info[:]['slot_id']:
##    if i!=4:
##        print(i)
#for i in range(nevents):
#    a_wave = waveforms[i,slot,chan]
#    if a_wave[0]!=0:
#       xx = range(len(a_wave))
#       plt.plot(xx,a_wave, label=f"event {i}")
#
#print(len(xx))
#plt.xlabel("samples")
#plt.ylabel("ADC value")
#plt.title(f"Channel {chan} waveforms")
#plt.legend()
#plt.grid(True)
#plt.show()

class fadc_waveform:
    def __init__(self, waveforms_file, info_file=None):
        """
        Initialize the waveform class.

        Parameters:
        -----------
        waveforms_file : str
            Path to the waveform numpy file (4D array: event, slot, channel, sample)
        info_file : str, optional
            Path to the metadata numpy file (structured array: event, slot)
        """
        self.waveforms = np.load(waveforms_file, allow_pickle=True)
        self.info = None
        if info_file is not None:
            self.info = np.load(info_file, allow_pickle=True)

        self.nevents, self.nslots, self.nchannels, self.nsamples = self.waveforms.shape

    def plot_channel(self, event_start, event_end, slot, channel):
        """
        Plot raw waveforms for a given event range, slot, and channel.

        Parameters:
        -----------
        event_start : int
            Starting event index (inclusive)
        event_end : int
            Ending event index (exclusive)
        slot : int
            Slot index
        channel : int
            Channel index
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        for i in range(event_start, min(event_end, self.nevents)):
            a_wave = self.waveforms[i, slot, channel]
            if np.any(a_wave):
                ax.plot(a_wave, label=f"event {i}")
    
        ax.set_xlabel("Samples")
        ax.set_ylabel("ADC value")
        ax.set_title(f"Slot {slot}, Channel {channel}, Events {event_start}–{event_end}")
        ax.legend(fontsize="x-small", ncol=3)
        ax.grid(True)
        
        return fig

    def plot_channel_events_grid(self, event_start, event_end, slot, channel):

        """
        Plot raw waveforms of a given slot & channel for a range of events.
        Each event gets its own subplot, arranged in one canvas.
        Skips events with empty waveforms (a_wave[0] == 0).
        """
        # collect only valid events
        events = []
        for evt in range(event_start, min(event_end, self.nevents)):
            a_wave = self.waveforms[evt, slot, channel]
            if len(a_wave) > 0 and a_wave[0] != 0:
                events.append(evt)

        n_events = len(events)
        if n_events == 0:
            print("No valid events found in the specified range.")
            return None

        # make a grid close to square
        ncols = int(np.ceil(np.sqrt(n_events)))
        nrows = int(np.ceil(n_events / ncols))

        fig, axes = plt.subplots(nrows, ncols, figsize=(3*ncols, 2.5*nrows), sharex=True, sharey=True)
        axes = np.atleast_1d(axes).flatten()

        for idx, evt in enumerate(events):
            a_wave = self.waveforms[evt, slot, channel]
            ax = axes[idx]
            ax.plot(a_wave, color="b")
            ax.set_title(f"Evt {evt}", fontsize=8)
            ax.grid(True)

        # hide unused axes if grid is bigger than events
        for j in range(len(events), len(axes)):
            axes[j].axis("off")

        fig.suptitle(f"Slot {slot}, Channel {channel}, Events {event_start}–{event_end}", fontsize=14)
        fig.text(0.5, 0.04, "Samples", ha="center")
        fig.text(0.04, 0.5, "ADC value", va="center", rotation="vertical")

        return fig

    def plot_slot(self, event_start, event_end, slot):
        """
        Plot raw waveforms for all 16 channels in a given slot across an event range.

        Parameters:
        -----------
        event_start : int
            Starting event index (inclusive)
        event_end : int
            Ending event index (exclusive)
        slot : int
            Slot index
        """
        #fig, axes = plt.subplots(4, 4, figsize=(16, 10), sharex=True, sharey=True)
        fig, axes = plt.subplots(4, 4, figsize=(16, 10), sharex=True)
        axes = axes.flatten()

        for chan in range(self.nchannels):
            ax = axes[chan]
            for i in range(event_start, min(event_end, self.nevents)):
                a_wave = self.waveforms[i, slot, chan]
                if np.any(a_wave):
                    ax.plot(a_wave, alpha=0.7)
            ax.set_title(f"Ch {chan}", fontsize=8)
            ax.grid(True)

        fig.suptitle(f"Slot {slot}, Events {event_start}–{event_end}", fontsize=14)
        fig.text(0.5, 0.04, "Samples", ha="center")
        fig.text(0.04, 0.5, "ADC value", va="center", rotation="vertical")

        return fig


if __name__ == "__main__":

   if len(sys.argv) < 2:
        print("Usage: python plot_waveform.py <filename.npy>")
        sys.exit(1)

   fw = fadc_waveform(sys.argv[1])
   
   # Plot one channel across events
   fig1 = fw.plot_channel(event_start=0, event_end=50, slot=1, channel=15)
   fig2 = fw.plot_channel_events_grid(event_start=0, event_end=50, slot=1, channel=15)

   
   # Plot all 16 channels for a slot across events
   fig3 = fw.plot_slot(event_start=0, event_end=50, slot=1)

   plt.show() 
