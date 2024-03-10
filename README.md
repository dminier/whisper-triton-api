# Description

API Speech2Text

Whisper + Triton 

# Requirement

* NVIDIA GPU
* CUDA 12.3
* docker compose
* python 3.10

# Prepare Whisper model with TensorRT

NVIDIA Release 24.01 (build 80100513)
Triton Server Version 2.42.0


```
mount="./models/whisper/1/whisper_large_v3:/workspace/TensorRT-LLM/examples/whisper/whisper_large_v3"
docker run -it --name "whisper-server" --gpus all --net host -v $mount --shm-size=2g soar97/triton-whisper:24.01.complete

# You are inside container under /workspace 
cd TensorRT-LLM/examples/whisper

# REF : https://github.com/k2-fsa/sherpa/tree/master/triton/whisper#export-whisper-model-to-tensorrt-llm

# take large-v3 model as an example
wget --directory-prefix=assets https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt

# Build the large-v3 model using a single GPU with plugins.
python3 build.py --output_dir whisper_large_v3 --use_gpt_attention_plugin --use_gemm_plugin  --use_bert_attention_plugin --enable_context_fmha

```

 
Upload .models/whisper/1 inside a safe place like S3.

Remove your previous container.

```
docker rm "whisper-server"
```

Open http://localhost:7000/docs# and post a English WAV file 

 
# Run

```docker compose up -d
python main.py
```



# REF

Whisper + Triton : https://github.com/k2-fsa/sherpa/tree/master/triton/whisper
speech2text client : https://github.com/yuekaizhang/Triton-ASR-Client/blob/main/client.py
