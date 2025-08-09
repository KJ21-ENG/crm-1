const express = require('express');
const cors = require('cors');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

// Middleware
app.use(cors());
app.use(express.json());

// WhatsApp client instance
let client = null;
let qrCodeData = null;
let clientStatus = 'disconnected';
let lastQrAt = 0;

// SSE clients for live updates
const sseClients = new Set();

function sseBroadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const res of sseClients) {
    try {
      res.write(payload);
    } catch (_) {}
  }
}

// Create session directory
const sessionDir = path.join(__dirname, '.wwebjs_auth');
if (!fs.existsSync(sessionDir)) {
  fs.mkdirSync(sessionDir, { recursive: true });
}

// Try to detect a Chrome executable path for macOS/Linux/Windows
function getChromeExecutablePath() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) {
    return process.env.PUPPETEER_EXECUTABLE_PATH;
  }

  const candidates = [
    // macOS (regular)
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    // macOS (Chrome for Testing)
    '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    // Linux common paths
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    // Windows
    'C:/Program Files/Google/Chrome/Application/chrome.exe',
    'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  ];

  for (const p of candidates) {
    try {
      if (fs.existsSync(p)) {
        return p;
      }
    } catch (_) {}
  }

  return undefined;
}

// Initialize WhatsApp client
function initializeWhatsAppClient() {
  if (client) {
    client.destroy();
  }

  client = new Client({
    authStrategy: new LocalAuth({
      clientId: 'crm-local-client',
      dataPath: sessionDir
    }),
    puppeteer: {
      headless: true,
      executablePath: getChromeExecutablePath(),
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
      ],
      timeout: 60000
    }
  });

  // Event handlers
  client.on('qr', async (qr) => {
    console.log('QR Code received');
    try {
      qrCodeData = await qrcode.toDataURL(qr);
      clientStatus = 'connecting';
      console.log('QR Code generated');
      lastQrAt = Date.now();
      // Notify listeners in real-time
      sseBroadcast('qr', { qrCode: qrCodeData.split(',')[1] });
      sseBroadcast('status', { status: clientStatus });
    } catch (error) {
      console.error('Error generating QR code:', error);
    }
  });

  client.on('ready', () => {
    console.log('WhatsApp client is ready!');
    clientStatus = 'connected';
    qrCodeData = null;
    sseBroadcast('status', { status: clientStatus });
  });

  client.on('authenticated', () => {
    console.log('WhatsApp client authenticated');
    clientStatus = 'authenticated';
    sseBroadcast('status', { status: clientStatus });
  });

  client.on('auth_failure', (msg) => {
    console.error('WhatsApp authentication failed:', msg);
    clientStatus = 'auth_failed';
    qrCodeData = null;
    sseBroadcast('status', { status: clientStatus });
  });

  client.on('disconnected', (reason) => {
    console.log('WhatsApp client disconnected:', reason);
    clientStatus = 'disconnected';
    qrCodeData = null;
    sseBroadcast('status', { status: clientStatus });
  });

  client.on('message', (message) => {
    console.log('Message received:', message.body);
    // You can add message handling logic here
  });

  // Initialize the client
  client.initialize().catch(error => {
    console.error('Failed to initialize WhatsApp client:', error);
    clientStatus = 'error';
  });
}

// API Routes

// Get service status
app.get('/status', (req, res) => {
  res.json({
    status: clientStatus,
    timestamp: new Date().toISOString(),
    service: 'CRM Local WhatsApp Service'
  });
});

// SSE stream for real-time updates
app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders?.();
  sseClients.add(res);

  // Send initial snapshot
  res.write(`event: status\ndata: ${JSON.stringify({ status: clientStatus })}\n\n`);
  if (qrCodeData) {
    res.write(`event: qr\ndata: ${JSON.stringify({ qrCode: qrCodeData.split(',')[1] })}\n\n`);
  }

  req.on('close', () => {
    sseClients.delete(res);
  });
});

// Get QR code
app.get('/qr-code', (req, res) => {
  if (qrCodeData) {
    // Convert data URL to base64
    const base64Data = qrCodeData.split(',')[1];
    res.json({
      qrCode: base64Data,
      status: clientStatus
    });
  } else {
    res.status(404).json({
      error: 'QR code not available',
      status: clientStatus
    });
  }
});

