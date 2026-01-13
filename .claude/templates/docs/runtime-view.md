# {{PROJECT_NAME}} - Runtime View

Key flows and sequence diagrams showing how {{PROJECT_NAME}} components interact at runtime.

## Primary User Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as API Service
    participant DB as Database

    U->>UI: Initiates action
    UI->>API: POST /api/action
    API->>DB: Query/Update
    DB-->>API: Result
    API-->>UI: Response
    UI-->>U: Display result
```

## Background Processing Flow

```mermaid
sequenceDiagram
    participant API as API Service
    participant Q as Queue
    participant W as Worker
    participant DB as Database

    API->>Q: Enqueue task
    Q-->>W: Task available
    W->>DB: Process data
    W-->>Q: Ack complete
```

## Error Handling Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as API Service
    participant Log as Logging

    U->>UI: Initiates action
    UI->>API: Request
    API->>API: Error occurs
    API->>Log: Log error
    API-->>UI: Error response
    UI-->>U: Display error message
```

## Key Scenarios

| Scenario | Description | Latency Target |
|----------|-------------|----------------|
| Primary Flow | Standard user operation | <500ms |
| Background Processing | Async task completion | <30s |
| Error Recovery | Graceful degradation | <1s |

---

[← Container View](0001b-container-view.md) | [ADR Digest →](0001d-adr-digest.md)
