FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg wget gcc libchm-dev software-properties-common

# Install Nvidia CUDA
RUN add-apt-repository contrib
RUN apt-key del 7fa2af80
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
RUN dpkg -i cuda-keyring_1.1-1_all.deb
RUN apt-get update
RUN apt-get --allow-releaseinfo-change update
RUN apt-get install -y cuda-toolkit

COPY . .
RUN pip install -r av-worker.requirements.txt

EXPOSE 8000

CMD ["/bin/bash", "-c", "/usr/local/bin/celery -A av-worker worker --pool=threads --loglevel=info --concurrency=10"]