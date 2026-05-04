const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');
const readline = require('readline');
const { spawn } = require('child_process');

const app = express();
app.use(express.json());
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

// ==========================================
// Connect to SQLite Database Directly
// ==========================================
const dbPath = 'D:/Preditictive Agent/logs.db'; 
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) console.error("Database connection error:", err.message);
    else console.log("📦 Connected to SQLite Database");
});

io.on('connection', (socket) => {
    console.log('🟢 React UI Connected');
});

// 1. LIVE FEED ENDPOINT
app.post('/api/telemetry', (req, res) => {
    io.emit('telemetry_update', req.body);
    res.status(200).send({ status: "Success" });
});

// 2. METRICS EXPLORER ENDPOINT (Native Node.js SQLite)
app.get('/api/history', (req, res) => {
    const searchDate = req.query.date; 
    
    // Search the database directly from Node!
    const query = `SELECT * FROM server_metrics WHERE timestamp LIKE ? ORDER BY cpu DESC LIMIT 50`;
    
    db.all(query, [`%${searchDate}%`], (err, rows) => {
        if (err) {
            console.error("DB Error:", err);
            return res.status(500).json({ error: err.message });
        }
        res.json(rows);
    });
});

// 3. TEXT LOG EXPLORER ENDPOINT
app.get('/api/logs', async (req, res) => {
    const { date, level, component } = req.query;
    const logFilePath = 'D:/Preditictive Agent/app_logs_test.log'; 

    if (!fs.existsSync(logFilePath)) return res.json([]); 

    const matchedLogs = [];
    const fileStream = fs.createReadStream(logFilePath);
    const rl = readline.createInterface({ input: fileStream, crlfDelay: Infinity });

    for await (const line of rl) {
        if (!line.trim()) continue;
        try {
            const log = JSON.parse(line);
            if (date && !log.timestamp.includes(date)) continue;
            if (level && level !== 'All Levels') {
                if (level === 'ERROR & CRITICAL' && !['ERROR', 'CRITICAL'].includes(log.level)) continue;
                if (level === 'WARNING' && log.level !== 'WARN') continue;
                if (level === 'INFO' && log.level !== 'INFO') continue;
                if (level === 'DEBUG' && log.level !== 'DEBUG') continue;
            }
            if (component) {
                const searchStr = component.toLowerCase();
                if (!log.component.toLowerCase().includes(searchStr) && !log.message.toLowerCase().includes(searchStr)) continue;
            }
            const timeOnly = log.timestamp.split('T')[1].replace('Z', '');
            matchedLogs.push({ time: timeOnly, level: log.level, component: log.component, message: log.message });
        } catch (e) {}
    }
    res.json(matchedLogs.reverse().slice(0, 100));
});

// 4. AI CHAT ENDPOINT
app.post('/chat', (req, res) => {
    const { message, sessionId } = req.body;
    
    const pythonProcess = spawn('python', ['chat_runner.py'], {
        cwd: 'D:/Preditictive Agent',
        stdio: ['pipe', 'pipe', 'pipe']
    });

    pythonProcess.stdin.write(JSON.stringify({ message, sessionId }));
    pythonProcess.stdin.end();

    let output = '';
    pythonProcess.stdout.on('data', (data) => {
        output += data.toString();
    });
    
    pythonProcess.stderr.on('data', (data) => {
        console.error('Python stderr:', data.toString());
    });
    
    pythonProcess.on('close', (code) => {
        if (code === 0) {
            // Only respond with the final line to avoid startup prints affecting the result
            const lines = output.trim().split(/\r?\n/).filter(Boolean);
            const responseText = lines.length ? lines[lines.length - 1] : '';
            res.json({ response: responseText });
        } else {
            res.status(500).json({ error: 'Failed to process chat' });
        }
    });
});

server.listen(3000, () => console.log(`🚀 Node.js Backend running on port 3000`));