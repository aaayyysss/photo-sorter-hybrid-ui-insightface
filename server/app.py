import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO, emit
from photo_sorter import build_reference_embeddings, sort_photos_with_embeddings

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

reference_db = {}

@socketio.on('build_reference')
def handle_build_reference(data):
    ref_path = data.get('refPath')
    emit('log', f"⚙️ Building reference from: {ref_path}")
    try:
        global reference_db
        reference_db = build_reference_embeddings(ref_path, emit)
        emit('build_reference_done', f"Loaded {len(reference_db)} reference identities.")
    except Exception as e:
        emit('build_reference_error', str(e))

@socketio.on('start_sorting')
def handle_start_sorting(data):
    ref_path = data.get('refPath')
    unsorted_path = data.get('unsortedPath')
    output_path = data.get('outputPath')
    threshold = data.get('threshold', 0.35)

    emit('log', f"⚙️ Starting sorting with threshold = {threshold}")
    try:
        sort_photos_with_embeddings(reference_db, unsorted_path, output_path, threshold, emit)
        emit('sorting_done', "✅ Sorting complete.")
    except Exception as e:
        emit('sorting_error', str(e))

if __name__ == '__main__':
    print("🚀 Flask SocketIO server starting...")
    socketio.run(app, host="0.0.0.0", port=5000)
