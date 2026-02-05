# System Architecture

Technical architecture of Eshin Broking CRM System.

---

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser["Web Browser (Vue.js)"]
        Mobile["Mobile App (React Native / Flutter)"]
    end
    
    subgraph "Web Server"
        Nginx["Nginx (Reverse Proxy)"]
    end
    
    subgraph "Application Layer"
        Gunicorn["Gunicorn / Werkzeug"]
        Frappe["Frappe Framework"]
        CRM["CRM App"]
        SocketIO["Socket.IO (Real-time)"]
    end
    
    subgraph "Background Processing"
        Workers["Redis Queue Workers"]
        Scheduler["Scheduler"]
    end
    
    subgraph "Data Layer"
        MariaDB["MariaDB"]
        Redis["Redis (Cache/Queue)"]
        Files["File Storage"]
    end
    
    subgraph "External Services"
        WhatsApp["WhatsApp Service"]
        SMS["Twilio/Exotel"]
        Email["SMTP Server"]
    end
    
    Browser --> Nginx
    Mobile --> Nginx
    Nginx --> Gunicorn
    Nginx --> SocketIO
    Gunicorn --> Frappe --> CRM
    Frappe --> MariaDB
    Frappe --> Redis
    Frappe --> Files
    Workers --> Redis
    Scheduler --> Workers
    CRM --> WhatsApp
    CRM --> SMS
    CRM --> Email
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | Vue.js | 3.x | UI framework |
| **Frontend** | Frappe UI | Latest | Component library |
| **Frontend** | Vite | 5.x | Build tool |
| **Backend** | Python | 3.10+ | Server language |
| **Backend** | Frappe | v15 | Application framework |
| **Database** | MariaDB | 10.8+ | Primary database |
| **Cache** | Redis | 6+ | Caching & queues |
| **Web Server** | Nginx | 1.18+ | Reverse proxy |
| **Process** | Supervisor | 4+ | Process manager |
| **Mobile** | React Native | - | Android app |
| **Mobile** | Flutter | - | Alternative Android app |

---

## Component Details

### Frontend Architecture

```
Vue.js Application
├── Router (Vue Router)
│   └── Pages (Dashboard, Leads, Tickets, etc.)
├── State Management (Pinia/Vuex)
│   └── Stores (User, Leads, Settings)
├── Components (Frappe UI + Custom)
│   └── Modals, Forms, Lists, Activities
└── API Layer (Frappe call/resource)
    └── HTTP requests to backend
```

### Backend Architecture

```
Frappe Framework
├── Router (werkzeug)
│   └── /api/method/* endpoints
├── DocTypes (Data Models)
│   └── CRM Lead, CRM Ticket, CRM Customer, etc.
├── Controllers (Python Classes)
│   └── Business logic per DocType
├── Hooks (hooks.py)
│   └── Event handlers, schedulers
└── Patches (Database Migrations)
    └── Schema changes, data migrations
```

### Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant DB as MariaDB
    participant R as Redis
    
    U->>F: Click "Create Lead"
    F->>B: POST /api/method/frappe.client.save
    B->>B: Validate data
    B->>DB: INSERT into tabCRM Lead
    B->>R: Publish event
    B-->>F: Return success
    F-->>U: Show confirmation
    R->>B: Trigger background job
```

---

## DocType Relationships

```mermaid
erDiagram
    CRM_Lead ||--o{ CRM_Activity : has
    CRM_Lead ||--o{ CRM_Task : has
    CRM_Lead ||--o{ CRM_Call_Log : has
    CRM_Lead }|--|| User : assigned_to
    CRM_Lead }|--o| CRM_Customer : converts_to
    
    CRM_Ticket ||--o{ CRM_Activity : has
    CRM_Ticket ||--o{ CRM_Task : has
    CRM_Ticket }|--|| User : assigned_to
    CRM_Ticket }|--o| CRM_Lead : linked_to
    CRM_Ticket }|--o| CRM_Customer : linked_to
    
    CRM_Customer ||--o{ CRM_Ticket : has
    CRM_Customer ||--o{ CRM_Call_Log : has
    
    CRM_Assignment_Request }|--|| CRM_Lead : for
    CRM_Assignment_Request }|--|| User : from_user
    CRM_Assignment_Request }|--|| User : to_user
```

---

## Background Processing

### Job Queues

| Queue | Purpose | Workers |
|-------|---------|---------|
| **short** | Quick jobs, notifications | 2 |
| **default** | Standard processing | 2 |
| **long** | Heavy tasks, exports | 1 |

### Scheduled Tasks

| Schedule | Task | Purpose |
|----------|------|---------|
| Every minute | Task reassignment | Process overdue tasks |
| Every minute | Task notifications | Send due reminders |
| Daily 02:00 | Backup script | Automated backup |
| Daily 17:25 | Bench backup | Secondary backup |

---

## Security Architecture

```mermaid
graph LR
    subgraph "Authentication"
        Login["Login Form"]
        Session["Session Cookie"]
        API["API Key/Secret"]
    end
    
    subgraph "Authorization"
        Roles["Role-Based Access"]
        Permissions["Permission Query"]
        DocLevel["Document-Level"]
    end
    
    subgraph "Data Protection"
        TLS["TLS/HTTPS"]
        Hash["Password Hashing"]
        Mask["Field Masking"]
    end
    
    Login --> Session
    API --> Session
    Session --> Roles
    Roles --> Permissions
    Permissions --> DocLevel
```

---

## Deployment Architecture

### Single Server (Development/Small Team)

```
Ubuntu Server
├── Nginx (port 80/443)
├── Frappe Bench
│   ├── Gunicorn (port 8000)
│   ├── SocketIO (port 9000)
│   ├── Workers (background)
│   └── Scheduler (cron)
├── MariaDB
├── Redis
└── Supervisor (process management)
```

### Production (Recommended)

```
Load Balancer
├── App Server 1
│   ├── Nginx
│   ├── Gunicorn
│   └── Workers
├── App Server 2 (replica)
│   └── ...
├── Database Server
│   ├── MariaDB (primary)
│   └── MariaDB (replica)
├── Cache Server
│   └── Redis Cluster
└── File Storage
    └── S3 / NFS
```

---

## Integration Points

### WhatsApp Service

```mermaid
sequenceDiagram
    participant CRM
    participant WA as WhatsApp Service
    participant User as WhatsApp User
    
    CRM->>WA: Send message request
    WA->>User: WhatsApp message
    User-->>WA: Reply
    WA-->>CRM: Webhook callback
    CRM->>CRM: Create activity record
```

### Mobile App Sync

```mermaid
sequenceDiagram
    participant App as Mobile App
    participant API as CRM API
    participant DB as Database
    
    App->>API: POST /api/method/crm.api.mobile_sync.sync_call_logs
    API->>API: Deduplicate by device_call_id
    API->>DB: Insert/Update call logs
    API-->>App: Sync result
```

---

## Performance Considerations

| Area | Strategy |
|------|----------|
| Database | Indexes on frequently queried fields |
| Caching | Redis for session, cache, queue |
| Frontend | Lazy loading, code splitting |
| API | Pagination, field selection |
| Background | Async processing for heavy tasks |

---

## Monitoring Points

| Metric | Tool | Threshold |
|--------|------|-----------|
| Response time | Nginx logs | < 200ms |
| Error rate | frappe.log | < 1% |
| Queue depth | Redis | < 1000 |
| Database connections | MariaDB | < 100 |
| Memory usage | htop | < 80% |
