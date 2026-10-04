# WaterDIP

> **Cloud-Native Generative AI Platform for Reservoir Water Management Decision Intelligence**

WaterDIP is an end-to-end Generative AI and engineering intelligence platform for reservoir engineering, petroleum data engineering, Retrieval-Augmented Generation (RAG), and reservoir water management decision intelligence.

The platform combines cloud-native petroleum data ingestion, canonical engineering data models, engineering-aware parsing and chunking, vector search, knowledge graphs, self-hosted AI models, Large Language Models, and agentic workflows to build AI systems capable of supporting reservoir engineering workflows from raw subsurface datasets through engineering reasoning and decision support.

---

# Vision

WaterDIP is being developed as an enterprise AI platform for:

- Reservoir Engineering Decision Intelligence
- Reservoir Water Management
- Water Breakthrough Diagnostics
- Production Surveillance
- Decline Curve Analysis
- Injector–Producer Connectivity
- Well and Reservoir Intelligence
- Reservoir Knowledge Graphs
- Engineering Copilots
- AI-assisted Engineering Reports
- Hybrid RAG
- Multi-Agent Reservoir Engineering Workflows
- Agentic Reservoir Intelligence

The long-term objective is to connect heterogeneous petroleum engineering data with retrieval, engineering knowledge, self-hosted AI models, and domain-aware reasoning systems capable of supporting engineering decisions across the reservoir lifecycle.

---

# Platform Architecture

```text
                     Public Petroleum Data Sources
          (Databricks Marketplace • SPE • OPM • NPD • KGS)

                                │
                                ▼

                     WaterDIP Connector Framework

         Local FS       HTTP       Amazon S3       Azure Blob
                              Databricks Marketplace

                                │
                                ▼

                       WaterDIP Data Platform

                         Dataset Inventory
                                │
                         Dataset Registry
                                │
                     Metadata & Provenance
                                │
                                ▼
                  Engineering Parser Framework
                                │
        ┌───────────┬───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼           ▼
       PDF         DOCX        CSV        Excel        LAS
        │           │           │           │           │
        └───────────┴───────────┼───────────┴───────────┘
                                ▼
                       WaterDIPDocument
                                │
                  Canonical Engineering Schema
                                │
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
      Provenance         Engineering Metadata   Structured Content
                                │
                                ▼
                 Engineering-Aware Chunking
                                │
           ┌────────────────────┼───────────────────┐
           ▼                    ▼                   ▼
        Sections              Tables             Well Logs
           │                    │                   │
           └────────────────────┼───────────────────┘
                                ▼
                        DocumentChunk[]
                                │
                                ▼
               Self-Hosted Embedding Infrastructure
                         (Next Phase)
                                │
                       CPU / CUDA GPU
                                │
                                ▼
                        Vector Embeddings
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
          Qdrant / pgvector                  Neo4j
                │                               │
                └───────────────┬───────────────┘
                                ▼
                     WaterDIP Hybrid RAG
                                │
             Self-Hosted LLMs • vLLM • Agents
                + Optional Hosted Providers
                                │
                                ▼
              Reservoir Engineering Intelligence
                                │
                                ▼
        Reservoir Water Management Decision Intelligence
```

---

# Engineering Intelligence Pipeline

WaterDIP follows a layered engineering intelligence architecture:

```text
Raw Petroleum Data
        │
        ▼
Connector Framework
        │
        ▼
Dataset Registry / Inventory
        │
        ▼
ParseSource
        │
        ▼
Parser Registry / Dispatcher
        │
        ▼
Engineering Parser
        │
        ▼
WaterDIPDocument
        │
        ▼
Engineering-Aware Chunking
        │
        ▼
DocumentChunk[]
        │
        ▼
Embedding Pipeline
        │
        ▼
EmbeddingRecord[]
        │
        ▼
Vector Index + Knowledge Graph
        │
        ▼
Hybrid Retrieval
        │
        ▼
Reranking
        │
        ▼
Self-Hosted LLM
        │
        ▼
Engineering Reasoning
        │
        ▼
Agentic Reservoir Intelligence
```

The architecture intentionally separates:

**ingestion → parsing → normalization → chunking → embedding → indexing → retrieval → reasoning → action**

This allows each layer to evolve independently while maintaining deterministic provenance and engineering context.

---

# Repository Structure

