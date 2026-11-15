import os
import subprocess
from flask import Flask, redirect, Response, request

app = Flask(__name__)

CHANNELS = {
    "zeal_tv": {
        "name": "Zeal TV Kannur",
        "url": "https://www.youtube.com/@zealtvkannur/live"
    }
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

@app.route('/playlist.m3u')
def generate_playlist():
    host = request.host_url.rstrip('/')
    m3u_content = "#EXTM3U\n"
    for key, info in CHANNELS.items():
        m3u_content += f'#EXTINF:-1 tvg-id="{key}" tvg-name="{info["name"]}",{info["name"]}\n'
        m3u_content += f"{host}/stream/{key}\n"
    return Response(m3u_content, mimetype='audio/x-mpegurl')

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
    # Render dynamically assigns a port, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)