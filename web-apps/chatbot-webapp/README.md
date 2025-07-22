# Kognia Tactical Visualization & Chatbot Demo

This project demonstrates visualizing football match data in 3D and interacting with an LLM chatbot for tactical insights.

## Requirements

- Python 3.8+
- Node.js and npm
- A Gemini API Key

## How to Run

1.  **Setup Backend:**
    - Navigate to `kognia_chatbot_backend`.
    - Create a file named `.env` and add your API key: `GEMINI_API_KEY=YOUR_API_KEY_HERE`
    - Run `npm install` in the `kognia_chatbot_backend` directory.

2.  **Run Backend Server:**
    - In a terminal, navigate to `kognia_chatbot_backend`.
    - Run `node server.js`.
    - Keep this terminal running.

3.  **Run Frontend Server:**
    - Open a **new** terminal.
    - Navigate to the **main project directory** (where this README is).
    - Run `python -m http.server 8000` (or another port like 8080 if 8000 is busy).
    - Keep this terminal running.

4.  **Access Demo:**
    - Open your web browser to: `http://localhost:8000/kognia_3d_viz/` (use the port from step 3 if different).