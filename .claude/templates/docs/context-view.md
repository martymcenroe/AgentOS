# {{PROJECT_NAME}} - Context View (C4 Level 1)

The system context shows {{PROJECT_NAME}} and its relationships to users and external systems.

```mermaid
graph TB
    User((User)) -->|uses| System[{{PROJECT_NAME}}]

    System -->|integrates with| External1[External System 1]
    System -->|stores data in| External2[External System 2]

    subgraph External Systems
        External1
        External2
    end
```

## Actors

| Actor | Description | Interactions |
|-------|-------------|--------------|
| User | Primary user of the system | Uses core features |
| Admin | System administrator | Manages configuration |

## External Systems

| System | Description | Protocol | Data Flow |
|--------|-------------|----------|-----------|
| External System 1 | Description | REST/gRPC | Bidirectional |
| External System 2 | Description | SDK | Outbound |

## Boundaries

| Boundary | Trust Level | Notes |
|----------|-------------|-------|
| Internet | Untrusted | All input validated |
| Internal Network | Semi-trusted | Service-to-service auth |
| Data Store | Trusted | Encrypted at rest |

---

[← Back to Architecture](0001-architecture.md) | [Container View →](0001b-container-view.md)
