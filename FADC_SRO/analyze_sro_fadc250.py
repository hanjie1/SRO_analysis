import argparse
import numpy as np
from pyevio import EvioFile
import matplotlib.pyplot as plt
import os

#def decode_fadc_bank(bank, decoder, verbose=False):  # this function can't decode multi slot data
#    """
#    Decode a single FADC bank.
#
#    Args:
#        bank: Bank object to decode
#        decoder: FaDecoder instance to use
#        verbose: Enable verbose output
#
#    Returns:
#        decoder: Updated decoder with processed data
#    """
#    # Get the raw data from the bank
#    payload = bank.get_data()
#
#    # Convert payload to words
#    words = np.frombuffer(payload, dtype=np.dtype(f'{bank.endian}u4'))
#
#    # Process each word with the decoder
#    for word in words:
#        decoder.faDataDecode(int(word), verbose=verbose)
#
#    return decoder

def process_event(event, event_index, verbose=False):
    """
    Process a single event to extract FADC data.

    Args:
        event: Event object to process
        event_index: Index of this event
        verbose: Enable verbose output

    Returns:
        dict: Dictionary containing processed event data or None if no valid data
    """
    try:
        # Get the root bank for this event
        root_bank = event.get_bank()

        # Check for physics events (0xFF50 or 0xFF60)
        if root_bank.tag not in [0xFF60]:   #streaming bank
            if verbose:
                print(f"Skipping non-physics event {event_index} with tag 0x{root_bank.tag:04X}")
            return None

        # Get child banks
        children = list(root_bank.get_children())
        if verbose:
            print("children: ",children)
        if len(children) < 2:
            return None

        # Find FF31 bank (streaming info bank)
        if children[0].tag == 0xFF31:
            if verbose:
                print(f"Found FF31 bank in event {event_index}")
        else:
            return None

        sib_bank = children[0]
        sib_info = sib_bank.get_data()
        words = np.frombuffer(sib_info, dtype=np.dtype(f'{sib_bank.endian}u4'))
        if verbose:
            sib_hex = sib_bank.get_hex_dump()
            print("data words in the children[0]:")
            print(sib_hex)

        frame_number = words[1]   
        sib_timestamp1 = words[2]
        sib_timestamp2 = words[3]
        sib_timestamp = sib_timestamp1 + (sib_timestamp2<<32)
        if verbose:
            print("-----------------------")
            print("   Stream Infor Bank   ")
            print("frame number:  ", frame_number)
            print("time stamp  :  ", sib_timestamp)
            print("-----------------------")

        # roc time slice bank
        rts_bank = children[1]
        rts_children = rts_bank.get_children()

        # Get child banks
        if verbose:
            print("roc time slice bank's children: ",rts_children)
        if len(children) < 2:
            return None

        rts_sib_bank = rts_children[0]
        # Find FF30 bank (streaming info bank)
        if rts_sib_bank.tag == 0xFF30:
            if verbose:
                print(f"Found FF30 bank in event {event_index}")
        else:
            return None
        
        rts_sib_info = rts_sib_bank.get_data()
        words = np.frombuffer(rts_sib_info, dtype=np.dtype(f'{rts_sib_bank.endian}u4'))
        if verbose:
            rts_sib_hex = rts_sib_bank.get_hex_dump()
            print("data words in the roc time slice bank stream info bank:")
            print(rts_sib_hex)

        rts_frame_number = words[1]   
        rts_sib_timestamp1 = words[2]
        rts_sib_timestamp2 = words[3]
        rts_sib_timestamp = rts_sib_timestamp1 + (rts_sib_timestamp2<<32)

        if verbose:
            print("-------------------------------------------")
            print("   ROC time slice bank Stream Infor Bank   ")
            print("frame number:  ", frame_number)
            print("time stamp  :  ", sib_timestamp)
            print("-------------------------------------------")

        if rts_frame_number != frame_number:
            print("ERROR: ROC time slice bank frame number f{rts_frame_number} != Stream Info Bank frame number f{frame_number}")
            return None

        if rts_sib_timestamp != sib_timestamp:
            print("ERROR: ROC time slice bank time stamp f{rts_sib_timestamp} != Stream Info Bank time stamp f{sib_timestamp}")
            return None

        for bank in rts_children[1:]:
            payload_id = bank.tag
            payload_data = bank.get_data()
            if len(payload_data)==0:
                continue

            words = np.frombuffer(payload_data, dtype=np.dtype(f'{bank.endian}u4'))
            print(len(words))
            print(hex(words[0]))
            
            if verbose:
               print("payload id:  ",payload_id)
               print("     Payload Data      ")
               payload_hex = bank.get_hex_dump()
               print(payload_hex)

        return None

        # Process all FADC banks
