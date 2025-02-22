import os
import threading
import configparser
from contextlib import suppress

from dotenv import load_dotenv
from quart import Quart, send_file
from quart_cors import cors
from util.download import CACHE_DIR, ZIP_DIR, DOWNLOAD_DIR, start, start_playlist
from util.spotify import start_token_thread
from util.statistics import totalCaches, totalSongs, totalPlaylists, totalSongData, totalStorage, songStorage, playlistStorage, cacheStorage

app = Quart(__name__)
app = cors(app, allow_origin="*")

config = configparser.ConfigParser()

config.read('config.ini')

port = config.get('server', 'port', fallback='7000')
ip = config.get('server', 'ip', fallback='127.0.0.1')

@app.route('/track/<string:id>')
async def serve_audio(id):
    try:
        filename = await start(id)
        return await send_file(filename, mimetype='audio/mpeg'), 200
    except:
        return {
            "failed": True,
            "message": "Song not found"
        }, 404

@app.route('/playlist/<string:id>')
async def serve_playlist(id):
    try:
        filename = await start_playlist(id)
        return await send_file(filename, as_attachment=True, attachment_filename=f'{id}.zip', mimetype='application/zip'), 200
    except:
        return {
            "failed": True,
            "message": "Playlist not found"
        }, 404

@app.route("/stats")
async def stats():
    return {
        "failed": False,
        "data": {
            "total": await totalCaches(),
            "songs": await totalSongs(),
            "caches": await totalSongData(),
            "playlists": await totalPlaylists()
        },
        "storage": {
            "total": await totalStorage(),
            "songs": await songStorage(),
            "playlists": await playlistStorage(),
            "caches": await cacheStorage()
        }
    }

@app.route('/')
async def serve_index():
    return {
        "message": "Online",
        "github": "https://github.com/g3vv/yank",
        "routes": {
            "track": "/track/{song_id}",
            "playlist": "/playlist/{playlist_id}",
            "stats": "/stats"
        }
    }

token_thread = threading.Thread(target=start_token_thread)
token_thread.start()

if __name__ == '__main__':
    for directory in {CACHE_DIR, ZIP_DIR, DOWNLOAD_DIR}:
        with suppress(FileExistsError):    
            os.mkdir(directory)

    app.run(ip, port=port)
