
# fastapi_task
# 🚀 Kubernetes Application Observability Dashboard

## 📌 Overview

This project is a **Kubernetes-based Observability Dashboard** that provides a **single unified view** of:

* 📊 Live Kubernetes resource usage (CPU, Memory)
* 📦 Application & Microservice mapping
* 📁 Repository & tech stack details
* ☁️ Cloud migration & governance status

The system integrates **Kubernetes cluster data**, **Excel/SharePoint metadata**, and **migration roadmap data** into a centralized UI.

---

## 🎯 Problem Statement

Organizations often struggle with:

* ❌ Lack of visibility into Kubernetes resource usage
* ❌ No mapping between namespaces and applications
* ❌ Disconnected migration tracking (Excel vs actual infra)
* ❌ Difficulty validating governance tags (labels)

👉 This project solves these problems by creating a **single pane dashboard**.

---

## 🏗️ Architecture

```
                +----------------------+
                |   Kubernetes Cluster |
                | (Pods, Metrics API)  |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |   Node.js Backend    |
                |  (controller.js)     |
                +----------+-----------+
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
+---------------------+          +------------------------+
| Excel / SharePoint  |          | Migration Roadmap Data |
| (App Metadata)      |          | (Governance)           |
+---------------------+          +------------------------+
                           |
                           v
                +----------------------+
                |    Frontend (UI)     |
                |   Konsole Dashboard  |
                +----------------------+
```

---

## ⚙️ Features

### 🔹 Kubernetes Integration

* Fetch pods by namespace
* CPU & Memory usage aggregation
* Container-level insights

### 🔹 Application Mapping

* Namespace → Application mapping
* Microservices identification
* Repo URL & tech stack tracking

### 🔹 Migration Dashboard

* In Scope / Out of Scope tracking
* Migration progress visibility
* Hosting & strategy details

### 🔹 Governance Validation

* Label validation:

  * `dx-id`
  * `dx-environment`
  * `dx-is-production`

---

## 🧰 Tech Stack

| Layer       | Technology             |
| ----------- | ---------------------- |
| Backend     | Node.js (Express)      |
| Frontend    | HTML / JS (Konsole UI) |
| Kubernetes  | K8s API / kubectl      |
| Data Source | Excel / SharePoint     |
| Optional DB | MongoDB / PostgreSQL   |

---

## 📂 Project Structure

```
project-root/
│
├── backend/
│   ├── controller.js
│   ├── kube/
│   │   └── kubeset.js
│   └── routes/
│
├── frontend/
│   ├── index.html
│   ├── dashboard.js
│
├── data/
│   ├── app_metadata.xlsx
│   ├── migration_roadmap.xlsx
│
├── README.md
└── package.json
```

---

## 🔄 Data Flow

1. User selects a **namespace** from UI

2. Backend fetches pod data:

   ```bash
   kubectl get pods -n <namespace>
   ```

3. Backend calculates:

   * CPU usage
   * Memory usage

4. System maps namespace to:

   * Application
   * Microservices
   * Repo details

5. Migration data is added:

   * Scope
   * Status
   * Ownership

6. UI displays enriched data

---

## 🚀 Getting Started

### 1️⃣ Prerequisites

* Node.js (v16+)
* Kubernetes cluster access
* kubectl configured
* Excel / SharePoint data

---

### 2️⃣ Clone Repository

```bash
git clone <repo-url>
cd project-root
```

---

### 3️⃣ Install Dependencies

```bash
npm install
```

---

### 4️⃣ Configure Kubernetes

```bash
kubectl config get-contexts
kubectl config use-context <your-cluster>
```

---

### 5️⃣ Run Backend

```bash
node server.js
```

---

### 6️⃣ Open Frontend

Open:

```
http://localhost:3000
```

---

## 📊 API Example

### Get Namespace Data

```
GET /api/namespace/:name
```

### Response

```json
{
  "namespace": "easymail-dev",
  "cpu": 45,
  "memory": 60,
  "pods": [],
  "application": "Easymail",
  "microservices": ["frontend", "backend"]
}
```

---

## ⚠️ Common Issues

### ❌ Empty Dashboard

* Namespace not selected
* No pods in namespace
* Backend API not returning data

### ❌ Data Not Matching

* Namespace mismatch (Excel vs K8s)

### ❌ Label Missing

Check:

```bash
kubectl get ns --show-labels
```

---

## 🔥 Future Enhancements

* ✅ Replace Excel with Database (MongoDB/Postgres)
* ✅ Multi-cluster support
* ✅ Real-time monitoring (WebSockets)
* ✅ RBAC-based access control
* ✅ Alerts for high CPU/Memory usage
