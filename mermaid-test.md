# Mermaid diagram gallery

Dummy file for exercising ` ```mermaid ` rendering in Summit (via termaid).

## Flowchart (`graph` / `flowchart`)

```mermaid
graph TD
    A[Start] --> B{Is valid?}
    B -->|Yes| C(Process)
    C --> D([Done])
    B -->|No| E[Error]
```

```mermaid
flowchart LR
    subgraph Client
        UI[Web UI]
    end
    subgraph Server
        API[REST API]
        DB[(Database)]
    end
    UI -->|JSON| API
    API --> DB
```

## Sequence diagram

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob
    Bob-->>Alice: Hi Alice
    Alice->>Bob: How are you?
    Bob-->>Alice: Great!
```

## Class diagram

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +fetch()
    }
    Animal <|-- Dog
```

## Entity-relationship diagram

Logical / physical model with attributes, keys, and crow's-foot notation:

```mermaid
erDiagram
    CUSTOMER {
        uuid id PK
        string name
        string email UK
        uuid org_id FK
    }
    ORDER {
        uuid id PK
        uuid customer_id FK
        date placed_at
        string status
    }
    LINE-ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
    }
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
```

## Conceptual model

Chen-style view: entities as boxes, named relationships as diamonds. Omit attributes on an `erDiagram` and Summit treats it as conceptual.

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : enrolls
    COURSE ||--o{ ENROLLMENT : offers
    INSTRUCTOR ||--o{ COURSE : teaches
```

## State diagram

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Done : complete
    Done --> [*]
```

## Block diagram

```mermaid
block-beta
    columns 3
    A["Frontend"] B["API"] C["Database"]
```

## Git graph

```mermaid
gitGraph
   commit id: "init"
   commit id: "feat"
   branch develop
   commit id: "dev-1"
   commit id: "dev-2"
   checkout main
   commit id: "fix"
   merge develop id: "merge"
```

## Gantt chart

```mermaid
gantt
    title Sprint plan
    dateFormat YYYY-MM-DD
    section Design
        Wireframes      :a1, 2026-01-01, 7d
        Review          :after a1, 3d
    section Build
        Implementation  :2026-01-08, 10d
        QA              :5d
```

## Architecture diagram

```mermaid
architecture-beta
    group api(cloud)[API]
    service db(database)[Database] in api
    service disk1(disk)[Storage] in api
    service server(server)[Server] in api
    db:R -- L:server
    disk1:T -- B:server
```

## Pie chart

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

## Treemap

```mermaid
treemap-beta
    "Frontend"
        "React": 40
        "CSS": 15
    "Backend"
        "API": 35
        "Auth": 10
```

## Mindmap

```mermaid
mindmap
  Project
    Design
      Wireframes
      Mockups
    Development
      Frontend
      Backend
    Testing
```

## Timeline

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook
         : Google
    2005 : YouTube
    2006 : Twitter
```

## Kanban

```mermaid
kanban
    Todo
        [Write docs]
        [Sketch UI]
    In Progress
        [Render mermaid]
    Done
        [Add dummy file]
```

## Quadrant chart

```mermaid
quadrantChart
    title Reach and engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 Expand
    quadrant-2 Promote
    quadrant-3 Re-evaluate
    quadrant-4 Improve
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
    Campaign C: [0.57, 0.69]
    Campaign D: [0.78, 0.34]
```

## XY chart

```mermaid
xychart-beta
    title "Monthly Revenue"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    bar [12, 18, 25, 20, 30, 35]
```

## User journey

```mermaid
journey
    title My working day
    section Go to work
        Make tea: 5: Me
        Go upstairs: 3: Me
        Do work: 1: Me, Cat
    section Go home
        Go downstairs: 5: Me
        Sit down: 5: Me
```

## Packet diagram

```mermaid
packet
    0-15: "Source Port"
    16-31: "Destination Port"
    32-63: "Sequence Number"
    64-95: "Acknowledgment Number"
```

## Requirement diagram

```mermaid
requirementDiagram
    requirement test_req {
        id: 1
        text: the test must pass
        risk: high
        verifymethod: test
    }
    element test_ent {
        type: simulation
    }
    test_ent - satisfies -> test_req
```

## C4 context

```mermaid
C4Context
    title System Context
    Person(user, "User")
    System(summit, "Summit", "Markdown viewer")
    Rel(user, summit, "Reads docs")
```

## Sankey

```mermaid
sankey-beta
    Source,Target,Value
    A,B,10
    A,C,5
    B,D,8
    C,D,5
```

## Radar

```mermaid
radar-beta
    title Skills
    axis m["Mermaid"], t["Terminal"], p["Python"]
    curve a["Summit"]{80, 90, 70}
```
