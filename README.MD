# Modular AI System with Evolving Agents

This project provides a modular, Dockerized architecture for building AI systems with evolving agents. The system integrates Neo4j as a central vector database and knowledge graph for managing agent capabilities, tasks, relationships, and cached results. Agents interact dynamically with the orchestrator to execute tasks, refine outputs, and expand functionality by creating new API methods.

## Features

* **Dynamic API Creation**: Agents can register and call new API methods.
* **Knowledge Management**: Use Neo4j as a vector database/knowledge graph for tasks, relationships, and caching.
* **Efficiency**: Implement caching and semantic search to reduce redundant queries.
* **Scalability**: Modular Dockerized architecture for deploying agents and services.

## Architecture Overview

The system consists of the following components:

1. **Orchestrator (Coordinator Agent)**: Manages task delegation, agent communication, and caching.
2. **Specialized Agents**: Handles script/API generation and refinement, web/API-based data retrieval, and task planning.
3. **Neo4j as a Knowledge Graph**: Stores agent capabilities, tasks, and relationships.
4. **Dynamic API Manager**: Handles creation, validation, and execution of API methods by agents.
5. **Caching Layer**: Reduces API costs by storing frequently accessed results and embeddings.
6. **Dockerized Infrastructure**: Each component runs as an independent container for modularity and scalability.

## Getting Started

1. Clone the repository.
2. Build the Docker images with `docker-compose build`.
3. Start the services with `docker-compose up`.
4. Access the API endpoints via `http://localhost:8000`.

## Roadmap

The project is currently in the development phase. The following features are planned for future development:

* **Task Assignment Workflow**: Automate task assignment to agents based on their capabilities or availability.
* **Agent Evolution**: Allow agents to evolve capabilities or adjust their `base_prompt` dynamically based on completed tasks.
* **Capability Management**: Add CRUD endpoints for managing `Capability` nodes independently.

## Contributing

Contributions are welcome! Please open a pull request with your changes.
