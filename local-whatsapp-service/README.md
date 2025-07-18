# CRM Local WhatsApp Service

A local Node.js service that provides WhatsApp Web.js integration for the CRM system. Each user runs this service on their own machine to connect their personal WhatsApp account.

## 🚀 Quick Start

### Prerequisites
- **Node.js** 16.0.0 or higher
- **npm** or **yarn**
- **Chrome/Chromium** (for Puppeteer)

### Installation
```bash
# Clone or download the service
cd local-whatsapp-service

# Install dependencies
npm install

# Start the service
npm start
```

### One-Click Installation
```bash
# Run the installation script
./install.sh
```

## 📱 Usage

### Starting the Service
```bash
# Method 1: Direct start
node local-service.js

# Method 2: Using npm script
npm start

# Method 3: Using startup script (after install.sh)
./start-service.sh
```

### Service Endpoints
Once running, the service provides these endpoints:

- **Health Check**: `http://localhost:3001/health`
- **Status**: `http://localhost:3001/status`
- **QR Code**: `http://localhost:3001/qr-code`
- **Send Message**: `POST http://localhost:3001/send-message`
- **Disconnect**: `POST http://localhost:3001/disconnect`

### Connecting WhatsApp
1. Start the service
2. Open `http://localhost:3001/status` in your browser
3. Scan the QR code with your WhatsApp mobile app
4. Service will show "connected" status when ready

## 🔧 Configuration

### Environment Variables
Create a `.env` file to customize settings:

```env
PORT=3001
SESSION_DIR=.wwebjs_auth
PUPPETEER_ARGS=--no-sandbox,--disable-setuid-sandbox
```

### Service Configuration
Edit `local-service.js` to modify:

- **Port**: Change `PORT` constant
- **Puppeteer Options**: Modify `puppeteer.args`
- **Session Storage**: Change `sessionDir` path
- **Phone Formatting**: Modify phone number formatting logic

### Auto-Start Configuration

#### macOS (Launchd)
```bash
# Load service for auto-start
launchctl load ~/Library/LaunchAgents/com.crm.whatsapp.plist

# Unload service
launchctl unload ~/Library/LaunchAgents/com.crm.whatsapp.plist
```

#### Linux (Systemd)
```bash
# Enable auto-start
sudo systemctl enable crm-whatsapp.service

# Start service
sudo systemctl start crm-whatsapp.service

# Check status
sudo systemctl status crm-whatsapp.service
```

#### Windows (Task Scheduler)
Create a scheduled task to run:
```cmd
node C:\path\to\local-service.js
```

## 🛠️ Development

### Project Structure
```
local-whatsapp-service/
├── local-service.js       # Main service file
├── package.json           # Dependencies and scripts
├── install.sh            # Installation script
├── start-service.sh      # Startup script
├── .wwebjs_auth/         # WhatsApp session storage
├── service.log           # Service logs
├── service-error.log     # Error logs
└── README.md             # This file
```

### Development Mode
```bash
# Install nodemon for auto-restart
npm install -g nodemon

# Run in development mode
npm run dev
```

### Logging
The service logs to:
- **Console**: Real-time logs
- **service.log**: Standard output
- **service-error.log**: Error messages

### Debug Mode
```bash
# Enable debug logging
DEBUG=whatsapp-web.js node local-service.js
```

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start
1. **Check Node.js version**: `node --version` (must be 16+)
2. **Check port availability**: `lsof -i :3001`
3. **Check dependencies**: `npm install`
4. **Check permissions**: Ensure write access to session directory

#### WhatsApp Connection Issues
1. **QR Code Not Appearing**: Check Puppeteer installation
2. **Connection Fails**: Clear session data and retry
3. **Session Expired**: Delete `.wwebjs_auth` folder and reconnect
4. **Multiple Sessions**: Ensure only one service instance running

#### Message Sending Issues
1. **Phone Format**: Ensure correct country code (91 for India)
2. **Connection Status**: Verify WhatsApp is connected
3. **Rate Limiting**: Wait between messages
4. **Invalid Number**: Check phone number format

### Error Messages

#### "Puppeteer failed to launch"
```bash
# Install missing dependencies (Ubuntu/Debian)
sudo apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget
```

#### "Port already in use"
```bash
# Find process using port 3001
lsof -i :3001

# Kill the process
kill -9 <PID>
```

#### "Session directory not writable"
```bash
# Fix permissions
chmod 755 .wwebjs_auth
```

### Performance Optimization

#### Memory Usage
- **Session Cleanup**: Regularly clear old sessions
- **Puppeteer Options**: Use headless mode and minimal args
- **Process Management**: Restart service periodically

#### Network Issues
- **Proxy Support**: Configure proxy in Puppeteer args
- **Firewall**: Ensure port 3001 is accessible
- **DNS**: Use reliable DNS servers

## 🔒 Security

### Local Security
- **Port Binding**: Service only binds to localhost
- **CORS**: Configured for local development
- **Session Storage**: WhatsApp sessions stored locally
- **No External Access**: Service doesn't expose data externally

### WhatsApp Security
- **Session Management**: Sessions stored locally only
- **Authentication**: Uses WhatsApp Web authentication
- **Message Encryption**: WhatsApp's end-to-end encryption
- **Rate Limiting**: Built-in message rate limiting

### Best Practices
1. **Regular Updates**: Keep Node.js and dependencies updated
2. **Session Cleanup**: Clear old sessions periodically
3. **Firewall**: Restrict access to localhost only
4. **Monitoring**: Monitor service logs for issues

## 📊 Monitoring

### Health Checks
```bash
# Check service health
curl http://localhost:3001/health

# Check WhatsApp status
curl http://localhost:3001/status

# Get client info
curl http://localhost:3001/client-info
```

### Log Monitoring
```bash
# Monitor logs in real-time
tail -f service.log

# Monitor errors
tail -f service-error.log
```

### Performance Metrics
- **Memory Usage**: Monitor Node.js memory consumption
- **Response Time**: Track API endpoint response times
- **Connection Status**: Monitor WhatsApp connection stability
- **Message Success Rate**: Track message delivery success

## 🔄 Updates

### Updating the Service
```bash
# Pull latest changes
git pull origin main

# Install new dependencies
npm install

# Restart service
npm start
```

### Updating Dependencies
```bash
# Update all dependencies
npm update

# Update specific package
npm update whatsapp-web.js
```

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
2. Review service logs
3. Check GitHub issues
4. Create a new issue with detailed information 