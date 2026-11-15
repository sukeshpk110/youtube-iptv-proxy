import os
import subprocess
import time
from flask import Flask, redirect, Response, request

app = Flask(__name__)

CHANNELS = {
    "keralavision_news": {
        "name": "Kerala Vision News",
        "url": "https://www.youtube.com/@keralavisionnews24x7/live"
    },
    "kannurvision_news": {
        "name": "Kannur Vision News",
        "url": "https://www.youtube.com/@KannurVisionOnlinenews/live"
    },
    "amrita_news": {
        "name": "Amrita News",
        "url": "https://www.youtube.com/@AmritaNews/live"
    }
}

# Cache dictionary to store stream URLs and avoid running yt-dlp repeatedly
STREAM_CACHE = {}
CACHE_DURATION = 300  # Cache for 5 minutes

def get_live_stream_url(channel_id, youtube_url):
    current_time = time.time()
    
    # Return cached URL if it's still fresh
    if channel_id in STREAM_CACHE:
        cached = STREAM_CACHE[channel_id]
        if current_time - cached["time"] < CACHE_DURATION:
            return cached["url"]
            
    try:
        cmd = ["yt-dlp", "--print", "url", "--no-playlist", "--geo-bypass", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        if result.returncode == 0:
            urls = result.stdout.strip().splitlines()
            if urls:
                stream_url = urls[0]
                # Save to cache
                STREAM_CACHE[channel_id] = {"url": stream_url, "time": current_time}
                return stream_url
    except Exception as e:
        print(f"Error: {e}")
    return None

@app.route('/playlist.m3u')
def generate_playlist():
    host = request.host_url.rstrip('/')
    m3u_content = "#EXTM3U\n"
    for key, info in CHANNELS.items():
        m3u_content += f'#EXTINF:-1 tvg-id="{key}" tvg-name="{info["name"]}",{info["name"]}\n'
        m3u_content += f"{host}/stream/{key}\n"
    return Response(m3u_content, mimetype='audio/x-mpegurl')

@app.route('/channel/<channel_id>.m3u')
def generate_single_channel_playlist(channel_id):
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    
    info = CHANNELS[channel_id]
    host = request.host_url.rstrip('/')
    
    m3u_content = "#EXTM3U\n"
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{info["name"]}",{info["name"]}\n'
    m3u_content += f"{host}/stream/{channel_id}\n"
    
    return Response(m3u_content, mimetype='audio/x-mpegurl')

@app.route('/stream/<channel_id>')
def proxy_stream(channel_id):
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    
    stream_url = get_live_stream_url(channel_id, CHANNELS[channel_id]["url"])
    if stream_url:
        return redirect(stream_url, code=302)
    else:
        return "Stream is offline or unavailable.", 502

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
