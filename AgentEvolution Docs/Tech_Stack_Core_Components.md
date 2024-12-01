
# Section 1: Core Components of the Tech Stack

## **Core Components of the Docker Stack**

### **1. Neo4j Container**
- **Purpose**: Acts as the central knowledge graph and vector database, storing agent capabilities, tasks, relationships, and cached results.
- **Configuration**:
  - **Image**: `neo4j:latest`
  - **Ports**: Expose ports `7474` (HTTP) and `7687` (Bolt) for web interface and database access.
  - **Volumes**: Mount persistent storage for data durability.
  - **Environment Variables**: Set authentication credentials and accept license agreements.

### **2. Primary API Container**
- **Purpose**: Provides immutable functionalities such as updating the knowledge base, registering new Python functions, managing task queues, and orchestrating agent activities.
- **Configuration**:
  - **Image**: Custom-built image containing the orchestrator and essential APIs.
  - **Ports**: Expose the necessary port (e.g., `8000`) for API access.
  - **Volumes**: Mount volumes for configuration files and logs.
  - **Environment Variables**: Configure database connections, API keys, and other settings.

### **3. Evolving API Container**
- **Purpose**: Hosts dynamically generated functionalities. This container can be programmatically updated and restarted to incorporate new capabilities as they are developed.
- **Configuration**:
  - **Image**: Custom-built image designed to load and execute dynamically added functions.
  - **Ports**: Expose the necessary port (e.g., `8001`) for API access.
  - **Volumes**: Mount volumes where new functions can be added.
  - **Environment Variables**: Configure settings to monitor changes and reload functionalities upon updates.

### **4. Agent Containers**
- **Purpose**: Each agent operates within its own container, performing specialized tasks such as coding, research, or planning.
- **Configuration**:
  - **Image**: Custom-built images tailored to each agent's role.
  - **Ports**: Expose ports if agents need to communicate externally.
  - **Volumes**: Mount volumes for accessing shared resources or storing agent-specific data.
  - **Environment Variables**: Set configurations relevant to each agent's functionality.

### **5. Message Broker Container**
- **Purpose**: Facilitates communication between the orchestrator and agents, managing task distribution and inter-agent messaging.
- **Configuration**:
  - **Image**: `rabbitmq:management` for a message broker with a management interface.
  - **Ports**: Expose ports `5672` (AMQP) and `15672` (management interface).
  - **Volumes**: Mount volumes for persistent message storage.
  - **Environment Variables**: Configure user credentials and virtual hosts.

### **6. Monitoring and Logging Container**
- **Purpose**: Aggregates logs and monitors the health and performance of the entire stack.
- **Configuration**:
  - **Image**: `prom/prometheus` for monitoring and `grafana/grafana` for dashboards.
  - **Ports**: Expose ports `9090` (Prometheus) and `3000` (Grafana).
  - **Volumes**: Mount volumes for configuration and data storage.
  - **Environment Variables**: Set up data sources and dashboard configurations.
