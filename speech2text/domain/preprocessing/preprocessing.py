from array import array
from dataclasses import dataclass
from typing import List

import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
from six import BytesIO

from speech2text.domain.preprocessing.async_wrap import async_preprocess_wrap


@dataclass
class Channel:
    start: int
    end: int
    channel_name: str
    samples: array
    sequence: int = 0

MAX_CHUNK_DURATION = 15

def _preprocess_silence(b, frame_rate: int) -> (List[Channel], str):
    channels: List[Channel] = []
    audio = AudioSegment.from_file(BytesIO(b))
    audio = audio.set_frame_rate(frame_rate)
    mono_audios = audio.split_to_mono()

    for i in range(audio.channels):
        mono = mono_audios[i]
        total_duration = mono.duration_seconds
        # split on silence:
        chunks_on_silence: List[AudioSegment] = split_on_silence(
            mono,
            min_silence_len=500,
            silence_thresh=mono.dBFS - 16
        )
        start_chunk = 0
        end_chunk = 0
        for chunk_on_silence in chunks_on_silence:
            duration = chunk_on_silence.duration_seconds
            end_chunk = start_chunk + duration
            if duration > MAX_CHUNK_DURATION:
                nb_chunks = duration // MAX_CHUNK_DURATION
                chunks = np.array_split(chunk_on_silence.get_array_of_samples(), nb_chunks)
                for j in range(len(chunks)):
                    channels.append(
                        Channel(
                            start=start_chunk,
                            end=end_chunk,
                            channel_name=f"channel_{i}",
                            samples=chunks[j],
                            sequence=j
                        )
                    )
            else:
                channels.append(
                    Channel(
                        start=start_chunk,
                        end=end_chunk,
                        channel_name=f"channel_{i}",
                        samples=chunk_on_silence.get_array_of_samples()
                    )
                )

            start_chunk = end_chunk

    return channels, audio.duration_seconds


# we use dedicated workers for this function
preprocess_silence = async_preprocess_wrap(_preprocess_silence)
