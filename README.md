# GrocerTrack - Technical Assessment Submission

This repository contains the complete submission for the technical assessment, which includes two separate projects: a Django backend for a grocery management system and a Next.js frontend for an asset management UI.

---

## 🚀 Project Overview

This monorepo is structured into two main parts:

1.  **`backend/`**: A powerful RESTful API built with Django and Django REST Framework to manage a multi-branch grocery company. It handles data for groceries, items, suppliers, and daily income, featuring a robust authentication and permission system. It also integrates a Neo4j graph database to model relationships.
2.  **`frontend/`**: A responsive and interactive user interface built with Next.js and TypeScript, based on a Figma design. It allows users to manage a list of program assets.

---

## 🛠️ Tech Stack

| Category          | Technologies                                                    |
| ----------------- | --------------------------------------------------------------- |
| **Backend** | Django, Django REST Framework, Python                           |
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui             |
| **Databases** | PostgreSQL (Relational), Neo4j (Graph)                          |
| **Containerization**| Docker, Docker Compose                                          |
| **Authentication**| JWT (JSON Web Tokens)                                           |

---

## ✨ Features

### Backend: Grocery Management System

| User Role | Feature                                           | Status        |
| --------- | ------------------------------------------------- |---------------|
| **Admin** | ✅ Create & Manage Grocery Branches               | Implemented   |
| **Admin** | ✅ Create & Manage Supplier Accounts              | Implemented   |
| **Admin** | ✅ Manage Items for any Grocery                   | Implemented   |
| **Admin** | ✅ View Daily Income for all Groceries            | Implemented   |
| **Supplier** | ✅ Add Items to their **own** Grocery             | Implemented |
| **Supplier** | ✅ Add Daily Income for their **own** Grocery     | Implemented & |
| **Supplier** | ✅ Read Items from other Groceries (Read-Only)    | Implemented   |
| **Security** | ✅ Role-Based Permissions (Admin vs. Supplier)    | Implemented  |
| **Security** | ✅ Soft Delete on all models                      | Implemented   |

### Frontend: Asset Management UI

| Feature                          | Status      |
| -------------------------------- |-------------|
| ✅ Replicate Figma Design          | Implemented |
| ✅ Add/Delete Assets to a Temp List| Implemented |
| ✅ Prevent Duplicate Assets        | Implemented |
| ✅ Submit Assets to Final Table    | Implemented |

---

## 🏁 Getting Started (Local Development)

Follow these steps to get the entire project running locally.

### Prerequisites

* **Docker** and **Docker Compose** must be installed and running on your machine.

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone [(https://github.com/Akentar2001/AhmadKontar-Technical-Assessment.git)]
    cd your-repository-name
    ```

2.  **Configure Environment Variables**
    This project uses a central `.env` file in the root directory. Rename the example file to create your own configuration:
    ```bash
    mv .env.example .env
    ```
    Now, open the `.env` file and fill in your desired passwords and the Django `SECRET_KEY`.

3.  **Build and Run with Docker Compose**
    From the root directory, run the following command. This will build the images and start all services (backend, frontend, postgres, neo4j).
    ```bash
    docker-compose up --build
    ```
    *Wait for all services to start. The `backend` service might restart a few times while waiting for the databases, which is normal.*

4.  **Initialize the Backend Database**
    While the containers are running in the first terminal, **open a new terminal** and run these commands to set up the database and create your admin user:

    ```bash
    # Apply database migrations
    docker-compose exec backend python manage.py migrate

    # Create your admin account
    docker-compose exec backend python manage.py createsuperuser

    # Create the 'Suppliers' user group
    docker-compose exec backend python manage.py shell -c "from django.contrib.auth.models import Group; Group.objects.get_or_create(name='Suppliers')"
    ```

### Accessing the Services

* **Frontend Application**: [http://localhost:3000](http://localhost:3000)
* **Backend API**: [http://localhost:8000/api/](http://localhost:8000/api/)
* **Django Admin Panel**: [http://localhost:8000/admin](http://localhost:8000/admin)
* **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (User: `neo4j`, Password: the one you set in `.env`)

---

## 🧪 Running Tests

The backend includes a comprehensive test suite to verify the core business logic and security permissions.

To run the tests, execute the following command from your terminal in the root directory:
```bash
docker-compose exec backend python manage.py test api
