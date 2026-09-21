FROM python:3.12-slim
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
RUN pip install --no-cache-dir safetensors numpy pytest pyyaml httpx
WORKDIR /bench
COPY jcua/ ./jcua/
COPY cua-s1/ ./cua-s1/
COPY demo.jsonl checkpoint.safetensors checkpoint.json bench.py ./
ENV PYTHONPATH=/bench/jcua/src:/bench/cua-s1/src
CMD ["python3", "bench.py"]
