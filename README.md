This program takes raw jellyfin webhook song events and transforms them to `playback-info` documents.
It reads all events from the `jellyfin-music` collection.

Check out [Webhook Saver](https://github.com/Moreloja/webhook-saver) to learn how song events from jellyfin can be saved using the jellyfin webhook plugin.

## Document structure

Transformed documents look like the following example and are saved in the `playback-info` collection.

``` json
{
    _id: ObjectId('64c8e4844f1517ea5472483a'),
    Album: 'The Last Stand',
    Artist: 'Sabaton',
    DeviceId: 'This is my DeviceId :D',
    Name: 'Hill 3234',
    UserId: 'This is my UserId :P',
    timestamp: ISODate('2023-08-01T10:49:35.620Z'),
    timestamp_end: ISODate('2023-08-01T10:53:06.641Z'),
    Provider_musicbrainzalbum: '3e3737ab-cf23-4a39-be93-824cb8a4e3e2',
    Provider_musicbrainzalbumartist: '39a31de6-763d-48b6-a45c-f7cfad58ffd8',
    Provider_musicbrainzartist: '39a31de6-763d-48b6-a45c-f7cfad58ffd8',
    Provider_musicbrainzreleasegroup: 'c178c4e1-49af-44a5-9cb6-2182a5a42820',
    Provider_musicbrainztrack: '9ccae6a4-33d6-4823-95ac-ebccd7917aaf',
    ServerVersion: '10.8.10',
    Year: 2016,
    playback_position_seconds: 210,
    run_time: 211
}
```
