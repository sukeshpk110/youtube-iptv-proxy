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

STREAM_CACHE = {}
CACHE_DURATION = 300  # Cache for 5 minutes

def get_live_stream_url(channel_id, youtube_url):
    current_time = time.time()
    
    if channel_id in
