import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['webhooks']
collection = db['jellyfin-music']

def get_song_playback_info():
    playback_info_list = []

    # Retrieve all documents from the collection
    documents = collection.find()

    last_playback_position_seconds = 0
    last_provider_musicbrainztrack = None
    for doc in documents:
        if doc['NotificationType'] == 'PlaybackProgress' and not doc['IsPaused']:
            provider_musicbrainztrack = doc['Provider_musicbrainztrack']
            timestamp_str = doc['UtcTimestamp']
            song_name = doc['Name']
            artist_name = doc['Artist']
            album_name = doc['Album']
            playback_position_str = doc['PlaybackPosition']

            # Convert timestamp string to datetime object
            timestamp = datetime.fromisoformat(timestamp_str)

            # Convert playback position string to seconds
            playback_position_parts = playback_position_str.split(':')
            playback_position_seconds = (
                int(playback_position_parts[0]) * 3600 +
                int(playback_position_parts[1]) * 60 +
                int(playback_position_parts[2])
            )

            if last_playback_position_seconds > playback_position_seconds or last_provider_musicbrainztrack != provider_musicbrainztrack:
                last_playback_position_seconds = playback_position_seconds
                last_provider_musicbrainztrack = provider_musicbrainztrack

                playback_info = {
                    'timestamp': timestamp,
                    'song_name': song_name,
                    'artist_name': artist_name,
                    'album_name': album_name,
                    'playback_position_seconds': playback_position_seconds
                }

                playback_info_list.append(playback_info)

    return playback_info_list

if __name__ == '__main__':
    playback_info_list = get_song_playback_info()
    for playback_info in playback_info_list:
        print(f"Timestamp: {playback_info['timestamp']}, Playing: {playback_info['artist_name']} - {playback_info['album_name']} - {playback_info['song_name']}, Playback Position: {playback_info['playback_position_seconds']} seconds")
