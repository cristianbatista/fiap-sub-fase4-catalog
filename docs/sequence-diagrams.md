# Sequence Diagrams — Catalog Service

**Date**: 2026-05-08

## 1. Register Vehicle (`POST /vehicles`)

```
Operator          vehicles router      CreateVehicle       VehicleRepositoryImpl    MongoDB
   │                    │                   │                       │                  │
   │ POST /vehicles     │                   │                       │                  │
   │ Bearer token       │                   │                       │                  │
   │───────────────────►│                   │                       │                  │
   │                    │ validate JWT       │                       │                  │
   │                    │ (OAuth2 middleware)│                       │                  │
   │                    │                   │                       │                  │
   │                    │ execute(brand,     │                       │                  │
   │                    │  model, year,      │                       │                  │
   │                    │  color, price)     │                       │                  │
   │                    │──────────────────►│                       │                  │
   │                    │                   │ Vehicle(id=uuid,       │                  │
   │                    │                   │  status=available)     │                  │
   │                    │                   │ repo.save(vehicle)     │                  │
   │                    │                   │──────────────────────►│                  │
   │                    │                   │                       │ insert document   │
   │                    │                   │                       │─────────────────►│
   │                    │                   │                       │◄─────────────────│
   │                    │                   │◄──────────────────────│                  │
   │                    │◄──────────────────│                       │                  │
   │ 201 Created        │                   │                       │                  │
   │ {id, brand, ...}   │                   │                       │                  │
   │◄───────────────────│                   │                       │                  │

[Failure: missing field]  → 422 Unprocessable Entity (before use case is called)
[Failure: invalid JWT]    → 401 Unauthorized (OAuth2 middleware rejects)
```

## 2. Update Vehicle Status: available → sold (`PATCH /vehicles/{id}/status`)

```
Sales Service     vehicle_status router   UpdateVehicleStatus    VehicleRepositoryImpl    MongoDB
   │                      │                     │                       │                  │
   │ PATCH /{id}/status   │                     │                       │                  │
   │ {"status": "sold"}   │                     │                       │                  │
   │ Bearer token         │                     │                       │                  │
   │─────────────────────►│                     │                       │                  │
   │                      │ validate JWT         │                       │                  │
   │                      │──────────────────────────────────────────────────────────────  │
   │                      │ execute(id, sold)    │                       │                  │
   │                      │────────────────────►│                       │                  │
   │                      │                     │ find_by_id(id)         │                  │
   │                      │                     │──────────────────────►│                  │
   │                      │                     │                       │ find {_id: id}    │
   │                      │                     │                       │─────────────────►│
   │                      │                     │                       │◄─────────────────│
   │                      │                     │◄──────────────────────│ Vehicle(available)│
   │                      │                     │                       │                  │
   │                      │                     │ vehicle.status ≠ sold  │                  │
   │                      │                     │ (no conflict)          │                  │
   │                      │                     │ update_status(id, sold)│                  │
   │                      │                     │──────────────────────►│                  │
   │                      │                     │                       │ set {status:sold} │
   │                      │                     │                       │─────────────────►│
   │                      │                     │                       │◄─────────────────│
   │                      │                     │◄──────────────────────│ Vehicle(sold)     │
   │                      │◄────────────────────│                       │                  │
   │ 200 OK               │                     │                       │                  │
   │ {id, status, upd_at} │                     │                       │                  │
   │◄─────────────────────│                     │                       │                  │

[Failure: vehicle not found]           → 404 Not Found
[Failure: vehicle already sold]        → 409 Conflict (ConflictError)
[Failure: invalid status value]        → 422 Unprocessable Entity
[Failure: invalid JWT]                 → 401 Unauthorized
```

## 3. Update Vehicle Status: sold → available (`PATCH /vehicles/{id}/status`)

```
Sales Service     vehicle_status router   UpdateVehicleStatus    VehicleRepositoryImpl    MongoDB
   │                      │                     │                       │                  │
   │ PATCH /{id}/status   │                     │                       │                  │
   │ {"status":"available"}│                    │                       │                  │
   │ Bearer token         │                     │                       │                  │
   │─────────────────────►│                     │                       │                  │
   │                      │ validate JWT         │                       │                  │
   │                      │ execute(id,available)│                       │                  │
   │                      │────────────────────►│                       │                  │
   │                      │                     │ find_by_id(id)         │                  │
   │                      │                     │──────────────────────►│─────────────────►│
   │                      │                     │◄──────────────────────│ Vehicle(sold)     │
   │                      │                     │ vehicle.status ≠ avail │                  │
   │                      │                     │ (no conflict)          │                  │
   │                      │                     │ update_status(available)│                 │
   │                      │                     │──────────────────────►│─────────────────►│
   │                      │                     │◄──────────────────────│Vehicle(available) │
   │                      │◄────────────────────│                       │                  │
   │ 200 OK               │                     │                       │                  │
   │ {id,"available",upd} │                     │                       │                  │
   │◄─────────────────────│                     │                       │                  │

[Failure: vehicle already available]   → 409 Conflict (ConflictError)
```
