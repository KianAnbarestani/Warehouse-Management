
# Warehouse Management System (WMS)

A comprehensive Warehouse Management System (WMS) developed using Django and Django REST Framework (DRF). This system facilitates efficient inventory management by implementing FIFO (First-In-First-Out) and Weighted Mean cost calculation methods. It allows for the creation and management of wares, recording of input and output transactions, and accurate inventory valuation.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [API Documentation](#api-documentation)
  - [Endpoints](#endpoints)
    - [1. Create a Ware](#1-create-a-ware)
    - [2. Input Inventory](#2-input-inventory)
    - [3. Output Inventory](#3-output-inventory)
    - [4. Inventory Valuation](#4-inventory-valuation)
- [Error Handling](#error-handling)
- [Project Structure](#project-structure)
- [Contact](#contact)

## Features

- **Ware Management:** Create and manage wares with unique names and specified cost calculation methods (FIFO or Weighted Mean).
- **Inventory Transactions:**
  - **Input Transactions:** Record incoming inventory with quantity and purchase price.
  - **Output Transactions:** Record outgoing inventory based on FIFO or Weighted Mean calculations.
- **Inventory Valuation:** Evaluate total inventory value and quantity in stock for each ware.
- **Data Integrity:** Enforce unique ware names to prevent duplicate entries.
- **Comprehensive Testing:** Automated test cases ensure system reliability and correctness.

## Technologies Used

- **Backend:**
  - [Django](https://www.djangoproject.com/) - High-level Python Web framework.
  - [Django REST Framework (DRF)](https://www.django-rest-framework.org/) - Toolkit for building Web APIs.
- **Database:**
  - [SQLite](https://www.sqlite.org/index.html) - Lightweight disk-based database.
- **Others:**
  - [Python 3.11.7](https://www.python.org/) - Programming language.

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.11.7 or higher**
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **Virtual Environment Tool** (optional but recommended)

## Installation

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/warehouse-management.git
cd warehouse-management
```

### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment helps manage project dependencies without affecting global Python packages.

```bash
# Using venv
python -m venv env

# Activate the virtual environment
# For Windows:
env\Scripts\Activate

# For Unix or MacOS:
source env/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

**Note:** If `requirements.txt` is not present, you can manually install the necessary packages:

```bash
pip install django djangorestframework
```

### 4. Apply Migrations

Set up the SQLite database and create necessary tables.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Optional)

Creating a superuser allows you to access the Django admin interface.

```bash
python manage.py createsuperuser
```

Follow the prompts to set up the superuser credentials.

## Running the Application

Start the Django development server to run the application locally.

```bash
python manage.py runserver
```

The application will be accessible at `http://localhost:8000/`.

## Running Tests

Ensure that all functionalities work as expected by running the automated test suite.

```bash
python manage.py test inventory
```

## API Documentation

### Base URL

```
http://localhost:8000/api/
```
