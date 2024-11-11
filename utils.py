import re

def is_english_name(text):
    """
    Check if the given text is primarily in English.
    Returns False for Arabic text or text containing Arabic characters.
    """
    # Return False for empty strings
    if not text:
        return False
        
    # If text ends with مدبلج, consider it Arabic regardless
    if text.strip().endswith('مدبلج'):
        return False
        
    # Remove common non-letter characters, spaces, and numbers
    cleaned_text = re.sub(r'[0-9\s\-_\(\)\[\]\.]+', '', text)
    if not cleaned_text:
        return False
    
    # If the text contains any Arabic characters, consider it non-English
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return False
        
    # Count English letters vs non-English characters
    english_chars = sum(1 for c in cleaned_text if c.isascii() and c.isalpha())
    total_chars = len(cleaned_text)
    
    # Consider it English if more than 80% of characters are English letters
    return english_chars / total_chars > 0.8 if total_chars > 0 else False

def sanitize_filename(filename):
    """Remove invalid characters from filenames"""
    invalid = '<>:"/\\|?*'
    for char in invalid:
        filename = filename.replace(char, '')
    return filename.strip()

def extract_show_info(stream_name):
    """
    Extract show name, season, and episode info from titles like "Show Name S01 E01"
    Returns (show_name, season, episode) or (None, None, None) if no match
    """
    pattern = r"(.*?)(?:\s+S(\d+)\s+E(\d+))"
    match = re.match(pattern, stream_name)
    
    if match:
        show_name = match.group(1).strip()
        season = match.group(2)
        episode = match.group(3)
        return show_name, season, episode
    return None, None, None
