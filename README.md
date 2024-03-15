# Kerbal Telemetry


## Prerequisites

**Game Setup**

You will need to have the following installed and set up:

- [Kerbal Space Program](https://www.kerbalspaceprogram.com)
- [kRPC](https://krpc.github.io/krpc/)

**Development Setup**

You will need to have the following installed:

- [Python 3](https://www.python.org)
- [Docker](https://www.docker.com)


## Getting Started

### Set up Python virtual environment

You can read more about setting up Python virtual environments [here](https://docs.python.org/3/library/venv.html).

**Linux / MacOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows**

```cmd
python -m venv venv
venv\Scripts\activate
```

### Install Python dependencies

```bash
pip install -r requirements.txt
```

### Run the Docker containers

```bash
docker-compose up
```


### Run the telemetry script
    
```bash
python src/__main__.py
```

### Set up Elasticsearch / Kibana

You can access Kibana at [http://localhost:5601](http://localhost:5601).

TODO

