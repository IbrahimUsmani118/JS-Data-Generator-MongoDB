const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// Data storage file
const DATA_FILE = path.join(__dirname, 'data.json');

// In-memory data store (fallback)
let dataStore = {};

// Load data from file on startup
async function loadData() {
    try {
        const data = await fs.readFile(DATA_FILE, 'utf8');
        dataStore = JSON.parse(data);
        console.log('Data loaded from file');
    } catch (error) {
        console.log('No existing data file found, starting with empty store');
        dataStore = {};
    }
}

// Save data to file
async function saveData() {
    try {
        await fs.writeFile(DATA_FILE, JSON.stringify(dataStore, null, 2));
        console.log('Data saved to file');
    } catch (error) {
        console.error('Error saving data:', error);
    }
}

// API Routes

// GET /api/data - Get all data
app.get('/api/data', (req, res) => {
    try {
        const dataArray = Object.entries(dataStore).map(([key, value]) => ({
            key,
            ...value
        }));
        res.json({
            success: true,
            data: dataArray,
            count: dataArray.length
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to retrieve data'
        });
    }
});

// POST /api/data - Add new data
app.post('/api/data', async (req, res) => {
    try {
        const { key, value } = req.body;
        
        if (!key || !value) {
            return res.status(400).json({
                success: false,
                error: 'Key and value are required'
            });
        }

        // Validate key (no special characters, max 50 chars)
        if (key.length > 50 || /[<>:"/\\|?*]/.test(key)) {
            return res.status(400).json({
                success: false,
                error: 'Invalid key format'
            });
        }

        // Validate value (max 1000 chars)
        if (value.length > 1000) {
            return res.status(400).json({
                success: false,
                error: 'Value too long (max 1000 characters)'
            });
        }

        const timestamp = new Date().toISOString();
        const id = Date.now().toString(36) + Math.random().toString(36).substr(2);

        dataStore[key] = {
            value,
            timestamp,
            id
        };

        await saveData();

        res.status(201).json({
            success: true,
            data: {
                key,
                value,
                timestamp,
                id
            },
            message: 'Data added successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to add data'
        });
    }
});

// PUT /api/data/:key - Update data
app.put('/api/data/:key', async (req, res) => {
    try {
        const { key } = req.params;
        const { value } = req.body;

        if (!value) {
            return res.status(400).json({
                success: false,
                error: 'Value is required'
            });
        }

        if (!dataStore[key]) {
            return res.status(404).json({
                success: false,
                error: 'Data not found'
            });
        }

        // Validate value (max 1000 chars)
        if (value.length > 1000) {
            return res.status(400).json({
                success: false,
                error: 'Value too long (max 1000 characters)'
            });
        }

        dataStore[key] = {
            ...dataStore[key],
            value,
            lastModified: new Date().toISOString()
        };

        await saveData();

        res.json({
            success: true,
            data: dataStore[key],
            message: 'Data updated successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to update data'
        });
    }
});

// DELETE /api/data/:key - Delete data
app.delete('/api/data/:key', async (req, res) => {
    try {
        const { key } = req.params;

        if (!dataStore[key]) {
            return res.status(404).json({
                success: false,
                error: 'Data not found'
            });
        }

        delete dataStore[key];
        await saveData();

        res.json({
            success: true,
            message: 'Data deleted successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to delete data'
        });
    }
});

// DELETE /api/data - Clear all data
app.delete('/api/data', async (req, res) => {
    try {
        dataStore = {};
        await saveData();

        res.json({
            success: true,
            message: 'All data cleared successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to clear data'
        });
    }
});

// GET /api/stats - Get statistics
app.get('/api/stats', (req, res) => {
    try {
        const count = Object.keys(dataStore).length;
        const storageSize = Buffer.byteLength(JSON.stringify(dataStore), 'utf8');
        
        res.json({
            success: true,
            stats: {
                count,
                storageSize,
                storageSizeFormatted: formatBytes(storageSize)
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to get statistics'
        });
    }
});

// Helper function to format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        message: 'Server is running',
        timestamp: new Date().toISOString()
    });
});

// Start server
async function startServer() {
    await loadData();
    
    app.listen(PORT, () => {
        console.log(`🚀 Server running on http://localhost:${PORT}`);
        console.log(`📊 API endpoints available at http://localhost:${PORT}/api`);
    });
}

startServer().catch(console.error); 