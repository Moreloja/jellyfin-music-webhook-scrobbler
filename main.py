import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["webhooks"]
collection = db["jellyfin-music"]
playback_info_collection = db["playback-info"]


# Convert playback position string to seconds
def get_playback_position_seconds(doc):
    return convert_string_to_seconds(doc["PlaybackPosition"])


def get_run_time_as_seconds(doc):
    return convert_string_to_seconds(doc["RunTime"])


def convert_string_to_seconds(string):
    split_string = string.split(":")
    seconds = (
        int(split_string[0]) * 3600 + int(split_string[1]) * 60 + int(split_string[2])
    )
    return seconds


def create_playback_info(first_doc, previous_doc):
    timestamp = datetime.fromisoformat(first_doc["UtcTimestamp"])
    timestamp_end = datetime.fromisoformat(previous_doc["UtcTimestamp"])
    playback_position_seconds = get_playback_position_seconds(previous_doc)
    run_time = get_run_time_as_seconds(first_doc)

    playback_info = {
        "timestamp": timestamp,
        "timestamp_end": timestamp_end,
        "playback_position_seconds": playback_position_seconds,
        "run_time": run_time,
        "ServerVersion": first_doc["ServerVersion"],
        "Name": first_doc["Name"],
        "Year": first_doc["Year"],
        "Album": first_doc["Album"],
        "Artist": first_doc["Artist"],
        "Provider_musicbrainzalbumartist": first_doc["Provider_musicbrainzalbumartist"],
        "Provider_musicbrainzartist": first_doc["Provider_musicbrainzartist"],
        "Provider_musicbrainzalbum": first_doc["Provider_musicbrainzalbum"],
        "Provider_musicbrainzreleasegroup": first_doc[
            "Provider_musicbrainzreleasegroup"
        ],
        "Provider_musicbrainztrack": first_doc["Provider_musicbrainztrack"],
        "DeviceId": first_doc["DeviceId"],
        "UserId": first_doc["UserId"],
    }

    return playback_info


def save_playback_info(playback_info):
    # Use update_one with upsert=True to insert the new document if it doesn't exist
    playback_info_collection.update_one(
        {
            "timestamp": playback_info["timestamp"],
            "timestamp_end": playback_info["timestamp_end"],
            "Name": playback_info["Name"],
            "Album": playback_info["Album"],
            "Artist": playback_info["Artist"],
            "DeviceId": playback_info["DeviceId"],
            "UserId": playback_info["UserId"],
        },
        {"$set": playback_info},
        upsert=True,
    )
    # playback_info_collection.insert_one(playback_info)


def get_song_playback_info():
    return playback_info_collection.find()


def raw_data_to_playback_info() -> None:
    unique_devices = collection.distinct("DeviceId")

    for device in unique_devices:
        documents = collection.find({"DeviceId": device})

        first_doc = None
        previous_doc = None
        docs_to_delete = []
        for doc in documents:
            if doc["NotificationType"] == "PlaybackProgress" and not doc["IsPaused"]:
                if previous_doc is None:
                    first_doc = doc
                    previous_doc = doc
                    docs_to_delete.append(doc)
                    continue

                if (
                    get_playback_position_seconds(previous_doc)
                    > get_playback_position_seconds(doc)
                    # Don't trigger if previous is exactly 1 second ahead...
                    # ...this can happen in regular playback
                    and not get_playback_position_seconds(previous_doc)
                    - get_playback_position_seconds(doc)
                    == 1
                ) or previous_doc["Provider_musicbrainztrack"] != doc[
                    "Provider_musicbrainztrack"
                ]:
                    save_playback_info(create_playback_info(first_doc, previous_doc))
                    # Delete raw data for this song
                    ids_to_delete = [doc_to_delete["_id"] for doc_to_delete in docs_to_delete]
                    # Use delete_many() to delete all matching documents in one operation
                    collection.delete_many({"_id": {"$in": ids_to_delete}})

                    first_doc = doc

                previous_doc = doc
                docs_to_delete.append(doc)


if __name__ == "__main__":
    raw_data_to_playback_info()
    playback_info_list = get_song_playback_info()
    for playback_info in playback_info_list:
        print(
            f"Timestamp: {playback_info['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {playback_info['timestamp_end'].strftime('%H:%M:%S')}, Playing: {playback_info['Artist']} - {playback_info['Album']} - {playback_info['Name']}, {playback_info['playback_position_seconds']} seconds of {playback_info['run_time']}"
        )
