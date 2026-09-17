# REDIS_API_RATE_LIMITER



# FastAPI Sliding Window Rate Limiter

A lightweight **API rate-limiting system built with FastAPI and Redis**, designed to control the number of requests made by individual clients within a defined time window.

The project implements a **Sliding Window Counter** approach to provide smoother and more accurate request limiting than a traditional fixed-window counter.

---

## 📌 Overview

API rate limiting is used to prevent clients from sending an excessive number of requests to an application within a short period of time.

This project provides a Redis-backed rate limiter that:

* Identifies clients using their IP address.
* Tracks request activity using Redis.
* Maintains client request history.
* Applies a sliding-window calculation.
* Supports multiple clients.
* Automatically creates records for new clients.
* Updates existing client request data.
* Rejects requests when the configured limit is exceeded.

The current configuration allows:

> **100 requests per 60-second window per client.**

---

## 🏗️ Architecture

The basic request flow is:

```text
Client Request
      │
      ▼
   FastAPI
      │
      ▼
 Identify Client IP
      │
      ▼
 Retrieve Request Count
      │
      ▼
 Create Client Request Data
      │
      ▼
 Sliding Window Counter
      │
      ├───────────────┐
      │               │
      ▼               ▼
 Existing Client    New Client
      │               │
      ▼               ▼
 Retrieve History   Create History
      │               │
      └───────┬───────┘
              ▼
      Sliding Window
        Calculation
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   Within Limit   Limit Exceeded
       │             │
       ▼             ▼
   Allow Request   HTTP 400
```

---

# 🧠 How Sliding Window Counter Works

A fixed-window rate limiter divides time into separate blocks.

For example:

```text
09:00:00 ───────── 09:01:00
```

A client could potentially send:

```text
100 requests at 09:00:59
100 requests at 09:01:00
```

This creates a boundary problem because the two groups belong to different fixed windows.

The **Sliding Window Counter** reduces this problem by considering part of the previous window along with the requests from the current window.

---

## 📊 Example

Assume:

```text
Rate Limit = 100 requests
Window     = 60 seconds
```

Suppose the current time is:

```text
150 seconds
```

The current window begins at:

```text
120 seconds
```

Therefore:

```text
Previous Window:
60 ───────────── 120

Current Window:
120 ──────────── 150
```

The previous window contributes only partially because we are already halfway through the current window.

The weighting factor is:

```text
0.5
```

If the previous window contained:

```text
80 requests
```

its weighted contribution becomes:

```text
80 × 0.5 = 40
```

If the current window contains:

```text
30 requests
```

then:

```text
Estimated Requests = 40 + 30
                   = 70
```

Since:

```text
70 < 100
```

the request is allowed.

---

# 🔢 Sliding Window Calculation

The project calculates the weighted previous-window contribution using:

```text
Previous Window Contribution
        =
Previous Requests × Window Weight
```

Then:

```text
Total Requests
        =
Previous Window Contribution
+
Current Requests
```

The resulting value is compared against the configured request limit.

If:

```text
Total Requests > Request Limit
```

the request is rejected.

---

# 🗄️ Redis Usage

Redis is used as the storage layer for client request history.

The project stores the history under:

```text
client_history
```

The stored structure contains information similar to:

```json
[
    {
        "CLIENT_IP": "192.168.1.10",
        "TOTAL_DATA": 72.5
    },
    {
        "CLIENT_IP": "192.168.1.20",
        "TOTAL_DATA": 45.0
    }
]
```

Each client has its own record.

When a request arrives, the system:

1. Extracts the client's IP address.
2. Checks whether the IP already exists.
3. Retrieves the client's previous request value.
4. Applies the sliding-window calculation.
5. Updates the client's stored value.
6. Saves the updated client history back to Redis.

---

# 👥 Multiple Client Support

The rate limiter is designed to process multiple clients.

For example:

```text
Client A → 72 requests
Client B → 35 requests
Client C → 91 requests
```

Each client is evaluated independently.

The request history is maintained as a collection of client records rather than maintaining a separate file for every client.

This makes the architecture more suitable for a centralized Redis-backed application.

---

# 🆕 New Client Handling

When a client makes a request for the first time, its IP address will not exist in the stored history.

The system creates a new record:

```json
{
    "CLIENT_IP": "192.168.1.30",
    "TOTAL_DATA": 10
}
```

The record is then added to the existing Redis history.

---

# 🔄 Existing Client Handling

