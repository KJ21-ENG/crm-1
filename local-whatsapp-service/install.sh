#!/bin/bash

# CRM Local WhatsApp Service Installation Script
echo "🚀 Installing CRM Local WhatsApp Service..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create startup script
echo "📝 Creating startup script..."
cat > start-service.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting CRM Local WhatsApp Service..."
node local-service.js
EOF

chmod +x start-service.sh

# Create systemd service (for Linux)
if command -v systemctl &> /dev/null; then
    echo "📝 Creating systemd service..."
    sudo tee /etc/systemd/system/crm-whatsapp.service > /dev/null << EOF
[Unit]
Description=CRM Local WhatsApp Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which node) local-service.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Systemd service created"
    echo "To enable auto-start: sudo systemctl enable crm-whatsapp.service"
    echo "To start service: sudo systemctl start crm-whatsapp.service"
fi

# Create launchd service (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📝 Creating launchd service for macOS..."
    mkdir -p ~/Library/LaunchAgents
    
    cat > ~/Library/LaunchAgents/com.crm.whatsapp.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.crm.whatsapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which node)</string>
        <string>$(pwd)/local-service.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$(pwd)/service.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/service-error.log</string>
</dict>
</plist>
EOF

    echo "✅ Launchd service created"
    echo "To load service: launchctl load ~/Library/LaunchAgents/com.crm.whatsapp.plist"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start the service: ./start-service.sh"
echo "2. Install the Chrome extension from: apps/crm/whatsapp-extension/"
echo "3. Open your CRM and connect WhatsApp"
echo ""
echo "🔗 Service will be available at: http://localhost:3001"
echo "📊 Health check: http://localhost:3001/health"
echo ""
echo "💡 For auto-start on boot:"
if command -v systemctl &> /dev/null; then
    echo "   sudo systemctl enable crm-whatsapp.service"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   launchctl load ~/Library/LaunchAgents/com.crm.whatsapp.plist"
fi 