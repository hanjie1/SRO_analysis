import argparse
import numpy as np
from pyevio import EvioFile
import matplotlib.pyplot as plt
import os
import json

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

        event_data = {
                'sib_frame_number':0,
                'sib_timestamp':0,
                'rts_frame_number':0,
                'rts_sib_timestamp':0,
                'payload_id':[],
                'payload_ch':[],
                'payload_timestamp':[],
                'payload_charge':[]
                }

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

        event_data['sib_frame_number']=int(frame_number)
        event_data['sib_timestamp']=int(sib_timestamp)

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

        event_data['rts_frame_number']=int(rts_frame_number)
        event_data['rts_sib_timestamp']=int(rts_sib_timestamp)

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
            else:
                if verbose:
                   print("payload data length: ",len(payload_data))

            words = np.frombuffer(payload_data, dtype=np.dtype(f'{bank.endian}u4'))

            if verbose:
               print("payload id:  ",payload_id)
               print("     Payload Data      ")
               payload_hex = bank.get_hex_dump()
               print(payload_hex)

            for word in words:
                if (word & 0x80000000)==1:
                    print("ERROR: hit word data f{hex(word)} bit 31 is non-zero")
                    continue
                # bit 31=0, bit 30:17=4ns timestamp, 16:13=channel, 12:0=charge
                tmp_timestamp = int((word & 0x7FFE0000)>>17)
                tmp_chan = int((word & 0x1E000)>>13)
                tmp_charge = int((word & 0x1FFF))

                event_data['payload_id'].append(payload_id)
                event_data['payload_ch'].append(tmp_chan)
                event_data['payload_timestamp'].append(tmp_timestamp)
                event_data['payload_charge'].append(tmp_charge)

        return event_data

    except Exception as e:
        print(f"Error processing event {event_index}: {e}")
        return None

def process_fadc_data(filename, max_event=None, output_dir="output", verbose=False):
    print(f"Processing file: {filename}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # get the run number
    match = re.search(r'_(\d+)\.evio\.', filename)
    if match:
       run_number = match.group(1)


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

            # Store valid event data
            if event_data is not None:
               processed_events.append(event_data)

               if verbose and len(processed_events) % 100 == 0:
                  print(f"Processed {len(processed_events)} valid events so far...")

        print(f"Processed {len(processed_events)} events with FADC data")

        if len(processed_events) > 0:

           outfile = output_dir+f"/fadc_sro_data_run{run_number}.json"
           with open(outfile, 'w') as file:
                json.dump(processed_events, file)

        else:
            print("No valid FADC data found in this file.")

        return

def main():
    parser = argparse.ArgumentParser(description="Process EVIO files and extract FADC250 data")
    parser.add_argument("input_files", nargs="+", help="One or more EVIO files to process.")
    parser.add_argument("-e", "--events", type=int, default=None,
                        help="If set, stop processing after this many events.")
    parser.add_argument("-o", "--output-dir", default="output",
                        help="Directory where output files will be saved.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output.")
    args = parser.parse_args()

    # Run the processing for each file
    for file in args.input_files:
        fadc_info = process_fadc_data(
            file,
            max_event=args.events,
            output_dir=args.output_dir,
            verbose=args.verbose
        )


if __name__ == "__main__":
    main()
