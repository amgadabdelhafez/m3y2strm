import os
from utils import is_english_name, sanitize_filename, extract_show_info, reorder_mixed_language
from file_operations import safe_create_dir, safe_write_file

class MediaProcessor:
    def __init__(self, output_dir_grouped, output_dir_flat):
        self.output_dir_grouped = output_dir_grouped
        self.output_dir_flat = output_dir_flat
        self.processed_count = 0
        self.skipped_english_count = 0
        self.error_count = 0
        self.total_processed = 0

    def process_show(self, tvg_name, group_title, stream_url):
        """Process a TV show entry"""
        show_name, season, episode = extract_show_info(tvg_name)
        if not (show_name and season and episode):
            print(f"\nSkipping '{tvg_name}' as it doesn't match TV show format.")
            return False

        # Create grouped structure (with group-title)
        group_dir = os.path.join(self.output_dir_grouped, sanitize_filename(group_title))
        show_dir_grouped = os.path.join(group_dir, sanitize_filename(show_name))
        season_dir_grouped = os.path.join(show_dir_grouped, f"Season {season.zfill(2)}")
        
        # Create flat structure (without group-title)
        show_dir_flat = os.path.join(self.output_dir_flat, sanitize_filename(show_name))
        season_dir_flat = os.path.join(show_dir_flat, f"Season {season.zfill(2)}")
        
        # Create all necessary directories
        dirs_to_create = [
            group_dir,
            show_dir_grouped,
            season_dir_grouped,
            show_dir_flat,
            season_dir_flat
        ]
        
        for dir_path in dirs_to_create:
            if not safe_create_dir(dir_path):
                return False

        # Create the strm filename with season and episode
        strm_filename = f"S{season.zfill(2)}E{episode.zfill(2)}.strm"
        strm_file_path_grouped = os.path.join(season_dir_grouped, strm_filename)
        strm_file_path_flat = os.path.join(season_dir_flat, strm_filename)

        # Write both .strm files
        return (safe_write_file(strm_file_path_grouped, stream_url) and 
                safe_write_file(strm_file_path_flat, stream_url))

    def process_movie(self, tvg_name, group_title, stream_url):
        """Process a movie entry"""
        # Reorder mixed language parts in movie name
        movie_name = reorder_mixed_language(tvg_name)
        
        # Create grouped structure (with group-title)
        group_dir = os.path.join(self.output_dir_grouped, sanitize_filename(group_title))
        movie_dir_grouped = os.path.join(group_dir, sanitize_filename(movie_name))
        
        # Create flat structure (without group-title)
        movie_dir_flat = os.path.join(self.output_dir_flat, sanitize_filename(movie_name))
        
        # Create all necessary directories
        dirs_to_create = [
            group_dir,
            movie_dir_grouped,
            movie_dir_flat
        ]
        
        for dir_path in dirs_to_create:
            if not safe_create_dir(dir_path):
                return False

        # Create .strm files in both locations
        strm_filename = "movie.strm"
        strm_file_path_grouped = os.path.join(movie_dir_grouped, strm_filename)
        strm_file_path_flat = os.path.join(movie_dir_flat, strm_filename)

        # Write both .strm files
        return (safe_write_file(strm_file_path_grouped, stream_url) and 
                safe_write_file(strm_file_path_flat, stream_url))

    def process_entry(self, tvg_name, group_title, stream_url, is_tvshow):
        """Process a single media entry"""
        self.total_processed += 1
        
        # Skip if the name is in English
        if is_english_name(tvg_name):
            self.skipped_english_count += 1
            return False

        success = False
        if is_tvshow:
            success = self.process_show(tvg_name, group_title, stream_url)
        else:
            success = self.process_movie(tvg_name, group_title, stream_url)
        
        if success:
            self.processed_count += 1
        else:
            self.error_count += 1
            
        return success

    def get_progress_message(self, num_to_process):
        """Get the current progress message"""
        return (f"Processed {self.processed_count}/{num_to_process} "
                f"(Skipped {self.skipped_english_count} English names)...")

    def get_completion_summary(self, m3u_file):
        """Get the completion summary"""
        return [
            f"\nCompleted processing '{m3u_file}':",
            f"- Successfully created: {self.processed_count} files",
            f"- Skipped English names: {self.skipped_english_count}",
            f"- Errors encountered: {self.error_count}",
            f"- Total processed: {self.total_processed}",
            f"Grouped structure in: '{self.output_dir_grouped}'",
            f"Flat structure in: '{self.output_dir_flat}'"
        ]
