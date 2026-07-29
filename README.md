# WaterDIP

> **Cloud-native Generative AI Platform for Reservoir Water Management Decision Intelligence**

WaterDIP is an end-to-end Generative AI platform for reservoir engineering, petroleum data engineering, Retrieval-Augmented Generation (RAG), and engineering decision intelligence.

The platform combines cloud-native data engineering, engineering knowledge extraction, vector search, knowledge graphs, and Large Language Models to build AI assistants capable of supporting reservoir engineering workflows from raw petroleum datasets through engineering recommendations.

---

# Vision

WaterDIP is being developed as an enterprise AI platform for:

- Reservoir Engineering Decision Intelligence
- Reservoir Water Management
- Water Breakthrough Diagnostics
- Production Surveillance
- Decline Curve Analysis
- Injector–Producer Connectivity
- Reservoir Knowledge Graphs
- Engineering Copilots
- AI-assisted Engineering Reports
- Hybrid RAG
- Multi-Agent Reservoir Engineering Workflows

---

# Platform Architecture

```
                    Public Petroleum Data Sources
         (Databricks Marketplace • SPE • OPM • NPD • KGS)

                              │
                              ▼

                    WaterDIP Connector Framework

        Local FS      HTTP      Amazon S3      Azure Blob
                              Databricks Marketplace

                              │
                              ▼

                     WaterDIP Data Platform

          Inventory
               │
        Dataset Registry
               │
         Metadata Extraction
               │
          Engineering Parsers
               │
       Standardised Engineering Data
               │
           Chunk Generation
               │
           Vector Embeddings
               │
      ┌─────────────────────────────┐
      │                             │
      ▼                             ▼

   Qdrant / pgvector             Neo4j

      │                             │
      └──────────────┬──────────────┘
                     ▼

            WaterDIP Hybrid RAG Engine

                     │

      FastAPI • OpenAI • vLLM • Agents

                     │

                     ▼

 Reservoir Water Management Decision Intelligence
```

---

# Repository Structure

```
WaterDIP/

apps/
│
├── api/
├── web/

packages/
│
├── waterdip-core/
├── waterdip-models/

data/
│
├── raw/
├── processed/
├── graph/
├── registry/
├── vector/

docs/

infra/
│
├── docker/
├── helm/
├── kubernetes/
├── terraform/

reports/

tools/
```

---

# Platform Components

## AI Platform

Completed

- FastAPI platform
- Provider abstraction
- Streaming LLM inference
- Async inference
- OpenAI integration
- Metrics & logging

Planned

- vLLM
- WaterDIP domain models
- Agent framework
- Multi-agent orchestration

---

## Data Platform

Completed

- Dataset registry
- Connector framework
- Local filesystem connector
- HTTP connector
- Amazon S3 connector
- Databricks Marketplace connector
- Azure Blob connector (foundation)
- Automated Databricks → Amazon S3 transfer pipeline
- Manifest generation
- Engineering dataset inventory

Current datasets ingested

- Production
- Reports
- Technical
- Geophysics
- Eclipse
- RMS
- Drilling
- Well Logs
- Well Logs per Well
- Seismic VSP
- Geoscience Archive (~54 GB)
- Seismic 4D (~330 GB)

Pending

- Seismic ST0202 (~1.17 TB)
- Seismic ST10010 (~2.59 TB)

---

## Engineering Parsers (Next Phase)

- PDF parser
- LAS parser
- CSV parser
- Excel parser
- DOCX parser
- ZIP archive parser
- Seismic metadata extraction
- Well metadata extraction

---

## Retrieval-Augmented Generation

Next Phase

- Engineering chunking
- Metadata enrichment
- OpenAI embeddings
- Hybrid retrieval
- Semantic search
- Citation generation
- Engineering context ranking

---

## Knowledge Graph

Planned

- Neo4j integration
- Reservoir ontology
- Well relationships
- Completion relationships
- Production history graph
- Water injection graph

---

## Reservoir Intelligence

Planned

- Reservoir Engineering Copilot
- Water Management Assistant
- Water Breakthrough Diagnostics
- Production optimisation
- Injection optimisation
- Engineering recommendations

---

## MLOps

Planned

- MLflow
- Kubernetes
- Docker
- KServe
- AWS EKS
- GitHub Actions
- OpenTelemetry
- Prometheus
- Grafana

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
- Databricks Marketplace
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

## Phase 1 — Platform Foundation ✅

- Modular architecture
- FastAPI backend
- LLM abstraction
- Logging
- Metrics
- Repository restructuring

---

## Phase 2 — Data Platform ✅

- Dataset registry
- Connector framework
- Local filesystem connector
- HTTP connector
- Amazon S3 connector
- Databricks Marketplace connector
- Automated Databricks → Amazon S3 ingestion
- Engineering dataset acquisition
- Large-scale cloud data ingestion

---

## Phase 3 — Engineering Intelligence 🚧

Current work

- Engineering parsers
- Metadata extraction
- Chunk generation
- Embedding pipeline
- Vector database integration

---

## Phase 4 — Hybrid RAG ⏳

Upcoming

- Qdrant integration
- Neo4j knowledge graph
- Hybrid retrieval
- Engineering citations
- Context optimisation

---

## Phase 5 — Reservoir Decision Intelligence ⏳

Upcoming

- Reservoir Water Management AI Assistant
- Reservoir Engineering Copilot
- Engineering Agents
- WaterDIP domain intelligence

---

# Running the Platform

## Create environment

```powershell
py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1
```

---

## Install

```powershell
pip install -r requirements.txt
```

---

## Run FastAPI

```powershell
uvicorn apps.api.app.main:app --reload --host 127.0.0.1 --port 8080
```

---

## Run Flask UI

```powershell
python apps/web/llm.py
```

Open

```
http://127.0.0.1:5000
```

---

# Roadmap

| Phase | Status |
|---------|--------|
| Platform Architecture | ✅ |
| Data Platform | ✅ |
| Dataset Registry | ✅ |
| Connector Framework | ✅ |
| Databricks Marketplace Integration | ✅ |
| Amazon S3 Integration | ✅ |
| Engineering Parsers | 🚧 |
| Metadata Extraction | 🚧 |
| Chunking Pipeline | 🚧 |
| Embedding Pipeline | ⏳ |
| Vector Database | ⏳ |
| Knowledge Graph | ⏳ |
| Hybrid RAG | ⏳ |
| Reservoir Water Management AI Assistant | ⏳ |
| Agentic Reservoir Intelligence | ⏳ |
| MLOps | ⏳ |
| WaterDIP Foundation Models | ⏳ |

---

# Long-term Goal

WaterDIP is evolving into an enterprise-scale Reservoir Engineering Decision Intelligence platform that combines cloud-native petroleum data engineering, knowledge graphs, vector search, Retrieval-Augmented Generation, and AI agents to support reservoir water management, production optimisation, and engineering decision-making across the asset lifecycle.