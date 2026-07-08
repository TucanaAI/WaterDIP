# WaterDIP

> **Cloud-native Generative AI & ML Platform for Reservoir Engineering Decision Intelligence**

WaterDIP is an end-to-end AI platform for building intelligent reservoir engineering applications.

The platform combines Retrieval-Augmented Generation (RAG), production engineering analytics, cloud-native data engineering, and MLOps to support technical decision-making across oil & gas operations.

Unlike traditional reservoir engineering software, WaterDIP is being designed as an extensible AI platform capable of ingesting heterogeneous petroleum engineering datasets, constructing engineering knowledge graphs, and serving domain-aware LLM applications at scale.

---

# Vision

WaterDIP aims to become an enterprise AI platform capable of:

- Reservoir Engineering RAG
- Production Surveillance
- Decline Curve Analysis
- Water Breakthrough Diagnostics
- Injector–Producer Connectivity Analysis
- Reservoir Knowledge Graphs
- AI-assisted Engineering Reports
- Cloud-native Model Serving
- MLOps & Continuous Evaluation

---

# Current Platform Architecture

```
                    Public Datasets
      (Databricks • SPE • OPM • KGS • NLOG)
                         │
                         ▼
                Data Platform Connectors
                         │
       ┌─────────────────┼──────────────────┐
       │                 │                  │
 Local Filesystem   Amazon S3      Databricks Marketplace
       │                 │                  │
       └─────────────────┴──────────────────┘
                         │
                         ▼
                 WaterDIP Data Platform
                         │
      Inventory → Parsing → Metadata Extraction
                         │
                         ▼
              Engineering Data Standardisation
                         │
                         ▼
                  Chunking & Embeddings
                         │
               ┌─────────┴─────────┐
               │                   │
          Qdrant / pgvector      Neo4j
               │                   │
               └─────────┬─────────┘
                         ▼
               WaterDIP RAG Platform
                         │
          FastAPI • OpenAI • vLLM • WaterDIP
                         │
                         ▼
                 Reservoir Intelligence APIs
```

---

# Repository Structure

```
WaterDIP/

apps/
    api/
    web/

packages/
    waterdip-core/
    waterdip-models/

data/
    raw/
    processed/
    registry/

docs/

infra/
    docker/
    helm/
    k8s/
    terraform/

reports/

tools/
```

---

# Major Components

## AI Platform

- FastAPI
- Provider abstraction
- Streaming LLM inference
- OpenAI integration
- Future WaterDIP foundation model

---

## Data Platform

Current development:

- Dataset registry
- Connector framework
- File inventory
- Engineering parsers

Planned:

- Databricks Marketplace connector
- Amazon S3 connector
- Azure Blob connector
- HTTP connector
- Local filesystem connector

---

## Reservoir Engineering

Current roadmap:

- Decline Curve Analysis
- Water Cut Analytics
- Water Breakthrough Detection
- Injector–Producer Connectivity
- Reservoir Recommendations

---

## Retrieval-Augmented Generation

Current roadmap:

- Engineering document ingestion
- PDF parsing
- LAS parsing
- CSV & Excel parsing
- Metadata extraction
- Chunking
- Embeddings
- Qdrant
- Neo4j
- Engineering citations

---

## MLOps

Current roadmap:

- MLflow
- Kubernetes
- KServe
- vLLM
- OpenTelemetry
- Prometheus
- Grafana
- AWS EKS

---

# Technology Stack

## AI

- OpenAI
- vLLM (planned)
- WaterDIP Models (planned)

## Backend

- FastAPI
- Flask
- Pydantic

## Data Platform

- Amazon S3
- PostgreSQL
- Qdrant
- Neo4j

## Cloud

- AWS
- Docker
- Kubernetes
- Helm
- Terraform

## Observability

- Prometheus
- Grafana
- OpenTelemetry

---

# Current Development Status

## Completed

- Modular FastAPI platform architecture
- Provider abstraction
- Streaming LLM inference
- Async API inference
- Load testing framework
- Prometheus metrics
- Structured logging
- Flask demonstration frontend
- Repository refactor into platform architecture
- Initial Data Platform package
- AWS account & S3 integration
- Initial public dataset acquisition

---

## In Progress

- Connector framework
- Amazon S3 connector
- Databricks Marketplace connector
- Dataset registry
- Engineering data ingestion pipeline

---

## Planned

- LAS parser
- Reservoir report parser
- Engineering metadata extraction
- Qdrant integration
- Neo4j knowledge graph
- Reservoir Engineering RAG
- WaterDIP domain model
- Kubernetes deployment
- AWS EKS deployment
- MLflow
- KServe
- Production evaluation pipeline

---

# Running the Platform

## Create virtual environment

```powershell
py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1
```

---

## Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Start FastAPI

```powershell
uvicorn apps.api.app.main:app --reload --host 127.0.0.1 --port 8080
```

---

## Start Flask frontend

```powershell
python apps/web/llm.py
```

---

Open:

```
http://127.0.0.1:5000
```

---

# Long-term Goal

WaterDIP is being developed as a production-ready AI Platform demonstrating modern Generative AI, Data Platform Engineering, and MLOps practices for large-scale engineering workloads.

The project serves as a practical implementation of enterprise-grade AI infrastructure spanning cloud-native data ingestion, retrieval-augmented generation, knowledge graphs, model serving, observability, and production deployment.


| Phase                     | Status |
| ------------------------- | ------ |
| Platform Architecture     | ✅      |
| Data Platform             | 🚧     |
| Connectors                | 🚧     |
| Engineering Parsers       | ⏳      |
| RAG                       | ⏳      |
| Knowledge Graph           | ⏳      |
| MLOps                     | ⏳      |
| WaterDIP Foundation Model | ⏳      |