```text
WaterDIP/

apps/
│
├── api/
│   └── app/
│       └── data_platform/
│           │
│           ├── parsing/
│           │   ├── chunking/
│           │   ├── extractors/
│           │   ├── models/
│           │   └── well_logs/
│           │
│           └── embeddings/              # Next phase
│
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

tests/
│
└── data_platform/
    └── parsing/
```

---

# Platform Components

## AI Platform

### Completed

- FastAPI platform
- LLM provider abstraction
- Streaming LLM inference
- Async inference
- OpenAI integration
- Metrics and logging foundations

### Planned

- Self-hosted embedding inference
- GPU inference infrastructure
- Self-hosted LLM serving
- vLLM
- Model routing
- WaterDIP domain models
- Reranking models
- Judge models
- Agent framework
- Multi-agent orchestration
- Agentic Reservoir Intelligence

WaterDIP is being developed using a **self-hosted-first, provider-agnostic model architecture**.

Self-hosted models will provide the primary learning and experimentation environment for:

- GPU inference
- CUDA execution
- Model serving
- Batching
- Latency optimisation
- Throughput optimisation
- GPU memory management
- Quantisation
- Model evaluation
- Reranking
- Judge models
- Hallucination evaluation
- Consistency testing
- SLO engineering
- Monitoring and observability
- Container orchestration

Hosted model providers remain available as interchangeable fallback or specialised inference options.

---

# Data Platform

## Completed

- Dataset registry
- Connector framework
- Local filesystem connector
- HTTP connector
- Amazon S3 connector
- Databricks Marketplace connector
- Azure Blob connector foundation
- Automated Databricks → Amazon S3 transfer pipeline
- Manifest generation
- Engineering dataset inventory
- Dataset provenance
- Large-scale cloud ingestion
- Parameterised Databricks ingestion jobs
- S3-based petroleum data lake

### Databricks Ingestion Architecture

```text
Local Python
      │
      ▼
Databricks Jobs API
      │
      ▼
Databricks Notebook
      │
      ▼
Marketplace Volume
      │
      ▼
Amazon S3
      │
      ▼
waterdip-data-lake
```

Large datasets are transferred directly from Databricks infrastructure to Amazon S3 without routing the dataset through the local development machine.

## Current Datasets Ingested

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

## Pending Large-Scale Transfers

- Seismic ST0202 (~1.17 TB)
- Seismic ST10010 (~2.59 TB)

---

# Engineering Intelligence

Engineering Intelligence converts heterogeneous petroleum data into canonical, retrieval-ready engineering representations.

Parts 1–5 are implemented.

---

## Part 1 — Core Parser Framework ✅

WaterDIP implements an extensible parser infrastructure rather than coupling file processing directly to individual formats.

### Implemented

- `ParseSource`
- `ParserContext`
- `ParserResult`
- `BaseParser`
- `ParserRegistry`
- `ParserDispatcher`
- `ParsingPipeline`
- Pipeline stages
- Parser registration
- Parser selection
- Parser priority scoring
- Parser validation
- Parser execution diagnostics
- Typed parsing exceptions

### Architecture

```text
Raw File
    │
    ▼
ParseSource
    │
    ▼
ParserRegistry
    │
    ▼
ParserDispatcher
    │
    ▼
BaseParser
    │
    ▼
ParserResult
    │
    ▼
ParsingPipeline
```

The framework supports pluggable parsers and deterministic parser selection while remaining independent of individual engineering formats.

---

# Part 2 — Canonical Engineering Models ✅

WaterDIP uses a strongly typed canonical engineering representation built with Pydantic.

The central model is:

```text
WaterDIPDocument
│
├── id
├── schema_version
├── document_type
├── title
├── text
│
├── source
│   └── SourceProvenance
│
├── engineering
│   ├── WellContext
│   ├── ReservoirContext
│   ├── ProductionContext
│   ├── EngineeringEntity[]
│   └── Measurement[]
│
├── sections[]
├── tables[]
├── figures[]
├── attachments[]
│
├── quality_status
├── warnings
└── metadata
```

### Implemented Canonical Models

- `WaterDIPDocument`
- `SourceProvenance`
- `SourceLocation`
- `EngineeringMetadata`
- `EngineeringEntity`
- `Measurement`
- `WellContext`
- `ReservoirContext`
- `ProductionContext`
- `DocumentSection`
- `DocumentTable`
- `DocumentFigure`
- `DocumentAttachment`
- `DocumentChunk`
- `ChunkPosition`

