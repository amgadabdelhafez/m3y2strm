import os
import re
from file_operations import count_media_entries, handle_existing_folders, safe_create_dir
from media_processor import MediaProcessor

def get_num_to_process(media_count, media_type, m3u_file):
    """Get the number of entries to process from user input"""
    while True:
        try:
            num_input = input(
                f"How many {media_type} would you like to process from '{m3u_file}'? "
                f"(Enter 'all' or a number 1-{media_count}): "
            ).strip().lower()
            
            if num_input == 'all':
                return media_count
            elif num_input.isdigit() and 0 < int(num_input) <= media_count:
                return int(num_input)
            else:
                print(f"Please enter 'all' or a number between 1 and {media_count}")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except Exception as e:
            print(f"Invalid input. Please try again: {str(e)}")

def process_entries(m3u_file_path, processor, num_to_process, is_tvshows):
    """Process entries from the M3U file"""
    stream_name = group_title = tvg_name = None
    
    with open(m3u_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
                group_title_match = re.search(r'group-title="([^"]+)"', line)
                
                if tvg_name_match:
                    tvg_name = tvg_name_match.group(1)
                if group_title_match:
                    group_title = group_title_match.group(1)

            elif line.startswith("http") and tvg_name and group_title:
                processor.process_entry(tvg_name, group_title, line, is_tvshows)
                print(processor.get_progress_message(num_to_process), end='\r')
                
                if processor.processed_count >= num_to_process:
                    break
                    
                stream_name = group_title = tvg_name = None

def print_completion_summary(processor, m3u_file):
    """Print the completion summary"""
    for line in processor.get_completion_summary(m3u_file):
        print(line)

def get_processing_info(m3u_files):
    """Get processing information for all files upfront"""
    processing_info = {}
    
    print("\nChecking M3U files...")
    for m3u_file in m3u_files:
        m3u_file_path = os.path.join(os.getcwd(), m3u_file)
        
        # Validate file exists and is readable
        if not os.path.isfile(m3u_file_path):
            print(f"Error: File '{m3u_file}' not found or not accessible.")
            continue
            
        # Check if the file is for TV shows or movies
        is_tvshows = 'tvshows' in m3u_file.lower() or 'shows' in m3u_file.lower()
        media_type = "shows" if is_tvshows else "movies"
        
        # Count media entries
        media_count = count_media_entries(m3u_file_path)
        if media_count == 0:
            print(f"No valid media entries found in '{m3u_file}'.")
            continue
            
        print(f"\n'{m3u_file}' contains {media_count} {media_type}.")
        
        # Get number of entries to process
        num_to_process = get_num_to_process(media_count, media_type, m3u_file)
        if num_to_process is None:
            return None
            
        # Setup output directories paths
        output_dir_grouped = os.path.join(os.getcwd(), os.path.splitext(m3u_file)[0])
        output_dir_flat = os.path.join(os.getcwd(), f"{os.path.splitext(m3u_file)[0]}-flat")
        
        # Store processing info
        processing_info[m3u_file] = {
            'path': m3u_file_path,
            'is_tvshows': is_tvshows,
            'num_to_process': num_to_process,
            'output_dir_grouped': output_dir_grouped,
            'output_dir_flat': output_dir_flat
        }
    
    return processing_info

def process_m3u_file(m3u_file, info):
    """Process a single M3U file"""
    # Handle existing folders before any directory creation
    if not handle_existing_folders(info['output_dir_grouped'], info['output_dir_flat']):
        print(f"\nSkipping '{m3u_file}' as folder handling was cancelled.")
        return
    
    # Now create the directories if needed
    if not safe_create_dir(info['output_dir_grouped']) or not safe_create_dir(info['output_dir_flat']):
        print(f"\nSkipping '{m3u_file}' due to directory creation errors.")
        return

    # Initialize media processor
    processor = MediaProcessor(info['output_dir_grouped'], info['output_dir_flat'])
    
    try:
        process_entries(info['path'], processor, info['num_to_process'], info['is_tvshows'])
        print_completion_summary(processor, m3u_file)
    except Exception as e:
        print(f"\nError processing file: {str(e)}")

def main():
    """Main entry point"""
    try:
        current_directory = os.getcwd()
        m3u_files = [f for f in os.listdir(current_directory) if f.endswith(".m3u")]
        
        if not m3u_files:
            print("No .m3u files found in the current directory.")
            return
            
        # Get processing information for all files upfront
        processing_info = get_processing_info(m3u_files)
        if not processing_info:
            return
            
        print("\nStarting processing...")
        for m3u_file, info in processing_info.items():
            process_m3u_file(m3u_file, info)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
