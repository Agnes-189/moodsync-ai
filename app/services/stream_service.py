import urllib.request
import urllib.parse
import json

MOOD_SEARCH_QUERIES = {
    "happy": ["afrobeat hits", "amapiano dance", "feel good pop"],
    "relaxed": ["acoustic chill", "lofi beats", "sauti sol acoustic"],
    "heartbroken": ["sad rnb soul", "heartbreak ballads", "slow jams"],
    "energetic": ["amapiano mix", "dancehall party", "workout hype"],
    "stressed": ["calm ambient piano", "soothing instrumental", "peaceful gospel"],
    "romantic": ["afro love songs", "kenyan rnb love", "romantic slow jams"]
}

def fetch_online_streams(query, limit=12):
    """Fetch playable online audio streams and cover art from the iTunes API."""
    encoded = urllib.parse.quote(query)
    url = f"https://itunes.apple.com/search?term={encoded}&media=music&entity=song&limit={limit}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MoodSyncAI/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return []

    tracks = []
    for item in data.get("results", []):
        stream_url = item.get("previewUrl")
        if not stream_url:
            continue

        ms = item.get("trackTimeMillis", 0)
        mins = ms // 60000
        secs = (ms % 60000) // 1000
        artwork = item.get("artworkUrl100", "").replace("100x100bb", "500x500bb")

        tracks.append({
            "id": item.get("trackId"),
            "title": item.get("trackName", "Unknown Track"),
            "artist": item.get("artistName", "Unknown Artist"),
            "genre": item.get("primaryGenreName", "Music"),
            "duration": f"{mins}:{secs:02d}" if ms else "0:30",
            "cover_art": artwork,
            "stream_url": stream_url,
            "external_url": item.get("trackViewUrl", "#"),
            "provider": "Online Stream"
        })

    return tracks