### Engineering Metadata

Canonical engineering context supports concepts including:

- Field
- Well
- Wellbore
- Completion
- Formation
- Reservoir
- Zone
- Basin
- Block
- Licence
- Operator
- Country
- Production rates
- Injection rates
- Water cut
- Gas-oil ratio
- Pressure
- Porosity
- Permeability
- Saturation
- Reservoir temperature
- Depth

### Deterministic Identity

WaterDIP generates deterministic identifiers for documents and chunks using source provenance and content.

This enables:

- Idempotent ingestion
- Duplicate detection
- Reproducible processing
- Embedding cache reuse
- Traceable retrieval
- Reliable vector updates

---

# Part 3 — Basic Engineering Parsers ✅

WaterDIP implements format-specific parsers that convert heterogeneous engineering files into `WaterDIPDocument`.

### Implemented Parsers

| Parser | Status |
|---|---|
| TXT / Markdown / Logs | ✅ |
| PDF | ✅ |
| CSV | ✅ |
| Excel (`.xlsx`, `.xlsm`) | ✅ |
| DOCX | ✅ |
| JSON | ✅ |
| XML | ✅ |
| ZIP | ✅ |

### PDF

Supports:

- Page-level text extraction
- Page provenance
- PDF metadata
- Structured sections
- Detection of PDFs without extractable text

OCR is intentionally excluded from the baseline parser and can be introduced as a specialised extraction path.

### CSV

Supports:

- Delimiter detection
- Column extraction
- Row preservation
- Canonical table generation
- Retrieval-oriented textual representation

### Excel

Supports:

- Multi-sheet workbooks
- Read-only workbook processing
- Canonical table generation
- Formula-result reading through `data_only`

### DOCX

Supports:

- Paragraph extraction
- Heading-aware sections
- Table extraction
- Core document properties

### JSON / XML

Supports:

- Structured data extraction
- Retrieval-safe textual representations
- Structured metadata preservation

XML processing uses secure parsing through `defusedxml`.

### ZIP

ZIP files are treated as engineering containers rather than generic text.

The parser supports:

- Archive inventory
- Member metadata
- SHA-256 checksums
- Path traversal protection
- Member-count limits
- Expanded-size limits
- Compression-ratio protection

Recursive archive parsing is deliberately deferred to a controlled pipeline stage.

---

# Part 4 — LAS / Well-Log Engineering Intelligence ✅

WaterDIP includes a petroleum-domain-aware LAS parser rather than treating LAS files as generic text.

### Implemented

- LAS parsing
- LAS header extraction
- Well metadata
- Field metadata
- Company/operator metadata
- Well identifiers
- Depth interval extraction
- Depth units
- Sampling interval
- NULL-value handling
- Curve definitions
- Curve units
- Curve descriptions
- Curve statistics
- Well-log engineering entities
- LAS provenance

### Well-Log Curve Classification

WaterDIP performs conservative mnemonic-based classification for:

- Depth
- Gamma Ray
- Spontaneous Potential
- Resistivity
- Density
- Neutron
- Sonic
- Caliper
- Photoelectric Factor
- Porosity
- Saturation
- Temperature
- Pressure
- Permeability
- Facies

Unknown mnemonics remain explicitly classified as unknown rather than being aggressively guessed.

### Curve Statistics

Numerical log curves support:

- Valid sample count
- NULL count
- Minimum
- Maximum
- Mean
- Standard deviation
- P10
- P50
- P90

LAS NULL sentinels are excluded from engineering statistics.

### Architecture

```text
LAS
 │
 ▼
LASParser
 │
 ├── Well Headers
 ├── Depth
 ├── Curve Definitions
 ├── Units
 ├── NULL Handling
 ├── Curve Classification
 └── Curve Statistics
 │
 ▼
WellLogMetadata
 │
 ▼
EngineeringMetadata
 │
 ▼
WaterDIPDocument
```

Petrophysical interpretation is intentionally separated from parsing.

The parser extracts and normalises source information but does not silently derive quantities such as:

- Vsh
- Effective porosity
- Water saturation
- Net pay
- Hydrocarbon pore volume
- Permeability transforms

These belong to future explicit engineering interpretation workflows with methods, assumptions, and provenance.

---

# Part 5 — Engineering-Aware Chunking ✅

WaterDIP implements domain-aware chunking rather than generic fixed-character splitting.