#        for bank in children[1:]:
#
#            # Create a new decoder for each event block (which is one slot of data)
#            decoder = FaDecoder()
#
#            # Decode the bank
#            #decoder = decode_fadc_bank(bank, decoder, verbose) # can't decode multi slots
#
#            # Get the raw data from the bank
#            payload = bank.get_data()
#
#            # Convert payload to words
#            words = np.frombuffer(payload, dtype=np.dtype(f'{bank.endian}u4'))
#
#            # Process each word with the decoder
#            for word in words:
#                decoder.faDataDecode(int(word), verbose=verbose)
#                if decoder.block_trailer_found:
#                    # Check if we have raw data
#                    for chan in range(FADC_NCHAN):
#                        if decoder.fadc_nhit[chan] > 0:
#                            # Update event data with info from this channel
#                            event_data['info']['slot_id'] = decoder.fadc_data.slot_id_hd
#                            event_data['info']['evt_num'] = decoder.fadc_data.evt_num_1
#                            event_data['info']['time'] = decoder.fadc_trigtime
#
#                            if chan not in event_data['info']['channels']:
#                                event_data['info']['channels'].append(chan)
#
#                            event_data['info']['widths'][chan] = decoder.fadc_data.width
#                            event_data['info']['integrals'][chan] = decoder.fadc_int[chan]
#                            event_data['info']['overs'][chan] = bool(decoder.fadc_data.over)
#
#                            # Copy the raw data to our waveform array
#                            if hasattr(decoder, 'frawdata'):
#                                # Determine the number of valid samples
#                                valid_samples = 0
#                                for i, sample in enumerate(decoder.frawdata[chan]):
#                                    if sample > 0:  # Assuming 0 means no data
#                                        valid_samples = i + 1
#                                        # Update peak if this sample is larger
#                                        if sample > event_data['info']['peaks'][chan]:
#                                            event_data['info']['peaks'][chan] = sample
#
#                                # Copy data to waveform array
#                                event_data['waveforms'][chan, :valid_samples] = decoder.frawdata[chan][:valid_samples]
#                                event_data['has_data'] = True
#
#                    event_list.append(event_data)
#                    del decoder
#                    decoder = FaDecoder()  # each block (each slot) has its decoder
#
#        if event_list is not None:
#            return event_list
#        else:
#            return None
#
    except Exception as e:
        print(f"Error processing event {event_index}: {e}")
        return None

#def collect_event_data(events_data):
#    """
#    Collect data from processed events into arrays.
#
#    Args:
#        events_data: List of dictionaries containing event data
#
#    Returns:
#        tuple: (waveforms array, info structured array)
#    """
#    FADC_SLOT=[3,4]
#    FADC_NCHAN = 16
#
#    # Count valid events
#    valid_events = len(events_data)
#
#    if valid_events == 0:
#        return np.array([]), np.array([])
#
#    # Find maximum sample count
#    max_samples = 0
#    for event_data in events_data:
#        for chan in range(FADC_NCHAN):
#            # Find the last non-zero sample
#            non_zero = np.nonzero(event_data[0]['waveforms'][chan])[0]
#            if len(non_zero) > 0:
#                max_samples = max(max_samples, non_zero[-1] + 1)
#
#    # Create waveform array
#    waveforms = np.zeros((valid_events, len(FADC_SLOT), FADC_NCHAN, max_samples), dtype=np.int16)
#
#    # Create structured array for metadata
#    fadc_dtype = np.dtype([
#        ('slot_id', np.int32),
#        ('evt_num', np.int32),
#        ('time', np.int64),
#        ('channels', np.object_),  # List of active channels
#        ('widths', np.object_),    # Array of channel widths
#        ('integrals', np.object_), # Array of channel integrals
#        ('peaks', np.object_),     # Array of channel peaks
#        ('overs', np.object_)      # Array of channel over flags
#    ])
#
#    fadc_info = np.zeros(valid_events, dtype=fadc_dtype)
#
#    # Fill arrays
#    for i, event_list in enumerate(events_data):
#        for event_data in event_list:
#            # Copy metadata
#            fadc_info[i]['slot_id'] = event_data['info']['slot_id']
#            fadc_info[i]['evt_num'] = event_data['info']['evt_num']
#            fadc_info[i]['time'] = event_data['info']['time']
#            fadc_info[i]['channels'] = event_data['info']['channels']
#            fadc_info[i]['widths'] = event_data['info']['widths']
#            fadc_info[i]['integrals'] = event_data['info']['integrals']
#            fadc_info[i]['peaks'] = event_data['info']['peaks']
#            fadc_info[i]['overs'] = event_data['info']['overs']
#
#            # Copy waveform data
#            if fadc_info[i]['slot_id'] in FADC_SLOT:
#                slot_idx = FADC_SLOT.index(fadc_info[i]['slot_id'])
#                waveforms[i, slot_idx, :, :] = event_data['waveforms'][:, :max_samples]
#
#
#    return waveforms, fadc_info

