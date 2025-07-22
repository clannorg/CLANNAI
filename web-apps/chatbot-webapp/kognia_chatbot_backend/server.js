// kognia_chatbot_backend/server.js
import express from 'express';
import dotenv from 'dotenv';
import fetch from 'node-fetch'; // Using v2 syntax
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables (API key)
dotenv.config();

// ES Module equivalents for __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3000; // Use port 3000 unless specified

// --- Load Game Stats ---
let gameStats = {};
const statsFilePath = path.join(__dirname, 'team_stats.json');
try {
    const statsData = fs.readFileSync(statsFilePath, 'utf8');
    gameStats = JSON.parse(statsData);
    console.log("Successfully loaded team_stats.json");
} catch (err) {
    console.error("Error reading or parsing team_stats.json:", err);
    // Decide if you want the server to run without stats or exit
    // process.exit(1);
}
// --------------------

// --- NEW: Load Additional Insights ---
let additionalInsights = "";
// Construct the absolute path from the project root (__dirname here is kognia_chatbot_backend)
const insightsFilePath = path.join(__dirname, '..', 'llm_insights', 'gemini.md');
try {
    additionalInsights = fs.readFileSync(insightsFilePath, 'utf8');
    console.log("Successfully loaded insights from gemini.md");
} catch (err) {
    console.warn("Warning: Could not read insights file (gemini.md):", err.message);
    // Proceed without additional insights if file is missing or unreadable
}
// ---------------------------------

// --- Middleware ---
app.use(cors()); // Enable CORS for requests from your frontend (running on a different port)
app.use(express.json()); // Parse JSON request bodies
// --------------------

// --- API Endpoint ---
app.post('/api/chat', async (req, res) => {
    const userMessage = req.body?.message;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!userMessage) {
        return res.status(400).json({ error: 'No message provided' });
    }
    if (!apiKey) {
        console.error("GEMINI_API_KEY not found in .env file");
        return res.status(500).json({ error: 'Server configuration error: API key missing' });
    }

    // --- Construct Prompt for Gemini ---
    // const systemPrompt = `You are a helpful football tactics analyst. You are provided with game statistics (JSON) and a pre-written analysis document (Markdown) for the Chelsea FC vs West Ham match. Answer the user\'s questions by synthesizing information from BOTH sources. \\n- Use the insights from the analysis document to provide richer explanations, summaries, and context where relevant.\\n- Ensure your answers are consistent with the raw statistics.\\n- If the analysis document directly addresses the user\'s query, prioritize using that information.\\n- Be concise but informative.`; // Old Prompt
    const systemPrompt = `You are Kognia, an expert football tactics analyst. You have access to detailed game statistics (JSON) and contextual notes (Markdown) for the Chelsea FC vs West Ham match. Answer the user's questions based on all available information.\n- Provide insightful analysis drawing from both the stats and the contextual notes.\n- Frame your answers naturally, as if deriving insights directly, without mentioning the source of the contextual notes.\n- Ensure your analysis is consistent with the raw statistical data.\n- Be concise yet comprehensive.`; // New Implicit Prompt

    // Incorporate additional insights if available, but without explicit heading
    // const insightsSection = additionalInsights \
    //    ? `\\n\\nConsider these previous insights:\\n\\`\\`\\`markdown\\n${additionalInsights}\\n\\`\\`\\`\\n` \
    //    : ""; // Old way with heading

    const fullPrompt = `\n${systemPrompt}\n\nHere are the game statistics:\n\`\`\`json\n${JSON.stringify(gameStats, null, 2)}\n\`\`\`\n${additionalInsights ? `\\n\\n${additionalInsights}\\n\\n` : ''}User Question: ${userMessage}\n`; // Appended insights without heading
    // ---------------------------------

    // --- Call Google Gemini API ---
    // IMPORTANT: Replace with the correct endpoint and request format for the specific Gemini model you want to use.
    // This is a simplified example for the generative-language API (check latest docs).
    // const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=${apiKey}`; // Old Model
    const modelName = 'gemini-1.5-pro-latest'; // Back to the working model
    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${apiKey}`; // Use variable

    try {
        console.log(`Sending request to Gemini (${modelName})...`); // Log model name
        const geminiResponse = await fetch(geminiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{ parts: [{ text: fullPrompt }] }]
                // Add generationConfig here if needed (temperature, max tokens, etc.)
            }),
        });

        if (!geminiResponse.ok) {
            const errorBody = await geminiResponse.text(); // Read error text
            console.error(`Gemini API error: ${geminiResponse.status} ${geminiResponse.statusText}`, errorBody);
            throw new Error(`API request failed with status ${geminiResponse.status}: ${errorBody}`);
        }

        const data = await geminiResponse.json();
        console.log("Received response from Gemini.");

        // --- Extract Response ---
        // Adjust based on the actual Gemini API response structure
        const botResponse = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Sorry, I couldn't get a response.";
        // ------------------------

        // res.json({ reply: botResponse }); // Old response
        res.json({ reply: botResponse, model: modelName }); // Response with correct model name

    } catch (error) {
        console.error('Error calling Gemini API:', error);
        res.status(500).json({ error: 'Failed to get response from AI model' });
    }
    // ---------------------------
});
// --------------------

// --- Start Server ---
app.listen(port, () => {
    console.log(`Chatbot backend server listening on http://localhost:${port}`);
});
// --------------------