Different engineering data types use different retrieval strategies.

```text
WaterDIPDocument
        │
        ▼
Chunker Registry
        │
        ├── SectionChunker
        ├── TableChunker
        ├── WellLogChunker
        └── TextChunker
        │
        ▼
DocumentChunk[]
```

### Implemented Chunkers

#### Section-Aware Chunking

Used for structured engineering documents such as:

- PDF reports
- DOCX reports
- Technical reports

Preserves:

- Section title
- Section hierarchy
- Page range
- Section identifier
- Engineering metadata

#### Table-Aware Chunking

Used for:

- Production data
- Injection data
- Engineering spreadsheets
- Tabular datasets

Every table chunk preserves:

- Column names
- Units
- Table identity
- Row ranges
- Source metadata

Headers are repeated across table windows so retrieved numerical values retain their engineering meaning.

#### Well-Log-Aware Chunking

Generates retrieval units for:

- Well-log summaries
- Curve metadata
- Curve families
- Units
- Depth coverage
- Curve statistics

Future numerical storage will support depth-window retrieval over raw log samples without placing large numerical matrices inside document metadata.

#### Generic Text Chunking

Provides deterministic fallback chunking using:

- Paragraph boundaries
- Token-budget estimation
- Token-window fallback
- Configurable overlap

### Chunker Registry

WaterDIP uses a pluggable chunker registry with priority-based selection.

```text
WellLogChunker
      ↓
TableChunker
      ↓
SectionChunker
      ↓
TextChunker
```

Generic text chunking acts as a fallback rather than overriding richer engineering structure.

### Multimodal Documents

Documents containing multiple useful representations can generate multiple retrieval units.

For example:

```text
Technical Report
      │
      ├── Section chunks
      │
      └── Table chunks
```

This prevents embedded engineering tables from being lost inside generic report text.

---

# Current Canonical Processing Flow

Parts 1–5 now provide:

```text
Petroleum Dataset
      │
      ▼
Connector
      │
      ▼
ParseSource
      │
      ▼
Parser Registry
      │
      ▼
Engineering Parser
      │
      ▼
WaterDIPDocument
      │
      ├── Provenance
      ├── Engineering Metadata
      ├── Sections
      ├── Tables
      ├── Figures
      └── Attachments
      │
      ▼
Chunker Registry
      │
      ▼
Engineering-Aware Chunker
      │
      ▼
DocumentChunk[]
```

This forms the canonical input contract for the next stage: self-hosted embedding inference.

---

# Part 6 — Self-Hosted Embedding Infrastructure 🚧

Next development phase.

WaterDIP will use a **self-hosted-first, provider-agnostic embedding architecture**.

```text
DocumentChunk[]
      │
      ▼
EmbeddingPipeline
      │
      ├── Batching
      ├── Content Hashing
      ├── Caching
      ├── Validation
      └── Telemetry
      │
      ▼
EmbeddingProvider
      │
      ├── SentenceTransformers
      │       ├── CPU
      │       └── CUDA GPU
      │
      ├── Internal Model Server
      │
      └── Hosted Provider
      │          ├── OpenAI
      │          ├── Azure OpenAI
      │          └── Other providers
      │
      ▼
EmbeddingRecord[]
```

### Planned

- `EmbeddingProvider` abstraction
- Self-hosted SentenceTransformers
- CPU inference
- NVIDIA CUDA inference
- Deterministic test provider
- Provider registry
- Embedding batching
- Embedding caching
- Content hashing
- Deterministic embedding identities
- Vector validation
- GPU memory telemetry
- Latency measurement
- Throughput measurement
- Warm-up handling
- CPU vs GPU benchmarking
- Batch-size benchmarking
- Embedding consistency testing
- Hosted-provider fallback

---

# GPU / ML Systems Engineering

GPU engineering becomes a first-class part of WaterDIP beginning with self-hosted embedding inference.

The platform will progressively explore:

- NVIDIA CUDA
- PyTorch GPU execution
- VRAM utilisation
- GPU memory allocation
- GPU memory reservation
- Model loading
- Cold-start latency
- Warm inference latency
- p50 / p95 / p99 latency
- Throughput
- Batch-size optimisation
- GPU saturation
- CPU vs GPU benchmarking
- Out-of-memory behaviour
- Model quantisation
- Model serving
- Continuous batching
- Request queues
- Admission control
- GPU scheduling
- Multi-GPU inference
- Kubernetes GPU workloads

