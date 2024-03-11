import io
import os

import numpy as np
import soundfile
import tritonclient.grpc.aio as grpcclient
from tritonclient.utils import np_to_triton_dtype
from loguru import logger

TRITON_HOST = os.getenv("TRITON_HOST", "127.0.0.1")
TRITON_PORT = os.getenv("TRITON_PORT", 8001)
WHISPER_NAME = os.getenv("WHISPER_MODEL_NAME", "whisper")

logger.info(f"Create Triton GRPC client on {TRITON_HOST}:{TRITON_PORT}")

class Client:
    def __init__(self) -> None:
        url = f"{TRITON_HOST}:{TRITON_PORT}"
        self.triton_client = grpcclient.InferenceServerClient(url=url, verbose=False)
        self.protocol_client = grpcclient

    async def infer(self, audio_bytes: bytes, padding_duration=10,
                    whisper_prompt: str = "<|startoftranscript|><|en|><|transcribe|><|notimestamps|>"):
        waveform, sample_rate = self._load_audio(audio_bytes)
        duration = int(len(waveform) / sample_rate)

        # padding to nearset 10 seconds
        samples = np.zeros(
            (
                1,
                padding_duration * sample_rate * ((duration // padding_duration) + 1),
            ),
            dtype=np.float32,
        )

        samples[0, : len(waveform)] = waveform

        lengths = np.array([[len(waveform)]], dtype=np.int32)

        inputs = [
            self.protocol_client.InferInput(
                "WAV", samples.shape, np_to_triton_dtype(samples.dtype)
            )
            ,
            self.protocol_client.InferInput(
                "TEXT_PREFIX", [1, 1], "BYTES"
            ),
        ]
        inputs[0].set_data_from_numpy(samples)

        input_data_numpy = np.array([whisper_prompt], dtype=object)
        input_data_numpy = input_data_numpy.reshape((1, 1))
        inputs[1].set_data_from_numpy(input_data_numpy)

        outputs = [self.protocol_client.InferRequestedOutput("TRANSCRIPTS")]
        sequence_id = 10086

        response = await self.triton_client.infer(
            WHISPER_NAME, inputs, request_id=str(sequence_id), outputs=outputs
        )

        decoding_results = response.as_numpy("TRANSCRIPTS")[0]
        if type(decoding_results) == np.ndarray:
            decoding_results = b" ".join(decoding_results).decode("utf-8")
        else:
            # For wenet
            decoding_results = decoding_results.decode("utf-8")

        return decoding_results

    def _load_audio(self, audio_bytes):
        waveform, samplerate = soundfile.read(file=io.BytesIO(audio_bytes), dtype='float32')
        assert samplerate == 16000, f"Only support 16k sample rate, but got {samplerate}"
        return waveform, samplerate
