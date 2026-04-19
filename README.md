![Web App CI](https://github.com/swe-students-spring2026/4-containers-zesty_monkeys/actions/workflows/web-app-ci.yml/badge.svg)
![Machine Learning Client CI](https://github.com/swe-students-spring2026/4-containers-zesty_monkeys/actions/workflows/machine-learning-ci.yml/badge.svg)

# Presentation Analyzer
This project is a containerized app that analyzes a presentation. A user interacts with the Flask web application, audio files are passed to the machine learning client, the client uses OpenAI-Whisper to process the audio, and the resulting analysis is stored in MongoDB.

## Contributors
- Aaron Hui [Github](https://github.com/aaronthmetic/)
- Natt Hong [Github](https://github.com/nmh6063-star/)
- Andy Liu [Github](https://github.com/andy8259/)
- Simon Ni [Github](https://github.com/narezin/)
- Tim Xu [Github](https://github.com/timxu2006/)

## Configuration Instructions

### Requirements
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Setup

#### Clone the repository
```bash
git clone https://github.com/swe-students-spring2026/4-containers-zesty_monkeys.git
```

#### Configure environment variables

Copy the example environment file.

```bash
cp .env.example .env
```

Edit `.env` with your actual values.

#### Start all containers
### Start all containers

Build and start the application.

```bash
docker compose up -d --build
```

The web application will be available at [http://localhost:5000](http://localhost:5000).

#### Stop the system

```bash
docker compose down
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://mongodb:27017` |
| `MONGO_DBNAME` | MongoDB database name | `presentation_analyzer` |

## Task boards
[Link to our Task Board!](https://github.com/orgs/swe-students-spring2026/projects/117/views/3)