from dataclasses import dataclass


@dataclass
class Services:
    connector: object
    reader: object
    app_manager: object
    device_manager: object
    msg: object


@dataclass
class Events:
    audio_disconnect_event: object
    mic_disconnect_event: object
    disconnect_event: object