// Send WhatsApp message
app.post('/send-message', async (req, res) => {
  try {
    const { phone, message, debugId } = req.body;
    console.log('[CRM WhatsApp][svc] send-message', { debugId, phone: mask(phone), len: message?.length });

    if (!phone || !message) {
      return res.status(400).json({
        error: 'Phone number and message are required'
      });
    }

    if (clientStatus !== 'connected') {
      return res.status(400).json({
        error: 'WhatsApp is not connected. Please scan QR code first.'
      });
    }

    // Format phone number (remove + and add country code if needed)
    let formattedPhone = phone.replace(/\D/g, '');
    if (!formattedPhone.startsWith('91')) {
      formattedPhone = '91' + formattedPhone;
    }
    formattedPhone = formattedPhone + '@c.us';

    // Send message
    const result = await client.sendMessage(formattedPhone, message);
    console.log('[CRM WhatsApp][svc] sent', { debugId, to: formattedPhone });
    
    res.json({
      success: true,
      messageId: result.id._serialized,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error sending message:', error);
    res.status(500).json({
      error: error.message
    });
  }
});

// Disconnect WhatsApp
app.post('/disconnect', (req, res) => {
  try {
    if (client) {
      client.destroy();
      client = null;
    }
    clientStatus = 'disconnected';
    qrCodeData = null;
    
    res.json({
      success: true,
      message: 'WhatsApp disconnected successfully'
    });
  } catch (error) {
    console.error('Error disconnecting:', error);
    res.status(500).json({
      error: error.message
    });
  }
});

// Logout WhatsApp (logout and clear session data)
app.post('/logout', async (req, res) => {
  try {
    console.log('Logging out WhatsApp...');
    
    // Destroy current client
    if (client) {
      await client.destroy();
      client = null;
    }
    
    // Reset status
    clientStatus = 'disconnected';
    qrCodeData = null;
    
    // Clear session data
    const sessionPath = path.join(sessionDir, 'crm-local-client');
    if (fs.existsSync(sessionPath)) {
      try {
        fs.rmSync(sessionPath, { recursive: true, force: true });
        console.log('Session data cleared');
      } catch (error) {
        console.error('Error clearing session data:', error);
      }
    }
    
    // Clear cache data as well
    const cachePath = path.join(sessionDir, '.wwebjs_cache');
    if (fs.existsSync(cachePath)) {
      try {
        fs.rmSync(cachePath, { recursive: true, force: true });
        console.log('Cache data cleared');
      } catch (error) {
        console.error('Error clearing cache data:', error);
      }
    }
    
    // Immediately reinitialize to generate new QR for quick reconnect
    initializeWhatsAppClient();
    console.log('Logout completed. Reinitializing for fresh QR...');
    
    res.json({
      success: true,
      message: 'WhatsApp logged out successfully. Session data cleared.'
    });
  } catch (error) {
    console.error('Error logging out:', error);
    res.status(500).json({
      error: error.message
    });
  }
});

// Request new QR code (after logout)
app.post('/request-qr', (req, res) => {
  try {
    console.log('Requesting new QR code...');
    
    // Allow QR code generation if not connected (disconnected or connecting)
    if (clientStatus !== 'connected') {
      // Reset to disconnected state first
      clientStatus = 'disconnected';
      qrCodeData = null;
      
      // Destroy existing client if any
      if (client) {
        client.destroy();
        client = null;
      }
      
      // Initialize new client
      initializeWhatsAppClient();
      res.json({
        success: true,
        message: 'QR code generation initiated. Check /qr-code endpoint in a few seconds.'
      });
    } else {
      res.json({
        success: false,
        message: 'WhatsApp is already connected. No QR code needed.'
      });
    }
  } catch (error) {
    console.error('Error requesting QR code:', error);
    res.status(500).json({
      error: error.message
    });
  }
});

// Reconnect WhatsApp
app.post('/reconnect', (req, res) => {
  try {
    initializeWhatsAppClient();
    res.json({
      success: true,
      message: 'WhatsApp reconnection initiated'
    });
  } catch (error) {
    console.error('Error reconnecting:', error);
    res.status(500).json({
      error: error.message
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'CRM Local WhatsApp Service',
    timestamp: new Date().toISOString(),
    whatsappStatus: clientStatus
  });
});

// Get client info
app.get('/client-info', (req, res) => {
  if (client && clientStatus === 'connected') {
    res.json({
      status: clientStatus,
      info: {
        platform: client.info.platform,
        pushname: client.info.pushname,
        wid: client.info.wid.user
      }
    });
  } else {
    res.json({
      status: clientStatus,
      info: null
    });
  }
});

function mask(p) {
  if (!p) return p;
  const s = String(p);
  return s.length > 4 ? s.slice(0, s.length - 4).replace(/\d/g, '*') + s.slice(-4) : s;
}

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`CRM Local WhatsApp Service running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Status: http://localhost:${PORT}/status`);
  
  // Initialize WhatsApp client
  initializeWhatsAppClient();
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down server...');
  if (client) {
    client.destroy();
  }
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('Shutting down server...');
  if (client) {
    client.destroy();
  }
  process.exit(0);
}); 

// Periodically ensure a fresh QR is available when not connected
setInterval(() => {
  if (clientStatus !== 'connected') {
    const staleMs = Date.now() - (lastQrAt || 0);
    if (!qrCodeData || staleMs > 55_000) {
      try {
        console.log('Refreshing QR...');
        initializeWhatsAppClient();
      } catch (_) {}
    }
  }
}, 30_000);