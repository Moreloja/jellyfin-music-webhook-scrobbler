import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['webhooks']
collection = db['jellyfin-music']


# Convert playback position string to seconds
def get_playback_position_seconds(doc):
    playback_position_parts = doc['PlaybackPosition'].split(':')
    playback_position_seconds = (
        int(playback_position_parts[0]) * 3600 +
        int(playback_position_parts[1]) * 60 +
        int(playback_position_parts[2])
    )
    return playback_position_seconds


def create_playback_info(doc):
    song_name = doc['Name']
    artist_name = doc['Artist']
    album_name = doc['Album']
    timestamp = datetime.fromisoformat(doc['UtcTimestamp'])
    playback_position_seconds = get_playback_position_seconds(doc)

    playback_info = {
        'timestamp': timestamp,
        'song_name': song_name,
        'artist_name': artist_name,
        'album_name': album_name,
        'playback_position_seconds': playback_position_seconds
    }

    return playback_info


def get_song_playback_info():
    final_playback_info_list = []
    playback_info_list = []

    # Retrieve all documents from the collection
    documents = collection.find()

    previous_doc = None
    first_playback_info = None
    for doc in documents:
        if doc['NotificationType'] == 'PlaybackProgress' and not doc['IsPaused']:

            if previous_doc is None:
                first_playback_info = create_playback_info(doc)
                previous_doc = doc
                continue

            if ((get_playback_position_seconds(previous_doc) > get_playback_position_seconds(doc)
                # Don't trigger if previous is exactly 1 second ahead...
                # ...this can happen in regular playback
                and not get_playback_position_seconds(previous_doc) - get_playback_position_seconds(doc) == 1)
                or previous_doc['Provider_musicbrainztrack'] != doc['Provider_musicbrainztrack']):
                
                last_playback_info = create_playback_info(previous_doc)
                playback_info_list.append(first_playback_info)
                playback_info_list.append(last_playback_info)
                first_playback_info = create_playback_info(doc)
            
            previous_doc = doc

    return playback_info_list

if __name__ == '__main__':
    playback_info_list = get_song_playback_info()
    for playback_info in playback_info_list:
        print(f"Timestamp: {playback_info['timestamp']}, Playing: {playback_info['artist_name']} - {playback_info['album_name']} - {playback_info['song_name']}, Playback Position: {playback_info['playback_position_seconds']} seconds")
