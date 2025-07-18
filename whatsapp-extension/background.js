// Background service worker for CRM WhatsApp Extension
let localServicePort = null;
let whatsappStatus = 'disconnected';
let qrCodeData = null;

// Initialize local WhatsApp service
async function initializeLocalService() {
  try {
    // Check if local service is already running
    const response = await fetch('http://localhost:3001/status');
    if (response.ok) {
      const status = await response.json();
      whatsappStatus = status.status;
      return true;
    }
  } catch (error) {
    console.log('Local service not running, starting...');
  }

  // Start local service if not running
  try {
    // This would typically start a local Node.js process
    // For now, we'll assume the service is started manually
    console.log('Please start the local WhatsApp service manually');
    return false;
  } catch (error) {
    console.error('Failed to start local service:', error);
    return false;
  }
}

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'getStatus':
      sendResponse({ status: whatsappStatus, qrCode: qrCodeData });
      break;
      
    case 'sendMessage':
      sendWhatsAppMessage(request.phone, request.message)
        .then(result => sendResponse(result))
        .catch(error => sendResponse({ error: error.message }));
      return true; // Keep message channel open for async response
      
    case 'getQRCode':
      getQRCode()
        .then(qr => sendResponse({ qrCode: qr }))
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'initialize':
      initializeLocalService()
        .then(success => sendResponse({ success }))
        .catch(error => sendResponse({ error: error.message }));
      return true;
  }
});

// Send WhatsApp message via local service
async function sendWhatsAppMessage(phone, message) {
  try {
    const response = await fetch('http://localhost:3001/send-message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        phone: phone,
        message: message
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error sending WhatsApp message:', error);
    throw error;
  }
}

// Get QR code from local service
async function getQRCode() {
  try {
    const response = await fetch('http://localhost:3001/qr-code');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    qrCodeData = result.qrCode;
    return result.qrCode;
  } catch (error) {
    console.error('Error getting QR code:', error);
    throw error;
  }
}

// Monitor local service status
async function checkServiceStatus() {
  try {
    const response = await fetch('http://localhost:3001/status');
    if (response.ok) {
      const status = await response.json();
      whatsappStatus = status.status;
      
      // Notify content script of status change
      chrome.tabs.query({ url: ['http://localhost:8000/*', 'https://crm.localhost/*'] }, (tabs) => {
        tabs.forEach(tab => {
          chrome.tabs.sendMessage(tab.id, {
            action: 'statusUpdate',
            status: whatsappStatus
          });
        });
      });
    }
  } catch (error) {
    whatsappStatus = 'disconnected';
  }
}

// Check status every 5 seconds
setInterval(checkServiceStatus, 5000);

// Initialize on extension load
initializeLocalService(); 