The goal is not only to run models but to understand and optimise their production behaviour.

---

# Model Evaluation

WaterDIP will evaluate models across both **AI quality and systems performance**.

### Retrieval Evaluation

Planned metrics include:

- Recall@k
- Precision@k
- Mean Reciprocal Rank (MRR)
- nDCG@k
- Domain relevance

### Systems Evaluation

Planned metrics include:

- p50 latency
- p95 latency
- p99 latency
- Throughput
- Items/sec
- Tokens/sec
- GPU utilisation
- VRAM utilisation
- Queue latency
- Inference latency
- Cold-start time
- Error rate

### Generative AI Evaluation

Later phases will evaluate:

- Answer correctness
- Faithfulness
- Groundedness
- Citation correctness
- Engineering reasoning quality
- Hallucination rate
- Response consistency
- Judge-model consistency
- Human–judge agreement

Local judge models and optional hosted judge models will be supported.

---

# Retrieval-Augmented Generation

## Planned

- Self-hosted embeddings
- GPU embedding inference
- Vector indexing
- Semantic retrieval
- Metadata filtering
- Hybrid retrieval
- Self-hosted reranking
- Engineering context ranking
- Citation generation
- Context optimisation
- Self-hosted LLM inference
- Hosted-model fallback

The RAG architecture will combine semantic retrieval, engineering metadata, graph relationships, reranking, and model-based reasoning.

---

# Vector Retrieval

## Planned

- Qdrant and/or pgvector integration
- Vector indexing
- Metadata filtering
- Similarity search
- Engineering-aware retrieval
- Retrieval benchmarking
- Index performance benchmarking
- Retrieval evaluation datasets
- Hybrid dense/sparse retrieval

Vector infrastructure will remain independent of the embedding provider.

---

# Reranking

## Planned

WaterDIP will introduce self-hosted cross-encoder or reranking models after initial vector retrieval.

```text
Engineering Query
       │
       ▼
Vector Retrieval
       │
       ▼
Candidate Chunks
       │
       ▼
Self-Hosted Reranker
       │
       ▼
Ranked Engineering Context
```

This provides a separate optimisation layer between vector similarity and LLM generation.

---

# Knowledge Graph

## Planned

- Neo4j integration
- Reservoir ontology
- Well relationships
- Well-log relationships
- Completion relationships
- Formation relationships
- Reservoir relationships
- Production history graph
- Water injection graph
- Injector–producer relationships
- Engineering entity resolution

Example:

```text
Field
 │
 ├── HAS_WELL ──► Well
 │                 │
 │                 ├── HAS_LOG ──► WellLog
 │                 │                │
 │                 │                └── HAS_CURVE ──► LogCurve
 │                 │
 │                 ├── COMPLETED_IN ──► Reservoir
 │                 │
 │                 └── HAS_PRODUCTION ──► ProductionHistory
 │
 └── HAS_RESERVOIR ──► Reservoir
```

---

# Self-Hosted LLM Serving

## Planned

WaterDIP will support self-hosted generative models as a primary inference path.

The intended architecture separates application services from model-serving infrastructure:

```text
WaterDIP API
      │
      ▼
Model Gateway
      │
      ├── Embedding Server
      ├── Reranking Server
      ├── Generator / LLM Server
      └── Judge Model Server
               │
               ▼
          GPU Infrastructure
```

Areas of development will include:

- vLLM
- GPU model serving
- Quantisation
- KV-cache management
- Continuous batching
- Time to First Token
- Inter-token latency
- Tokens/sec
- Concurrent inference
- GPU memory management
- Model routing
- Hosted-provider fallback

---

# Reservoir Intelligence

## Planned

- Reservoir Engineering Copilot
- Water Management Assistant
- Water Breakthrough Diagnostics
- Production Surveillance
- Production Optimisation
- Injection Optimisation
- Injector–Producer Connectivity
- Well Intelligence
- Engineering Recommendations
- Engineering Report Generation
- Reservoir Decision Support

---

# Agentic Reservoir Intelligence

## Planned

Future WaterDIP agents will combine:

- Hybrid RAG
- Knowledge graph reasoning
- Engineering tools
- Reservoir datasets
- Production surveillance
- Well-log intelligence
- Model inference
- Long-term workflow state
- Tool calling
- Multi-agent orchestration

