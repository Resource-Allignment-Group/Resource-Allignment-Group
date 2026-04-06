# MAFES Equipment Management System

A web-based inventory, tracking, and reservation system for the Maine Agricultural and Forest Experiment Station (MAFES) at the University of Maine. This application replaces MAFES's existing spreadsheet-based workflow, allowing staff and students to search, reserve, and manage agricultural and forestry equipment across all six MAFES research farms.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)
- [Project Team](#project-team)

---

## Getting Started

Clone the repository:

```
git clone https://github.com/Resource-Allignment-Group/Resource-Allignment-Group.git
```

The application has two components that must be running simultaneously: the **Flask backend** and the **React frontend**. Follow the steps below to get both running locally.

---

## Backend Setup

> Requires Python 3.x

1. Create a virtual environment:
   ```
   py -m venv venv
   ```
2. Activate the virtual environment:
   ```
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   py -m pip install -r requirements.txt
   ```
4. Start the backend server:
   ```
   cd .\backend
   py .\main.py
   ```

---

## Frontend Setup

> Requires Node.js and npm

1. Open a new terminal and navigate to the frontend directory:
   ```
   cd .\frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

---

## Docker Deployment

You can also run the application on Docker.

### Building and Running Locally

```
docker-compose build --no-cache
docker-compose up
```

### Saving and Transferring the Image

After the container is running, commit and export the image:

```
docker commit <container_id_or_name> <new_image_name>:<tag>
docker save -o flask:prod.tar flask:prod
```

Transfer the image to the remote server:

```
scp <path_to_tar_file> opc@158.101.111.115:/home/opc/
ssh opc@158.101.111.115
```

### Frontend Production Build

To build and run the frontend production container independently:

```
docker build -f frontend/Dockerfile.prod -t rag-frontend:prod frontend
docker rm -f react_app
docker run -d --name react_app -p 3000:80 rag-frontend:prod
```

---

## Environment Configuration

Before running the application, create a `.env` file in the root of the project and populate it with the following values:

```env
# MongoDB
DATABASE_URI=your_mongodb_connection_string

# Flask
FLASK_SECRET_KEY=your_secret_key

# Email (used for notifications and password reset emails)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# Debugging
FLASK_DEBUG=TRUE or FALSE

# Frontend
REACT_APP_BACKEND_API_BASE=url_for_api_access
```

> **Note:** The email credentials are used to send system notifications (equipment requests, account approvals, damage reports, etc.) and password reset links. A dedicated Gmail account is recommended. You will need to generate a [Gmail App Password](https://support.google.com/accounts/answer/185833) rather than using your standard account password.

---

## Testing

The application uses a combination of testing frameworks for the frontent and backend directories. On the backend, testing is implemented with Python, using PyTest and psutil. These cover the unit, integration, and system testing of the backend endpoints and database interactions. On the frontend, testing is handled using Jest and React Testing Library for validating component rendering, user interactions, and application behavior in a simulated browser environment.

# Backend Tests

To run all backend tests with coverage, execute the following command from the root directory of the project:

```
pytest backend/tests --benchmark-save=none
```

This will run all tests in the backend module.

# Frontend Tests

To run all of the frontend tests, navigate to the frontend directory and run:

```
npm test -- --watchAll=false
```

This will execute all React component and page tests using Jest and React Testing Library.

---

## Project Team

| Name                | Role      |
| ------------------- | --------- |
| Bradan Craig        | Developer |
| Drew Marecek        | Developer |
| McKade Wing         | Developer |
| Theodore Morin      | Developer |
| Tyler Messerschmidt | Client    |
| Lee Hecker          | Client    |
