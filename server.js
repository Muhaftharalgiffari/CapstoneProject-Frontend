const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Konfigurasi multer untuk upload file
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ 
    storage: storage,
    limits: {
        fileSize: 5 * 1024 * 1024 // Batasi ukuran file 5MB
    }
});

// Pastikan folder uploads ada
const fs = require('fs');
if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads');
}

// Endpoint health check
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'ok',
        timestamp: new Date().toISOString()
    });
});

// Endpoint untuk prediksi
app.post('/api/predict', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'Tidak ada file yang diupload' });
    }

    // Jalankan script Python untuk prediksi
    const pythonProcess = spawn('python', ['predict.py', req.file.path]);
    
    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
        // Log error untuk debugging
        console.error('Python stderr:', data.toString());
    });

    pythonProcess.on('close', (code) => {
        // Hapus file setelah selesai
        fs.unlink(req.file.path, (err) => {
            if (err) console.error('Error deleting file:', err);
        });

        if (code !== 0) {
            console.error('Python process exited with code', code);
            return res.status(500).json({ error: 'Gagal memproses gambar' });
        }

        try {
            const prediction = JSON.parse(result);
            res.json(prediction);
        } catch (e) {
            console.error('Error parsing prediction result:', e);
            res.status(500).json({ error: 'Gagal memparse hasil prediksi' });
        }
    });
});

// Serve frontend static files
app.use(express.static(path.join(__dirname, '../frontend')));

// Handle SPA routing
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.listen(port, () => {
    console.log(`Server berjalan di http://localhost:${port}`);
}); 