# Customers RESTful API Service

[![CI Build](https://github.com/CSCI-GA-2820-FA25-003/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA25-003/customers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA25-003/customers/graph/badge.svg?token=2FYGK51XFT)](https://codecov.io/gh/CSCI-GA-2820-FA25-003/customers)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-red.svg)](https://www.python.org/)
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/CSCI-GA-2820-FA25-003/customers)

## Overview

This project is a **Flask-based RESTful API** for managing customer data in an e-commerce application.  
It allows clients to **create, read, update, delete (CRUD) and list** customer records and supports filtering by first name, last name, and address.

## Getting Started

Follow these steps to clone the repository, start the development environment, and run the API.

#### 1 Clone the repository
```bash
git clone https://github.com/CSCI-GA-2820-FA25-003/customers.git
cd customers
```

#### 2 Open in VS Code Dev Container
We strongly recommend running this project in a **Dev Container** for consistent dependencies.
Make sure you have installed:

- [Docker](https://docs.docker.com/get-docker/)
- [VS Code](https://code.visualstudio.com/)
- [Remote - Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

Steps:
1.Open the project folder in VS Code
2.When prompted, click "Reopen in Container"
3.VS Code will automatically build and start the dev container (this may take a few minutes the first time)

#### 3 Run the Flask Application

Inside the dev container

```bash
honcho start
```
If successful, the server should start at:
```
http://localhost:8080/
```

## API Endpoints & Example  `curl` Calls

Below are example commands you can copy and paste to test the API directly from your terminal.
These examples assume the server is running locally on `http://localhost:8080`.

##### Create a new customer
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "last_name": "Doe", "address": "123 Main Street, Anytown, USA"}' \
  http://localhost:8080/customers
```

##### Read a customer by ID
Replace `<VALID-ID-HERE>` with a valid customer ID:
```bash
curl -X GET http://localhost:8080/customers/<VALID-ID-HERE>
```

##### Update a customer by ID
Replace `<VALID-ID-HERE>` with a real customer ID returned from the list or create endpoint.
```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Jane", "last_name": "Doe", "address": "456 Elm Street, Cityville, USA"}' \
  http://localhost:8080/customers/<VALID-ID-HERE>
```

##### Delete a customer by ID
Replace `<VALID-ID-HERE>` with a valid customer ID:
```bash
curl -X DELETE http://localhost:8080/customers/<VALID-ID-HERE>
```

##### Retrieve all customers
```bash
curl -X GET http://localhost:8080/customers
```

##### Filter customers by first name

Replace `<FIRST_NAME>` with the customer's first name you want to search for:
```bash
curl -X GET "http://localhost:8080/customers?first_name=<FIRST_NAME>"
```

##### Filter customers by last name

Replace `<LAST_NAME>` with the customer's last name you want to search for:
```bash
curl -X GET "http://localhost:8080/customers?last_name=<LAST_NAME>"
```

##### Filter customers by address

Replace `<ADDRESS>` with the customer's address you want to search for:
```bash
curl -X GET "http://localhost:8080/customers?address=<ADDRESS>"
```

##### Filter customers by first name and last name
Replace `<FIRST_NAME>` and `<LAST_NAME>` with valid values:
```bash
curl -X GET "http://localhost:8080/customers?first_name=<FIRST_NAME>&last_name=<LAST_NAME>"
```

##### Filter customers by first name and address
Replace `<FIRST_NAME>` and `<ADDRESS>` with valid values:
```bash
curl -X GET "http://localhost:8080/customers?first_name=<FIRST_NAME>&address=<ADDRESS>"
```

##### Filter customers by last name and address
Replace `<LAST_NAME>` and `<ADDRESS>` with valid values:
```bash
curl -X GET "http://localhost:8080/customers?last_name=<LAST_NAME>&address=<ADDRESS>"
```

##### Filter customers by first name, last name, and address
Replace `<FIRST_NAME>`, `<LAST_NAME>,` and `<ADDRESS>` with valid values:
```bash
curl -X GET "http://localhost:8080/customers?first_name=<FIRST_NAME>&last_name=<LAST_NAME>&address=<ADDRESS>"
```

## Project Structure

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
