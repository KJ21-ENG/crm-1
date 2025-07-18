# CRM WhatsApp Chrome Extension

This Chrome extension provides local WhatsApp integration for the CRM system, allowing each user to connect their own WhatsApp account without conflicts.

## 🚀 Installation

### Prerequisites
1. **Local WhatsApp Service** must be running (see `../local-whatsapp-service/README.md`)
2. **Google Chrome** browser
3. **Node.js** 16+ (for local service)

### Step 1: Install Local WhatsApp Service
```bash
cd ../local-whatsapp-service
./install.sh
./start-service.sh
```

### Step 2: Install Chrome Extension

#### Method 1: Load Unpacked Extension (Development)
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `whatsapp-extension` folder
5. The extension should appear in your extensions list

#### Method 2: Pack Extension (Production)
1. In `chrome://extensions/`, click "Pack extension"
2. Select the `whatsapp-extension` folder
3. This creates a `.crx` file that can be distributed

## 📱 Usage

### Connecting WhatsApp
1. **Start Local Service**: Ensure the local WhatsApp service is running
2. **Open CRM**: Navigate to your CRM application
3. **Click Extension Icon**: Click the CRM WhatsApp extension icon in Chrome toolbar
4. **Connect**: Click "Connect WhatsApp" button
5. **Scan QR Code**: Use your WhatsApp mobile app to scan the QR code
6. **Ready**: Once connected, you can send messages from the CRM

### Sending Messages
- **From CRM Interface**: Use existing WhatsApp send buttons in the CRM
- **From Extension**: Click the extension icon and use the popup interface
- **Status Indicator**: Green dot indicates connected status

## 🔧 Configuration

### Extension Settings
The extension automatically detects CRM pages and injects the WhatsApp interface. It works with:
- `http://localhost:8000/*`
- `https://crm.localhost/*`
- Any page with `[data-whatsapp-integration]` attribute

### Local Service Configuration
- **Port**: 3001 (configurable in `local-service.js`)
- **Session Storage**: `~/.wwebjs_auth/` (automatic)
- **Auto-reconnect**: Enabled by default

## 🛠️ Development

### File Structure
```
whatsapp-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker
├── content.js            # Content script (injected into CRM)
├── popup.html            # Extension popup UI
├── popup.js              # Popup functionality
├── icons/                # Extension icons
└── README.md             # This file
```

### Modifying the Extension
1. **Background Script**: Handles communication with local service
2. **Content Script**: Injects UI into CRM pages
3. **Popup**: Extension popup interface
4. **Manifest**: Extension permissions and configuration

### Testing Changes
1. Make your changes
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension
4. Reload your CRM page

## 🔍 Troubleshooting

### Extension Not Working
1. **Check Local Service**: Ensure service is running on port 3001
2. **Check Permissions**: Verify extension has required permissions
3. **Check Console**: Open DevTools and check for errors
4. **Reload Extension**: Refresh the extension in `chrome://extensions/`

### WhatsApp Connection Issues
1. **QR Code Not Appearing**: Check local service logs
2. **Connection Fails**: Try disconnecting and reconnecting
3. **Session Expired**: Clear browser data and reconnect
4. **Multiple Users**: Each user needs their own local service

### Common Errors
- **"Service not running"**: Start the local WhatsApp service
- **"Permission denied"**: Check extension permissions
- **"QR code failed"**: Restart local service
- **"Message send failed"**: Check WhatsApp connection status

## 🔒 Security

### Local Service Security
- **Port Binding**: Service only binds to localhost (127.0.0.1)
- **CORS**: Configured for local development only
- **Session Storage**: WhatsApp sessions stored locally
- **No External Access**: Service doesn't expose data externally

### Extension Security
- **Limited Permissions**: Only requests necessary permissions
- **Local Communication**: Only communicates with localhost:3001
- **No Data Collection**: Extension doesn't collect or store user data
- **Open Source**: Code is transparent and auditable

## 📋 API Reference

### Local Service Endpoints
- `GET /status` - Get service status
- `GET /qr-code` - Get WhatsApp QR code
- `POST /send-message` - Send WhatsApp message
- `POST /disconnect` - Disconnect WhatsApp
- `GET /health` - Health check

### Extension Messages
- `initialize` - Initialize extension
- `getStatus` - Get WhatsApp status
- `getQRCode` - Get QR code
- `sendMessage` - Send message
- `statusUpdate` - Status change notification

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review local service logs
3. Check Chrome DevTools console
4. Create an issue in the repository 