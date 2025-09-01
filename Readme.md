# mini-rag

this is a minimal implementaion of the RAG model for question answering.

## Requirements

- Python 3.13 or later

#### Instal Python using MiniConda

1. Download and install MiniConda from [here](https://www.anaconda.com/docs/getting-started/miniconda/install)
2. create a new environment using the following command:

```bash
$ conda create -n mini-rag
```

3. activate the environmentL

```bash
$ conda activate mini-rag
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your env variables in the .env file like "OPENAI_API_KEY" value.

##Run Docker compose service

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials

## Run the FastAPI server

```bash
$ uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
