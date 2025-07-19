# CRM WhatsApp Extension v1.1.0

A Chrome extension that integrates WhatsApp Web.js with the CRM system, allowing users to send WhatsApp messages directly from the CRM interface.

## ✨ New in v1.1.0

- **🔓 Logout Functionality**: Users can now logout and switch to different WhatsApp accounts
- **🔄 QR Code Refresh**: Generate new QR codes for re-authentication
- **📱 Phone Number Display**: Shows connected phone number when authenticated
- **🎨 Enhanced UI**: Improved popup interface with better visual feedback
- **⚡ Better Error Handling**: More robust error handling and user feedback

## Features

- **WhatsApp Integration**: Connect your WhatsApp account via QR code
- **Message Sending**: Send messages directly from CRM tickets and leads
- **Multi-User Support**: Each user can connect their own WhatsApp account
- **Real-time Status**: Monitor connection status in real-time
- **Logout Functionality**: Logout and switch to different WhatsApp accounts
- **QR Code Refresh**: Generate new QR codes for re-authentication

## Installation

### Prerequisites

1. **Local WhatsApp Service**: Make sure the local WhatsApp service is running on port 3001
2. **Chrome Browser**: This extension works with Chrome and Chromium-based browsers
3. **WhatsApp Mobile App**: For QR code scanning

### Installation Steps

1. **Download the Extension**:
   - Go to CRM Settings → WhatsApp Setup
   - Click "Download Extension" button
   - Extract the downloaded ZIP file

2. **Install in Chrome**:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)
   - Click "Load unpacked"
   - Select the extracted extension folder

3. **Connect WhatsApp**:
   - Start the local WhatsApp service
   - Click the extension icon in Chrome toolbar
   - Click "Connect WhatsApp"
   - Scan QR code with your WhatsApp mobile app

## Usage

### Connecting WhatsApp

1. Click the extension icon in Chrome toolbar
2. Click "Connect WhatsApp" button
3. Wait for QR code to appear
4. Open WhatsApp on your phone
5. Go to Settings → Linked Devices → Link a Device
6. Scan the QR code
7. Wait for connection confirmation (green dot)

### Sending Messages

1. Open any CRM ticket or lead
2. Go to WhatsApp Support tab
3. Select support pages to send
4. Click "Send via WhatsApp"
5. Message will be sent to the customer's mobile number

### Logging Out

1. Click the extension icon in Chrome toolbar
2. Click "Logout WhatsApp" button
3. Confirm logout
4. New QR code will appear for re-authentication

### Refreshing QR Code

1. Click the extension icon in Chrome toolbar
2. Click "Refresh QR Code" button
3. New QR code will be generated

## Troubleshooting

### Extension Not Working

- Check if local WhatsApp service is running on port 3001
- Verify extension permissions in Chrome
- Check Chrome DevTools console for errors
- Restart the local WhatsApp service

### Connection Issues

- Ensure WhatsApp mobile app is up to date
- Check internet connection
- Try logging out and reconnecting
- Clear browser cache and cookies

### QR Code Not Appearing

- Wait 30-60 seconds for initialization
- Check local service logs
- Restart the local WhatsApp service
- Verify Node.js version (16.0.0+)

## Development

### Local Development

1. Clone the repository
2. Make changes to extension files
3. Reload extension in Chrome (`chrome://extensions/`)
4. Test changes

### Building for Distribution

1. Update version in `manifest.json`
2. Create ZIP file with all extension files
3. Upload to CRM system for download

## File Structure

```
whatsapp-extension/
├── manifest.json          # Extension manifest
├── background.js          # Background service worker
├── content.js            # Content script for CRM pages
├── popup.html            # Extension popup UI
├── popup.js              # Popup functionality
├── README.md             # This file
└── icons/                # Extension icons
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## API Integration

The extension communicates with:
- **Local WhatsApp Service**: For WhatsApp Web.js functionality
- **CRM Frontend**: For integration with CRM interface
- **Chrome Extension APIs**: For browser integration

## Security

- All WhatsApp communication is handled locally
- No data is sent to external servers
- Uses official WhatsApp Web.js library
- Secure QR code authentication

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review local service logs
3. Check Chrome DevTools console
4. Contact system administrator

## Changelog

### v1.1.0 (Current)
- Added logout functionality
- Added QR code refresh feature
- Enhanced UI with phone number display
- Improved error handling
- Better user feedback

### v1.0.0
- Initial release
- Basic WhatsApp integration
- QR code authentication
- Message sending functionality 