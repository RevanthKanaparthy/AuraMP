# AURA Project Setup Guide

This guide provides instructions on how to set up and run the AURA project locally.

## 1. Prerequisites

*   Python 3.8+
*   Node.js and npm (for the frontend)
*   PostgreSQL database

## 2. Backend Setup

### 2.1. Install Python Dependencies

Install all the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 2.2. Set Up Environment Variables

The backend requires several environment variables to be set. You can set them directly in your shell or use a `.env` file (note: you would need to add `python-dotenv` to `requirements.txt` and load it in the code).

**Important:** The application is currently failing to connect to your database because the password for the `postgres` user is incorrect. Please make sure to set the `DB_PASSWORD` environment variable to the correct password for your PostgreSQL instance.

Here are the environment variables you need to set:

| Variable        | Description                                                                                                | Default Value            |
| --------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ |
| `DB_NAME`       | The name of your PostgreSQL database.                                                                      | `mvsr_rag`               |
| `DB_USER`       | The username for your PostgreSQL database.                                                                 | `postgres`               |
| `DB_PASSWORD`   | **(Required)** The password for your PostgreSQL database user.                                             | `password`               |
| `DB_HOST`       | The host where your database is running.                                                                   | `localhost`              |
| `DB_PORT`       | The port on which your database is running.                                                                | `5432`                   |
| `SECRET_KEY`    | A strong, unique secret key for JWT token encryption. **Please change the default value for security.**      | `your-secret-key-here`   |
| `GEMINI_API_KEY`| Your API key for Google Gemini (if you are using it as the LLM provider).                                    | `None`                   |
| `LLM_PROVIDER`  | The LLM provider to use. Can be `ollama` or `gemini`.                                                      | `ollama`                 |

**Example (bash):**

```bash
export DB_PASSWORD="your_database_password"
export SECRET_KEY="a-very-strong-and-secret-key"
```

### 2.3. Run the Backend

Once the dependencies are installed and the environment variables are set, you can run the backend server:

```bash
python backend_complete.py
```

The backend will be available at `http://localhost:8000`.

## 3. Frontend Setup

### 3.1. Install Node.js Dependencies

Navigate to the `aura-frontend` directory and install the required npm packages:

```bash
cd aura-frontend
npm install
```

### 3.2. Run the Frontend

After the installation is complete, you can start the frontend development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or another port if 5173 is busy).

## 4. Troubleshooting

*   **Database Connection Error:** If you see a `password authentication failed` error, it means your `DB_PASSWORD` is incorrect. Double-check the password for the `DB_USER` in your PostgreSQL setup.
*   **401 Unauthorized Error:** If you get a `401 Unauthorized` error when accessing protected endpoints, it might be because the `SECRET_KEY` is not set correctly or is different between application restarts. Make sure to set a persistent `SECRET_KEY` in your environment.
*   **404 Not Found for `/api/documents`:** This endpoint has been disabled in the frontend as it is not implemented in the backend. This is expected behavior.
