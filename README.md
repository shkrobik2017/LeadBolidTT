# Multiply telegram agents project

---

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Usage](#usage)

---

## Features

- FastAPI for building RESTful APIs.
- MongoDB and Beanie ODM for data persistence.
- LangChain with OllamaLLM.
- LangChain with OpenAI
- Dockerized deployment.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker and Docker Compose](https://docs.docker.com/get-docker/)
- [Poetry](https://python-poetry.org/)
- [MongoDB](https://account.mongodb.com/account/login)

---

## Installation

Follow the steps below to set up the project:

---

### 1. Clone the Repository

```bash
git clone https://github.com/shkrobik2017/LeadBolidTT.git
cd src
```

---

### 2. Configure the Environment
Create a .env file in the project root and set variables from env_example file.

---

### 3. Install Dependencies
```bash
docker-compose build
```

---

## Usage

Follow the steps below to run the project:

---

### 1. Run the application

```bash
docker-compose up
```

---

### 2. Pull ollama model to Ollama Docker Image

Do it only if you want to use Ollama LLM. 

If you use OpenAI LLM, just set LLM_NAME variable as "openai" and continue to the next step.

```bash
docker exec -it ollama ollama pull llama3.2
```

---

### 3. Access to SwaggerUI to create bots

[FastAPI - SwaggerUI](http://localhost:8000/docs)

To create bots you need next variables:
- bot_name: Name of your user bot session
- tg_session_string: User bot session string
- bot_tg_id: User bot telegram id (example: 76857367)

---

### 4. Public telegram group created by main user bot from .env file

Create telegram group and add there your another bots created in [Third paragraph](#3-access-to-swaggerui-to-create-bots)

### 5. Write message

Write message to group created in previous step and receive response. 