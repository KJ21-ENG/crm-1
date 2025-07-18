const express = require('express');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// WhatsApp client
let client = null;
let qrCodeString = '';
let isConnected = false;
let phoneNumber = null;

// Initialize WhatsApp client
function initializeClient() {
    // Don't initialize if already initializing
    if (client && client.isInitializing) {
        return;
    }
    
    client = new Client({
        authStrategy: new LocalAuth(),
        puppeteer: {
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        }
    });
    
    // Mark as initializing
    client.isInitializing = true;

    client.on('qr', (qr) => {
        console.log('QR code received');
        // Generate QR code as data URL immediately
        qrcode.toDataURL(qr, (err, url) => {
            if (err) {
                console.error('Error generating QR code:', err);
                qrCodeString = qr; // Fallback to string
            } else {
                qrCodeString = url;
                console.log('QR code generated as data URL');
            }
            // Clear initializing flag when QR code is ready
            if (client) {
                client.isInitializing = false;
            }
        });
    });

    client.on('ready', async () => {
        console.log('WhatsApp client is ready!');
        isConnected = true;
        qrCodeString = '';
        client.isInitializing = false; // Clear initializing flag
        
        // Get phone number with better error handling
        try {
            if (client.info && client.info.wid && client.info.wid.user) {
                phoneNumber = client.info.wid.user;
            } else {
                // Try alternative method
                const info = await client.getState();
                phoneNumber = client.info?.me?.user || 'Connected';
            }
        } catch (error) {
            console.error('Error getting phone number:', error);
            phoneNumber = 'Connected';
        }
        
        console.log('WhatsApp ready - Connected:', isConnected, 'Phone:', phoneNumber);
    });

    client.on('authenticated', () => {
        console.log('WhatsApp client authenticated');
        // Set connected state here as backup
        isConnected = true;
        qrCodeString = '';
        client.isInitializing = false; // Clear initializing flag
    });

    client.on('auth_failure', (msg) => {
        console.error('Authentication failed:', msg);
        isConnected = false;
        phoneNumber = null;
        client.isInitializing = false; // Clear initializing flag
    });

    client.on('disconnected', (reason) => {
        console.log('WhatsApp client disconnected:', reason);
        isConnected = false;
        phoneNumber = null;
        qrCodeString = '';
        client.isInitializing = false; // Clear initializing flag
    });

    client.initialize();
}

// API Routes

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Get QR code for authentication
app.get('/qr-code', (req, res) => {
    if (isConnected) {
        res.json({ 
            success: false, 
            message: 'WhatsApp is already connected' 
        });
        return;
    }

    if (!qrCodeString) {
        // Initialize client if not already done
        if (!client || client.isInitializing) {
            if (!client) {
                initializeClient();
            }
            
            res.json({ 
                success: false, 
                message: 'QR code is being generated. Please try again in a moment.' 
            });
            return;
        }
    }

    res.json({ 
        success: true, 
        qr_code: qrCodeString 
    });
});

// Get connection status
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        phone_number: phoneNumber,
        qr_code_available: !!qrCodeString,
        is_initializing: client ? client.isInitializing : false,
        timestamp: new Date().toISOString()
    });
});

// Send message
app.post('/send-message', async (req, res) => {
    const { to, message } = req.body;

    if (!isConnected || !client) {
        res.json({ 
            success: false, 
            message: 'WhatsApp is not connected' 
        });
        return;
    }

    if (!to || !message) {
        res.json({ 
            success: false, 
            message: 'Phone number and message are required' 
        });
        return;
    }

    try {
        // Format phone number (remove + and add country code if needed)
        let formattedNumber = to.replace(/\D/g, '');
        
        // If number doesn't start with country code, assume it's Indian number
        if (!formattedNumber.startsWith('91') && formattedNumber.length === 10) {
            formattedNumber = '91' + formattedNumber;
        }
        
        const chatId = formattedNumber + '@c.us';

        // Send message
        await client.sendMessage(chatId, message);

        res.json({ 
            success: true, 
            message: 'Message sent successfully',
            to: formattedNumber
        });

    } catch (error) {
        console.error('Error sending message:', error);
        res.json({ 
            success: false, 
            message: 'Error sending message: ' + error.message 
        });
    }
});

// Logout WhatsApp (without destroying the service)
app.post('/logout', async (req, res) => {
    try {
        if (client) {
            await client.logout();
            // Don't destroy the client, just logout from the account
        }
        
        isConnected = false;
        phoneNumber = null;
        qrCodeString = '';
        
        // Reinitialize the client to allow new QR code generation
        client = null;
        initializeClient();
        
        // Set initializing flag to true
        if (client) {
            client.isInitializing = true;
        }

        res.json({ 
            success: true, 
            message: 'WhatsApp logged out successfully' 
        });

    } catch (error) {
        console.error('Error logging out WhatsApp:', error);
        res.json({ 
            success: false, 
            message: 'Error logging out WhatsApp: ' + error.message 
        });
    }
});

// Disconnect WhatsApp (legacy endpoint - now just calls logout)
app.post('/disconnect', async (req, res) => {
    try {
        if (client) {
            await client.logout();
            // Keep the service running, just logout from the account
        }
        
        isConnected = false;
        phoneNumber = null;
        qrCodeString = '';
        
        // Reinitialize the client to allow new QR code generation
        client = null;
        initializeClient();

        res.json({ 
            success: true, 
            message: 'WhatsApp logged out successfully' 
        });

    } catch (error) {
        console.error('Error logging out WhatsApp:', error);
        res.json({ 
            success: false, 
            message: 'Error logging out WhatsApp: ' + error.message 
        });
    }
});

// Send media message (future enhancement)
app.post('/send-media', async (req, res) => {
    const { to, media_url, caption } = req.body;

    if (!isConnected || !client) {
        res.json({ 
            success: false, 
            message: 'WhatsApp is not connected' 
        });
        return;
    }

    if (!to || !media_url) {
        res.json({ 
            success: false, 
            message: 'Phone number and media URL are required' 
        });
        return;
    }

    try {
        // Format phone number
        let formattedNumber = to.replace(/\D/g, '');
        
        if (!formattedNumber.startsWith('91') && formattedNumber.length === 10) {
            formattedNumber = '91' + formattedNumber;
        }
        
        const chatId = formattedNumber + '@c.us';

        // Create media message
        const media = await MessageMedia.fromUrl(media_url);
        
        await client.sendMessage(chatId, media, { caption: caption || '' });

        res.json({ 
            success: true, 
            message: 'Media sent successfully',
            to: formattedNumber
        });

    } catch (error) {
        console.error('Error sending media:', error);
        res.json({ 
            success: false, 
            message: 'Error sending media: ' + error.message 
        });
    }
});

// Start server
app.listen(port, () => {
    console.log(`WhatsApp service running on port ${port}`);
    console.log(`Health check: http://localhost:${port}/health`);
    console.log(`QR code: http://localhost:${port}/qr-code`);
    console.log(`Status: http://localhost:${port}/status`);
    
    // Initialize WhatsApp client on startup
    initializeClient();
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down WhatsApp service...');
    
    if (client) {
        try {
            await client.destroy();
        } catch (error) {
            console.error('Error during shutdown:', error);
        }
    }
    
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('Shutting down WhatsApp service...');
    
    if (client) {
        try {
            await client.destroy();
        } catch (error) {
            console.error('Error during shutdown:', error);
        }
    }
    
    process.exit(0);
}); 