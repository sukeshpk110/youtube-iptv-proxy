import os
import time
from flask import Flask, Response, redirect, request
import yt_dlp

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
        "url": "https://www.youtube.com/@KannurVisionOnlinenews/live"
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

    ydl_opts = {
        'format': 'best',
        'no_playlist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            if 'url' in info:
                stream_url = info['url']
                STREAM_CACHE[channel_id] = {"url": stream_url, "time": current_time}
                return stream_url, None
            elif 'requested_formats' in info:
                stream_url = info['requested_formats'][0]['url']
                STREAM_CACHE[channel_id] = {"url": stream_url, "time": current_time}
                return stream_url, None
        return None, "Could not extract stream URL."
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
        return f"Extraction Error: <pre>{error_log}</pre>", 502

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