If the client's IP already exists, the existing record is located.

For example:

```json
{
    "CLIENT_IP": "192.168.1.10",
    "TOTAL_DATA": 65
}
```

The previous value is used in the sliding-window calculation.

After the calculation, the value is updated and written back to Redis.

---

# ⏱️ Redis Expiration

The Redis history key is configured with an expiration time:

```text
86400 seconds
```

which is equivalent to:

```text
24 hours
```

This prevents stale client-history data from remaining indefinitely.

---

# 🚫 Rate Limit Exceeded

When the calculated request count exceeds the configured limit, the API raises an HTTP exception.

Current configuration:

```text
Request Limit: 100
Window:        60 seconds
```

Conceptually:

```text
if calculated_requests > 100:
    reject request
```

The current implementation returns:

```text
HTTP 400
API LIMIT EXCEEDED
```

---

# ⚙️ Configuration

The main rate-limiting parameters are:

| Parameter        |         Value |
| ---------------- | ------------: |
| Request Limit    |           100 |
| Window           |    60 seconds |
| Redis Expiration | 86400 seconds |
| Redis Host       |     localhost |
| Redis Port       |          6379 |

These values can be changed according to the application's requirements.

---

# 🛠️ Technology Stack

### Backend

* Python
* FastAPI

### Database / Storage

* Redis

### Supporting Technologies

* AsyncIO
* JSON
* HTTPException
* Redis asynchronous client

---

# 📁 Project Structure

A simplified structure looks like:

```text
project/
│
├── sensibull.py
│
├── helpers/
│   └── rate_limiter.py
│
├── requirements.txt
│
└── README.md
```

> The exact structure may vary depending on how the project is organized.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd <PROJECT_DIRECTORY>
```

---

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If a requirements file is not available:

```bash
pip install fastapi uvicorn redis
```

---

# 🗄️ Start Redis

The application requires a running Redis instance.

The current configuration expects Redis at:

```text
localhost:6379
```

Verify Redis is running:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

---

# ▶️ Run the FastAPI Application

Start the application using Uvicorn:

```bash
uvicorn sensibull:api_testings --reload
```

The API should then be available locally.

FastAPI's interactive API documentation can be accessed through:

```text
/docs
```

---

# 🔍 Example Request Flow

Suppose a client sends a request:

```text
Client IP: 192.168.1.10
```

The application first retrieves the client's request information.

The rate limiter then checks:

```text
Does 192.168.1.10 already exist?
```

### If No

A new client record is created.

### If Yes

The previous request data is retrieved and used in the sliding-window calculation.

The calculated request count is then compared with:

```text
100 requests
```

If the limit has not been exceeded, processing continues.

If the limit is exceeded:

```text
API LIMIT EXCEEDED
```

is returned.

---

# 🔐 Why Redis?

Redis is well suited for rate limiting because it provides:

* Fast in-memory operations
* Low-latency reads and writes
* Key expiration
* Centralized state
* Support for concurrent applications
* Better scalability than storing request state in local files

Using Redis also avoids relying on individual application-server files for client request history.

---


---

# ⚠️ Current Limitations

This project is primarily intended as a learning and implementation project.

The current implementation can be further improved for high-concurrency production environments.

In particular, multiple simultaneous requests may require atomic Redis operations to prevent race conditions when reading and updating shared request history.

For production deployment, the rate limiter should therefore be tested under concurrent load before being used as the sole protection mechanism for a critical API.

---

# 🧪 Testing

The rate limiter should be tested with:

### Single Client

```text
1 client
100 requests
```

Expected:

```text
Requests accepted
```

Then test:

```text
101+ requests
```

Expected:

```text
API LIMIT EXCEEDED
```

### Multiple Clients

Test several IP addresses simultaneously:

```text
Client A → 100 requests
Client B → 100 requests
Client C → 100 requests
```

Each client should have an independent rate-limit state.

### Window Boundary

Test requests around the transition between two 60-second windows to verify the sliding-window calculation.

---

# 🎯 Project Goal

The primary goal of this project is to understand and implement a **Redis-backed Sliding Window Counter Rate Limiter** using FastAPI.

It demonstrates how application-level request control can be implemented using:

```text
FastAPI
   +
Redis
   +
Sliding Window Algorithm
```

The project also provides practical experience with asynchronous Python, Redis state management, request tracking, and API protection.

---

* Asynchronous Python
* Backend System Design
