# C4 Component Diagram — Catalog Service

**Level**: Component (Level 3)
**Date**: 2026-05-08
**Service**: Catalog Service (`fiap-sub-fase4-catalog`)

## Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Catalog Service                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Presentation Layer                         │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │  │
│  │  │  vehicles    │  │vehicle_status│  │     health       │  │  │
│  │  │  router      │  │  router      │  │     router       │  │  │
│  │  │              │  │              │  │                  │  │  │
│  │  │ POST /vehicles│  │PATCH /{id}  │  │  GET /health     │  │  │
│  │  │ GET  /vehicles│  │  /status    │  │                  │  │  │
│  │  │ GET  /{id}   │  │              │  └──────────────────┘  │  │
│  │  │ PUT  /{id}   │  └──────┬───────┘                        │  │
│  │  └──────┬───────┘         │                                │  │
│  │         │          ┌──────▼────────────────────────────┐   │  │
│  │         │          │         OAuth2 Middleware          │   │  │
│  │         │          │  (python-jose JWT Bearer validation)│   │  │
│  │         │          └───────────────────────────────────┘   │  │
│  └─────────┼───────────────────────────────────────────────────┘  │
│            │                                                        │
│  ┌─────────▼──────────────────────────────────────────────────┐   │
│  │                   Application Layer                         │   │
│  │                                                             │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐  │   │
│  │  │ CreateVehicle  │  │ UpdateVehicle  │  │  GetVehicle │  │   │
│  │  └────────────────┘  └────────────────┘  └─────────────┘  │   │
│  │  ┌──────────────────────┐  ┌────────────────────────────┐  │   │
│  │  │ ListAvailableVehicles│  │  UpdateVehicleStatus       │  │   │
│  │  └──────────────────────┘  └────────────────────────────┘  │   │
│  └──────────────────────────┬─────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼─────────────────────────────────┐   │
│  │                    Domain Layer                             │   │
│  │                                                             │   │
│  │  ┌─────────────────────────────┐  ┌─────────────────────┐  │   │
│  │  │   Vehicle (Entity)          │  │  VehicleRepository  │  │   │
│  │  │   - id: UUID                │  │  (Abstract)         │  │   │
│  │  │   - brand, model, year      │  │  - save()           │  │   │
│  │  │   - color, price, status    │  │  - find_by_id()     │  │   │
│  │  │   - created_at, updated_at  │  │  - update()         │  │   │
│  │  │   - VehicleStatus enum      │  │  - update_status()  │  │   │
│  │  └─────────────────────────────┘  │  - list_available() │  │   │
│  │                                   └─────────────────────┘  │   │
│  └──────────────────────────┬─────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼─────────────────────────────────┐   │
│  │                 Infrastructure Layer                        │   │
│  │                                                             │   │
│  │  ┌──────────────────────────┐  ┌────────────────────────┐  │   │
│  │  │  VehicleRepositoryImpl   │  │   MongoDB Connection    │  │   │
│  │  │  (Motor + Beanie)        │  │   (init_beanie)        │  │   │
│  │  │  VehicleDocument (ODM)   │  │   Indexes: {status,    │  │   │
│  │  │  Indexes: status+price   │  │    price} compound     │  │   │
│  │  └──────────────────────────┘  └────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │                                          │
         ▼                                          ▼
  ┌─────────────┐                        ┌──────────────────┐
  │   MongoDB   │                        │  Sales Service   │
  │  (isolated) │                        │  (HTTP client)   │
  └─────────────┘                        └──────────────────┘
```

## Component Descriptions

| Component | Layer | Responsibility |
|---|---|---|
| `vehicles router` | Presentation | Handle POST, GET, PUT for vehicle CRUD |
| `vehicle_status router` | Presentation | Handle PATCH for status lifecycle |
| `health router` | Presentation | Liveness probe (`GET /health`) |
| `OAuth2 Middleware` | Presentation/Infra | JWT Bearer token validation via python-jose |
| `CreateVehicle` | Application | Register vehicle with initial status `available` |
| `UpdateVehicle` | Application | Edit vehicle attributes; raises `NotFoundError` |
| `GetVehicle` | Application | Retrieve single vehicle; raises `NotFoundError` |
| `ListAvailableVehicles` | Application | List `available` vehicles sorted by price, paginated |
| `UpdateVehicleStatus` | Application | Transition status bidirectionally; raises `ConflictError` |
| `Vehicle` | Domain | Entity with status enum and transition guards |
| `VehicleRepository` | Domain | Abstract repository interface (zero framework deps) |
| `VehicleRepositoryImpl` | Infrastructure | Motor/Beanie async MongoDB implementation |
| `VehicleDocument` | Infrastructure | Beanie ODM document with compound index |
| `MongoDB` | External | Isolated document store (Catalog service only) |
| `Sales Service` | External | Calls `PATCH /vehicles/{id}/status` to mark vehicles sold/available |

## External Interactions

| From | To | Protocol | Purpose |
|---|---|---|---|
| Operator/Client | Catalog Service | HTTPS + Bearer JWT | CRUD operations on vehicles |
| Sales Service | Catalog Service | HTTPS + Bearer JWT | Status updates (`available ↔ sold`) |
| Catalog Service | MongoDB | TCP (Motor async) | Document persistence |
