import os
from flask import Flask, Response, redirect, request

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
        "url": "https://www.youtube.com/@AmritaTV/live"
    }
}

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
    
    # Redirect directly to the live YouTube watch page or embed stream
    live_page = CHANNELS[channel_id]["url"]
    return redirect(live_page, code=302)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