Potential specialised agents include:

```text
Reservoir Intelligence Orchestrator
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
Production   Water      Well
Agent        Agent      Agent
    │         │          │
    └─────────┼──────────┘
              ▼
      Engineering Tools
              │
              ▼
       Decision Support
```

---

# MLOps and AI Systems Engineering

## Planned

- Docker
- Kubernetes
- Helm
- Terraform
- AWS EKS
- GPU node pools
- NVIDIA GPU scheduling
- Model serving
- KServe
- MLflow
- GitHub Actions
- Model versioning
- Experiment tracking
- Evaluation pipelines
- Performance benchmarking
- SLOs
- Model monitoring

---

# Observability

WaterDIP will progressively instrument the complete AI request lifecycle.

```text
Request
   │
   ├── Embedding
   │      ├── queue latency
   │      ├── inference latency
   │      ├── batch size
   │      └── GPU metrics
   │
   ├── Retrieval
   │      ├── search latency
   │      └── candidate count
   │
   ├── Reranking
   │      ├── inference latency
   │      └── score distribution
   │
   ├── Context Construction
   │      └── token count
   │
   └── Generation
          ├── queue latency
          ├── time to first token
          ├── tokens/sec
          ├── output tokens
          └── GPU metrics
```

Planned observability stack:

- OpenTelemetry
- Prometheus
- Grafana
- NVIDIA GPU telemetry / DCGM
- Structured application logging
- Distributed tracing
- Model inference metrics
- Retrieval metrics
- Evaluation metrics

---

# Technology Stack

## AI / ML

- PyTorch
- SentenceTransformers
- Hugging Face ecosystem
- CUDA
- vLLM — planned
- Self-hosted embedding models
- Self-hosted reranking models — planned
- Self-hosted LLMs — planned
- OpenAI — optional hosted provider
- Azure OpenAI — optional hosted provider
- WaterDIP domain models — planned

## Engineering Data

- Pydantic
- lasio
- pypdf
- openpyxl
- python-docx
- defusedxml
- NumPy

## Backend

- FastAPI
- Flask
- Python 3.11
- Pydantic

## Data Platform

- Amazon S3
- Databricks Marketplace
- PostgreSQL
- Qdrant
- Neo4j

## Cloud / Infrastructure

- AWS
- Docker
- Kubernetes
- Helm
- Terraform

## GPU / Model Infrastructure

- NVIDIA CUDA
- PyTorch CUDA
- vLLM — planned
- NVIDIA GPU Kubernetes workloads — planned
- Dedicated model serving — planned

## Observability

- OpenTelemetry
- Prometheus
- Grafana
- NVIDIA DCGM — planned

---

# Current Development Status

## Phase 1 — Platform Foundation ✅

Completed:

- Modular architecture
- FastAPI backend
- LLM abstraction
- Logging
- Metrics
- Repository restructuring

---

## Phase 2 — Data Platform ✅

Completed:

- Dataset registry
- Connector framework
- Local filesystem connector
- HTTP connector
- Amazon S3 connector
- Databricks Marketplace connector
- Azure Blob foundation
- Automated Databricks → Amazon S3 ingestion
- Engineering dataset acquisition
- Manifest generation
- Dataset inventory
- Large-scale cloud data ingestion

---

## Phase 3 — Engineering Intelligence 🚧

### Part 1 — Core Parser Framework ✅

- `ParseSource`
- `BaseParser`
- Parser registry
- Parser dispatcher
- Parsing pipeline
- Pipeline stages
- Typed exceptions

### Part 2 — Canonical Engineering Models ✅

- `WaterDIPDocument`
- Source provenance
- Engineering metadata
- Well context
- Reservoir context
- Production context
- Structured document content
- Deterministic document/chunk identities

### Part 3 — Basic Engineering Parsers ✅

- TXT
- PDF
- CSV
- Excel
- DOCX
- JSON
- XML
- ZIP

### Part 4 — LAS / Well-Log Engineering Parser ✅

- LAS parsing
- Well headers
- Depth indexing
- NULL handling
- Curve metadata
- Curve classification
- Curve statistics
- Engineering metadata integration

### Part 5 — Engineering-Aware Chunking ✅

- Chunker framework
- Chunker registry
- Section-aware chunking
- Table-aware chunking
- Well-log-aware chunking
- Generic text fallback
- Multimodal document chunking
- Deterministic chunks

