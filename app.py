import os
import subprocess
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

def get_live_stream_url(youtube_url):
    try:
        cmd = ["yt-dlp", "--print", "url", "--no-playlist", "--geo-bypass", youtube_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            urls = result.stdout.strip().splitlines()
            if urls:
                return urls[0]
    except Exception as e:
        print(f"Error: {e}")
    return None

# 1. Master Playlist (All channels)
@app.route('/playlist.m3u')
def generate_playlist():
    host = request.host_url.rstrip('/')
    m3u_content = "#EXTM3U\n"
    for key, info in CHANNELS.items():
        m3u_content += f'#EXTINF:-1 tvg-id="{key}" tvg-name="{info["name"]}",{info["name"]}\n'
        m3u_content += f"{host}/stream/{key}\n"
    return Response(m3u_content, mimetype='audio/x-mpegurl')

# 2. Individual Channel M3U Link (Single channel playlist)
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

# 3. Direct Stream Proxy (Redirects to fresh YouTube link)
@app.route('/stream/<channel_id>')
def proxy_stream(channel_id):
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    
    stream_url = get_live_stream_url(CHANNELS[channel_id]["url"])
    if stream_url:
        return redirect(stream_url, code=302)
    else:
        return "Stream is offline or unavailable.", 502

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
