# {{PROJECT_NAME}} Architecture

{{PROJECT_DESCRIPTION}}

```mermaid
graph TB
    User((User)) -->|interacts| App[{{PROJECT_NAME}}]

    subgraph Core[Core System]
        %% TODO: Add your components here
        Component1[Component 1] --> Component2[Component 2]
    end

    App --> Core
```

## Components

| Component | Description | Zoom Deeper |
|-----------|-------------|-------------|
| Component 1 | Description here | [Container View](0001b-container-view.md#component1) |
| Component 2 | Description here | [Container View](0001b-container-view.md#component2) |

## Key Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| [0201](adr/0201-example.md) | Example decision | Final |

[Full ADR Index →](0001d-adr-digest.md)

## Quality Snapshot

| Attribute | Target | Current | Evidence |
|-----------|--------|---------|----------|
| Latency | <Xs | TBD | [Performance Audit](audits/performance.md) |
| Privacy | Standard | TBD | [Privacy Audit](audits/privacy.md) |
| Security | Standard | TBD | [Security Audit](audits/security.md) |

[Quality Details →](0001e-quality-attributes.md)

## Navigation

| View | Description |
|------|-------------|
| [Context View](0001a-context-view.md) | System boundary and external actors |
| [Container View](0001b-container-view.md) | Major deployable components |
| [Runtime View](0001c-runtime-view.md) | Key flows as sequence diagrams |
| [Deployment View](0001f-deployment-view.md) | Infrastructure and CI/CD |
| [Glossary](0001g-glossary.md) | Key terms and concepts |
