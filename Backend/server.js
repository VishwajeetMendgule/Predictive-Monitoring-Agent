const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

io.on('connection', (socket) => {
    console.log('🟢 React UI Connected');
    socket.on('disconnect', () => console.log('🔴 React UI Disconnected'));
});

app.post('/api/telemetry', (req, res) => {
    io.emit('telemetry_update', req.body);
    res.status(200).send({ status: "Success" });
});

server.listen(3000, () => console.log(`🚀 Node.js Backend running on port 3000`));