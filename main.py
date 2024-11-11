import os
import re
from file_operations import count_media_entries, handle_existing_folders, safe_create_dir
from media_processor import MediaProcessor

def process_m3u_file(m3u_file_path, is_tvshows):
    """Process a single M3U file"""
    # Get base name for output directories
    list_name = os.path.splitext(os.path.basename(m3u_file_path))[0]
    current_directory = os.getcwd()
    
    # Setup output directories paths (but don't create them yet)
    output_dir_grouped = os.path.join(current_directory, list_name)
    # For flat directory, always add '-flat' suffix regardless of original name
    output_dir_flat = os.path.join(current_directory, f"{list_name}-flat")
    
    # Count media entries first to ensure file is valid
    media_count = count_media_entries(m3u_file_path)
    if media_count == 0:
        print(f"No valid media entries found in '{m3u_file_path}'.")
        return
        
    media_type = "shows" if is_tvshows else "movies"
    print(f"\n'{m3u_file_path}' contains {media_count} {media_type}.")
    
    # Handle existing folders before any directory creation
    if not handle_existing_folders(output_dir_grouped, output_dir_flat):
        print(f"\nSkipping '{m3u_file_path}' as folder handling was cancelled.")
        return
    
    # Now create the directories if needed
    if not safe_create_dir(output_dir_grouped) or not safe_create_dir(output_dir_flat):
        print(f"\nSkipping '{m3u_file_path}' due to directory creation errors.")
        return

    # Get number of entries to process
    num_to_process = get_num_to_process(media_count, media_type, m3u_file_path)
    if num_to_process is None:
        return

    # Initialize media processor
    processor = MediaProcessor(output_dir_grouped, output_dir_flat)
    
    try:
        process_entries(m3u_file_path, processor, num_to_process, is_tvshows)
        print_completion_summary(processor, m3u_file_path)
    except Exception as e:
        print(f"\nError processing file: {str(e)}")

def get_num_to_process(media_count, media_type, m3u_file):
    """Get the number of entries to process from user input"""
    while True:
        try:
            num_input = input(
                f"How many {media_type} would you like to process from '{m3u_file}'? "
                f"(Enter 'all' or a number): "
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

def main():
    """Main entry point"""
    try:
        current_directory = os.getcwd()
        m3u_files = [f for f in os.listdir(current_directory) if f.endswith(".m3u")]
        
        if not m3u_files:
            print("No .m3u files found in the current directory.")
            return
        
        for m3u_file in m3u_files:
            m3u_file_path = os.path.join(current_directory, m3u_file)
            
            # Validate file exists and is readable
            if not os.path.isfile(m3u_file_path):
                print(f"Error: File '{m3u_file}' not found or not accessible.")
                continue
                
            # Check if the file is for TV shows or movies
            is_tvshows = 'tvshows' in m3u_file.lower() or 'shows' in m3u_file.lower()
            
            process_m3u_file(m3u_file_path, is_tvshows)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