### Part 6 — Self-Hosted Embedding Infrastructure 🚧

Next:

- Provider-agnostic embedding framework
- SentenceTransformers
- CPU/CUDA execution
- GPU inference
- Batching
- Caching
- Embedding provenance
- GPU telemetry
- Performance instrumentation

---

# Development Roadmap

| Capability | Status |
|---|---|
| Platform Architecture | ✅ |
| Data Platform | ✅ |
| Dataset Registry | ✅ |
| Connector Framework | ✅ |
| Databricks Marketplace Integration | ✅ |
| Amazon S3 Integration | ✅ |
| Core Parser Framework | ✅ |
| Canonical Engineering Models | ✅ |
| Basic Engineering Parsers | ✅ |
| LAS / Well-Log Parser | ✅ |
| Engineering Metadata Extraction | ✅ |
| Engineering-Aware Chunking | ✅ |
| Self-Hosted Embedding Infrastructure | 🚧 |
| GPU Embedding Benchmarking | ⏳ |
| Vector Database | ⏳ |
| Retrieval Benchmarking | ⏳ |
| Self-Hosted Reranking | ⏳ |
| Knowledge Graph | ⏳ |
| Hybrid RAG | ⏳ |
| Self-Hosted LLM Serving | ⏳ |
| Judge Models / AI Evaluation | ⏳ |
| Hallucination / Consistency Evaluation | ⏳ |
| Reservoir Water Management AI Assistant | ⏳ |
| Agentic Reservoir Intelligence | ⏳ |
| GPU / Kubernetes Model Infrastructure | ⏳ |
| Full AI Observability / SLO Engineering | ⏳ |
| WaterDIP Domain Models | ⏳ |

---

# Running the Platform

## Create Environment

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

## Run Tests

Run the engineering parser and chunking tests:

```powershell
pytest tests/data_platform/parsing -v
```

Run the complete data-platform test suite:

```powershell
pytest tests/data_platform -v
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

Open the local application at port `5000`.

---

# Engineering Principles

WaterDIP development follows several core architectural principles.

### Engineering-Aware, Not Generic

Petroleum engineering data is treated according to its domain semantics.

PDF reports, production tables, LAS well logs, seismic metadata, and reservoir models should not be processed identically.

### Metadata First

Engineering metadata and provenance are preserved throughout the pipeline.

### Deterministic Processing

Documents, chunks, and future embeddings use deterministic identities wherever possible to support reproducibility and idempotency.

### Provider Agnostic

Core WaterDIP pipelines do not depend directly on a particular AI provider.

```text
WaterDIP Interface
        │
        ├── Self-Hosted Model
        ├── Internal Model Server
        └── Hosted Provider
```

### Self-Hosted First

Local and self-hosted models are a first-class execution path for embeddings, reranking, generation, and evaluation.

Hosted providers remain available where operationally or technically appropriate.

### GPU-Aware

GPU inference is treated as an engineering system requiring measurement of:

- Latency
- Throughput
- VRAM
- Utilisation
- Batching
- Concurrency
- Reliability
- Cost
- Quality

### Evaluation Driven

Model selection should be based on measured engineering retrieval and reasoning quality rather than model popularity alone.

### Observable

AI inference, retrieval, model behaviour, and infrastructure performance should be measurable end-to-end.

---

# Long-Term Goal

WaterDIP is evolving into an enterprise-scale **Reservoir Engineering Decision Intelligence Platform** combining:

- Cloud-native petroleum data engineering
- Canonical engineering knowledge representation
- Engineering-aware retrieval
- Self-hosted AI models
- GPU inference infrastructure
- Vector search
- Reservoir knowledge graphs
- Hybrid Retrieval-Augmented Generation
- Engineering evaluation
- AI observability
- Reservoir engineering tools
- Multi-agent orchestration
- Agentic Reservoir Intelligence

The target architecture is designed to progress from:

```text
Raw Petroleum Data
        ↓
Engineering Information
        ↓
Engineering Knowledge
        ↓
Engineering Retrieval
        ↓
Engineering Reasoning
        ↓
Engineering Agents
        ↓
Reservoir Water Management Decision Intelligence
```

WaterDIP is therefore moving beyond a conventional RAG application toward a domain-specific AI engineering platform capable of combining petroleum data, reservoir knowledge, self-hosted models, engineering tools, and agentic workflows for reservoir decision support.