def process_fadc_data(filename, max_event=None, output_dir="output", verbose=False):
    """
    Process EVIO file and extract FADC250 data into numpy arrays.

    Args:
        filename: Input EVIO file
        max_event: Maximum number of events to process (None for all)
        output_dir: Directory for output files
        verbose: Enable verbose output

    Returns:
        tuple: (waveforms array, info structured array)
    """
    print(f"Processing file: {filename}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the EVIO file
    with EvioFile(filename) as evio_file:
        total_event_count = evio_file.get_total_event_count()
        print(f"File contains {evio_file.record_count} records")
        print(f"File total_event_count = {total_event_count}")

        if max_event is None:
            max_event = total_event_count
        else:
            max_event = min(max_event, total_event_count)

        print(f"max_event is set to: {max_event}")

        # List to store processed event data
        processed_events = []

        # Iterate through events
        for global_evt_index, (record, event) in enumerate(evio_file.iter_events()):
            if global_evt_index >= max_event:
                break

            # Process this event
            event_data = process_event(event, global_evt_index, verbose)

    return None
#            # Store valid event data
#            if event_data is not None:
#                processed_events.append(event_data)
#
#                if verbose and len(processed_events) % 100 == 0:
#                    print(f"Processed {len(processed_events)} valid events so far...")
#
#        print(f"Processed {len(processed_events)} events with FADC data")
#
#        # Collect data into arrays
#        waveforms, fadc_info = collect_event_data(processed_events)
#
#        if len(processed_events) > 0:
#            print(f"Final waveform array shape: {waveforms.shape}")
#
#            # Save data to numpy files
#            np.save(os.path.join(output_dir, "fadc_waveforms.npy"), waveforms)
#            np.save(os.path.join(output_dir, "fadc_info.npy"), fadc_info)
#
#            # Generate time histogram
#            #print("\nGenerating time histogram...")
#            #generate_time_histogram(fadc_info, output_dir)
#
#            # Generate diagnostic plots if requested
#            #if verbose:
#            #    generate_diagnostic_plots(waveforms, fadc_info, output_dir)
#        else:
#            print("No valid FADC data found in this file.")
#
#        return waveforms, fadc_info

def main():
    parser = argparse.ArgumentParser(description="Process EVIO files and extract FADC250 data")
    parser.add_argument("input_files", nargs="+", help="One or more EVIO files to process.")
    parser.add_argument("-e", "--events", type=int, default=None,
                        help="If set, stop processing after this many events.")
    parser.add_argument("-o", "--output-dir", default="output",
                        help="Directory where output files will be saved.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output.")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Generate diagnostic plots.")
    parser.add_argument("-t", "--time-hist", action="store_true",
                        help="Generate only the time histogram without other plots.")
    args = parser.parse_args()

    # Run the processing for each file
    for file in args.input_files:
        fadc_info = process_fadc_data(
            file,
            max_event=args.events,
            output_dir=args.output_dir,
            verbose=args.verbose or args.plot or args.time_hist
        )

        #if waveforms.size > 0:
        #    print(f"Saved data to {args.output_dir}/fadc_waveforms.npy and {args.output_dir}/fadc_info.npy")

        #    # Print some statistics
        #    print("\nBasic Statistics:")
        #    print(f"Total events with data: {waveforms.shape[0]}")
        #    print(f"Channels per event: {waveforms.shape[1]}")
        #    print(f"Maximum samples per channel: {waveforms.shape[2]}")

        #    # Channel statistics
        #    active_channels = set()
        #    for i in range(len(fadc_info)):
        #        active_channels.update(fadc_info[i]['channels'])

        #    print(f"Active channels: {len(active_channels)}")
        #    print(f"Channels list: {sorted(list(active_channels))}")

        #    # Check if the time histogram was created successfully
        #    time_hist_path = os.path.join(args.output_dir, "event_time_histogram.png")
        #    if os.path.exists(time_hist_path):
        #        print(f"\nTime histogram saved to: {time_hist_path}")
        #else:
        #    print("No valid FADC data found.")

if __name__ == "__main__":
    main()
