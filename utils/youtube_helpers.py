import re

def extract_youtube_id(url_str):
    """
    Safely extracts an 11-character YouTube video ID from various YouTube URL formats.
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&feature=shared
    - Bare 11-char VIDEO_ID
    Returns None if the URL is invalid or no valid ID is found.
    """
    if not url_str or not isinstance(url_str, str):
        return None

    url = url_str.strip()
    if not url:
        return None

    # Check if raw 11-character video ID is passed
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    if match:
        return match.group(1)

    return None

def get_youtube_embed_url(url_str):
    """
    Converts any valid YouTube URL or video ID into a standardized YouTube embed URL.
    Returns None if URL is invalid.
    """
    video_id = extract_youtube_id(url_str)
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return None
