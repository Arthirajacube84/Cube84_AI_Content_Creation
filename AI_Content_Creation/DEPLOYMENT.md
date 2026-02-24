# Deployment Guide

This guide explains how to deploy your Content Creation Assistant to the cloud using Docker. We will use **Render** (https://render.com) as it is free, easy to use, and works directly with GitHub.

## Prerequisites

1.  **GitHub Account**: You need a GitHub account to host your code.
2.  **Render Account**: Sign up at [render.com](https://render.com) using your GitHub account.

## Step 1: Push Your Code to GitHub

1.  **Initialize Git** (if you haven't already):
    ```bash
    git init
    # If this is a new repo:
    git checkout -b main
    ```

2.  **Create a `.gitignore` file** (if not already present) to exclude unnecessary files:
    
    Ensure your `.gitignore` includes:
    ```dirname
    __pycache__/
    *.pyc
    venv/
    .venv/
    .env
    .DS_Store
    ```

3.  **Commit your changes**:
    ```bash
    git add .
    git commit -m "Prepare for deployment with Docker"
    ```

4.  **Create a new repository on GitHub** and push your code:
    ```bash
    # Replace <your-username> and <your-repo-name> with your details
    git remote add origin https://github.com/<your-username>/<your-repo-name>.git
    git push -u origin main
    ```

## Step 2: Deploy on Render

1.  **Log in to Render** and click the **"New +"** button.
2.  Select **"Web Service"**.
3.  **Connect your GitHub account** (if not already connected) and selecting your repository.
4.  Configure the service:
    *   **Name**: Give your service a name (e.g., `content-creation-assistant`).
    *   **Region**: Select the region closest to you (e.g., Oregon, Frankfurt).
    *   **Branch**: `main`.
    *   **Runtime**: Select **Docker**.
    *   **Instance Type**: **Free** coverage is usually sufficient for testing.

5.  **Environment Variables**:
    *   Scroll down to the **"Advanced"** section and click **"Add Environment Variable"**.
    *   Add the following variables (even if they are in your `config.py`, it is safer to set them here):
        *   `GEMINI_API_KEY`: Your Google Gemini API Key.
        *   `TAVILY_API_KEY`: Your Tavily API Key.
        *   `MODEL_NAME`: `gemini-2.5-flash` (optional, uses default if skipped).
        *   `PORT`: `5001` (Render might set its own PORT, but our Dockerfile respects it).

6.  **Deploy**:
    *   Click **"Create Web Service"**.
    *   Render will now build your Docker image and deploy it. This may take a few minutes.

## Step 3: Verify Deployment

1.  Once the deployment is "Live", Render will provide a URL (e.g., `https://content-creation-assistant.onrender.com`).
2.  Click the URL to access your application.
3.  Test the chat functionality to ensure the API keys are working correctly.


## Optional: Test Locally with Docker

Before deploying to Render, you can verify your Docker setup works locally:

1.  **Build the Docker image**:
    ```bash
    docker build -t content-creation .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 5001:5001 -e GEMINI_API_KEY="your-key" content-creation
    ```
    (Replace `your-key` with your actual API key if needed, or create a `.env` file and use `--env-file .env`)

3.  **Access the app**:
    Open your browser to `http://localhost:5001`.

## Debugging

If the deployment fails:
1.  Check the **Logs** tab in Render. It will show you exactly what happened during the build or runtime.
2.  Common issues:
    *   **Missing API Keys**: Ensure you added environment variables in Render.
    *   **Port Issues**: The application logs should say something like `Listening at: http://0.0.0.0:xxxx`.


---

**Note**: The Free Tier on Render spins down after 15 minutes of inactivity. The first request after a while might take ~30-60 seconds to load. This is normal for the free plan.
