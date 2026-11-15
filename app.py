import os
import subprocess
import time
from flask import Flask, Response, redirect, request

app = Flask(__name__)

STREAM_CACHE = {}
CACHE_DURATION = 300  # 5-minute in-memory stream URL cache

CHANNELS = {
    "keralavision_news": {
        "name": "Kerala Vision News",
        "url": "https://www.youtube.com/@keralavisionnews24x7/live"
    },
    "kannurvision_news": {
        "name": "Kannur Vision News",
        "url": "https://www.youtube.com/@zealtvkannur/live"
    },
    "amrita_news": {
        "name": "Amrita News",
        "url": "https://www.youtube.com/@AmritaTV/live"
    }
}

def get_live_stream_url(channel_id, youtube_url):
    current_time = time.time()
    if channel_id in STREAM_CACHE:
        cached = STREAM_CACHE[channel_id]
        if current_time - cached["time"] < CACHE_DURATION:
            return cached["url"], None

    try:
        cmd = [
            "yt-dlp",
            "--extractor-args", "youtube:player_client=android",
            "-f", "best",
            "--print", "url",
            "--no-playlist",
            youtube_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            urls = result.stdout.strip().splitlines()
            if urls:
                stream_url = urls[0]
                STREAM_CACHE[channel_id] = {"url": stream_url, "time": current_time}
                return stream_url, None
        return None, result.stderr
    except Exception as e:
        return None, str(e)

@app.route('/health')
def health_check():
    return "OK", 200

@app.route('/playlist.m3u')
def master_playlist():
    host = request.host_url.rstrip('/')
    m3u_content = "#EXTM3U\n"
    for channel_id, info in CHANNELS.items():
        m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{info["name"]}",{info["name"]}\n'
        m3u_content += f'{host}/stream/{channel_id}\n'
    return Response(m3u_content, mimetype='audio/x-mpegurl')

@app.route('/channel/<channel_id>.m3u')
def channel_playlist(channel_id):
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    host = request.host_url.rstrip('/')
    info = CHANNELS[channel_id]
    m3u_content = "#EXTM3U\n"
    m3u_content += f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{info["name"]}",{info["name"]}\n'
    m3u_content += f'{host}/stream/{channel_id}\n'
    return Response(m3u_content, mimetype='audio/x-mpegurl')

@app.route('/stream/<channel_id>')
def proxy_stream(channel_id):
    if channel_id not in CHANNELS:
        return "Channel not found", 404
    
    stream_url, error_log = get_live_stream_url(channel_id, CHANNELS[channel_id]["url"])
    if stream_url:
        return redirect(stream_url, code=302)
    else:
        return f"yt-dlp Error: <pre>{error_log}</pre>", 502

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
