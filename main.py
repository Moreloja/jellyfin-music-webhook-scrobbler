import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['webhooks']
collection = db['jellyfin-music']


# Convert playback position string to seconds
def get_playback_position_seconds(doc):
    return convert_string_to_seconds(doc['PlaybackPosition'])


def get_run_time_as_seconds(doc):
    return convert_string_to_seconds(doc['RunTime'])


def convert_string_to_seconds(string):
    split_string = string.split(':')
    seconds = (
        int(split_string[0]) * 3600 +
        int(split_string[1]) * 60 +
        int(split_string[2])
    )
    return seconds


def create_playback_info(first_doc, previous_doc):
    timestamp = datetime.fromisoformat(first_doc['UtcTimestamp'])
    timestamp_end = datetime.fromisoformat(previous_doc['UtcTimestamp'])
    song_name = first_doc['Name']
    artist_name = first_doc['Artist']
    album_name = first_doc['Album']
    playback_position_seconds = get_playback_position_seconds(previous_doc)
    run_time = get_run_time_as_seconds(first_doc)

    playback_info = {
        'timestamp': timestamp,
        'timestamp_end': timestamp_end,
        'song_name': song_name,
        'artist_name': artist_name,
        'album_name': album_name,
        'playback_position_seconds': playback_position_seconds,
        'run_time': run_time
    }

    return playback_info


def get_song_playback_info():
    final_playback_info_list = []

    # Retrieve all documents from the collection
    documents = collection.find()

    first_doc = None
    previous_doc = None
    for doc in documents:
        if doc['NotificationType'] == 'PlaybackProgress' and not doc['IsPaused']:
        # if doc['NotificationType'] == 'PlaybackProgress':

            if previous_doc is None:
                first_doc = doc
                previous_doc = doc
                continue

            if ((get_playback_position_seconds(previous_doc) > get_playback_position_seconds(doc)
                # Don't trigger if previous is exactly 1 second ahead...
                # ...this can happen in regular playback
                and not get_playback_position_seconds(previous_doc) - get_playback_position_seconds(doc) == 1)
                or previous_doc['Provider_musicbrainztrack'] != doc['Provider_musicbrainztrack']
                # or (doc['IsPaused'] and not previous_doc['IsPaused'])
                ):
                
                # Method that takes first_doc and previous_doc to calculate how much of a song was played
                final_playback_info_list.append(create_playback_info(first_doc, previous_doc))
                first_doc = doc
            
            previous_doc = doc

    return final_playback_info_list

if __name__ == '__main__':
    playback_info_list = get_song_playback_info()
    for playback_info in playback_info_list:
        print(f"Timestamp: {playback_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {playback_info['timestamp_end'].strftime('%H:%M:%S')}, Playing: {playback_info['artist_name']} - {playback_info['album_name']} - {playback_info['song_name']}, {playback_info['playback_position_seconds']} seconds of {playback_info['run_time']}")
