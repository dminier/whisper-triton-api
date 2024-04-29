from array import array
from dataclasses import dataclass
from typing import List

import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
from six import BytesIO

from speech2text.domain.preprocessing.async_wrap import async_preprocess_wrap


@dataclass
class PreprocessedChunk:
    start: int
    end: int
    channel_name: str
    samples: array
    sequence: int = 0


@dataclass
class PreprocessedAudio:
    chunks: List[PreprocessedChunk]
    durations: float


MAX_CHUNK_DURATION = 15


def _preprocess_simple_chunks(b, frame_rate: int, channel_number: int) -> PreprocessedAudio:
    channels: List[PreprocessedChunk] = []
    audio = AudioSegment.from_file(BytesIO(b))
    audio = audio.set_frame_rate(frame_rate)
    mono_audios = audio.split_to_mono()

    if channel_number > -1:
        if channel_number < len(mono_audios):
            mono_audios = [mono_audios[channel_number]]
        else:
            raise Exception(
                f"Wrong channel number, only {len(mono_audios)} channels. Chose a number between 0 and {len(mono_audios) - 1}")

    for i in range(len(mono_audios)):
        mono = mono_audios[i]
        duration = mono.duration_seconds
        nb_chunks = duration // MAX_CHUNK_DURATION
        if nb_chunks > 0 :
            chunks = np.array_split(mono.get_array_of_samples(), nb_chunks)
            for j in range(len(chunks)):
                channels.append(
                    PreprocessedChunk(
                        start=-1,
                        end=-1,
                        channel_name=f"channel_{i}",
                        samples=chunks[j],
                        sequence=j
                    )
                )
        else:
            channels.append(
                PreprocessedChunk(
                    start=-1,
                    end=-1,
                    channel_name=f"channel_{i}",
                    samples=mono.get_array_of_samples(),
                    sequence=0
                )
            )

    return PreprocessedAudio(
        chunks=channels,
        durations=audio.duration_seconds
    )


def _preprocess_silence_with_sentence_timestamp(b, frame_rate: int) -> (List[PreprocessedChunk], int):
    channels: List[PreprocessedChunk] = []
    audio = AudioSegment.from_file(BytesIO(b))
    audio = audio.set_frame_rate(frame_rate)
    mono_audios = audio.split_to_mono()

    for i in range(audio.channels):
        mono = mono_audios[i]
        total_duration = mono.duration_seconds
        # split on silence:
        MIN_SILENCE_MS = 500
        KEEP_SILENCE_MS = 100
        silence_thresh = mono.dBFS * 2.5
        chunks_on_silence: List[AudioSegment] = split_on_silence(
            mono,
            min_silence_len=MIN_SILENCE_MS,
            silence_thresh=silence_thresh,
            keep_silence=KEEP_SILENCE_MS)

        start_chunk = 0
        end_chunk = 0
        for chunk_on_silence in chunks_on_silence:
            duration = chunk_on_silence.duration_seconds
            end_chunk = start_chunk + duration

            # durée minimum du chunk
            if duration > 0.5:
                if duration > MAX_CHUNK_DURATION:
                    nb_chunks = duration // MAX_CHUNK_DURATION
                    chunks = np.array_split(chunk_on_silence.get_array_of_samples(), nb_chunks)
                    for j in range(len(chunks)):
                        channels.append(
                            PreprocessedChunk(
                                start=start_chunk,
                                end=end_chunk,
                                channel_name=f"channel_{i}",
                                samples=chunks[j],
                                sequence=j
                            )
                        )
                else:
                    channels.append(
                        PreprocessedChunk(
                            start=start_chunk,
                            end=end_chunk,
                            channel_name=f"channel_{i}",
                            samples=chunk_on_silence.get_array_of_samples()
                        )
                    )

                start_chunk = end_chunk

    return PreprocessedAudio(
        chunks=channels,
        durations=audio.duration_seconds
    )


# we use dedicated workers for this function
preprocess_silence_with_sentence_timestamp = async_preprocess_wrap(_preprocess_silence_with_sentence_timestamp)
preprocess_simple_chunks = async_preprocess_wrap(_preprocess_simple_chunks)
