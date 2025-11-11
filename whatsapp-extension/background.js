// Background service worker for CRM WhatsApp Extension
let localServicePort = null;
let whatsappStatus = 'disconnected';
let qrCodeData = null;
let phoneNumber = null;
let sse;

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
      sendResponse({ status: whatsappStatus, qrCode: qrCodeData, phoneNumber: phoneNumber });
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
      
    case 'logout':
      logoutWhatsApp()
        .then(result => sendResponse(result))
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
    console.log('[CRM WhatsApp][bg] sendWhatsAppMessage', { phone: mask(phone), len: message?.length });
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
      const text = await response.text().catch(() => '');
      throw new Error(`HTTP ${response.status}: ${response.statusText} ${text}`);
    }
    
    const result = await response.json();
    console.log('[CRM WhatsApp][bg] sendWhatsAppMessage:response', result);
    return result;
  } catch (error) {
    console.error('Error sending WhatsApp message:', error);
    return { success: false, error: error.message };
  }
}

function mask(p) {
  if (!p) return p;
  const s = String(p);
  return s.length > 4 ? s.slice(0, s.length - 4).replace(/\d/g, '*') + s.slice(-4) : s;
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

// Logout WhatsApp via local service
async function logoutWhatsApp() {
  try {
    const response = await fetch('http://localhost:3001/logout', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Update local status
    whatsappStatus = 'connecting';
    qrCodeData = null;
    phoneNumber = null;
    
    // Notify content script of status change
    chrome.tabs.query({ url: ['http://localhost:8000/*', 'https://crm.localhost/*', 'https://eshin.in/*', 'https://*.eshin.in/*'] }, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          action: 'statusUpdate',
          status: whatsappStatus
        });
      });
    });
    
    return result;
  } catch (error) {
    console.error('Error logging out WhatsApp:', error);
    throw error;
  }
}

// Monitor local service status
async function checkServiceStatus() {
  try {
    const response = await fetch('http://localhost:3001/status');
    if (response.ok) {
      const status = await response.json();
      const previousStatus = whatsappStatus;
      whatsappStatus = status.status;
      
      // Get phone number if connected
      if (whatsappStatus === 'connected') {
        try {
          const clientInfoResponse = await fetch('http://localhost:3001/client-info');
          if (clientInfoResponse.ok) {
            const clientInfo = await clientInfoResponse.json();
            phoneNumber = clientInfo.info?.wid || 'Connected';
          }
        } catch (error) {
          console.error('Error getting client info:', error);
          phoneNumber = 'Connected';
        }
      } else {
        phoneNumber = null;
      }
      
      // Notify content script of status change
      if (previousStatus !== whatsappStatus) {
        chrome.tabs.query({ url: ['http://localhost:8000/*', 'https://crm.localhost/*', 'https://eshin.in/*', 'https://*.eshin.in/*'] }, (tabs) => {
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, {
              action: 'statusUpdate',
              status: whatsappStatus,
              phoneNumber: phoneNumber
            });
          });
        });
      }
    }
  } catch (error) {
    whatsappStatus = 'disconnected';
    phoneNumber = null;
  }
}

// Check status every 5 seconds
setInterval(checkServiceStatus, 5000);

// Live updates from service via SSE
function startEventStream() {
  try {
    if (sse) sse.close();
    sse = new EventSource('http://localhost:3001/events');
    sse.addEventListener('status', (evt) => {
      try {
        const data = JSON.parse(evt.data || '{}');
        if (data.status) {
          const prev = whatsappStatus;
          whatsappStatus = data.status;
          if (prev !== whatsappStatus) {
            chrome.tabs.query({ url: ['http://localhost:8000/*', 'https://crm.localhost/*', 'https://eshin.in/*', 'https://*.eshin.in/*'] }, (tabs) => {
              tabs.forEach(tab => chrome.tabs.sendMessage(tab.id, { action: 'statusUpdate', status: whatsappStatus, phoneNumber }));
            });
          }
        }
      } catch (_) {}
    });
    sse.addEventListener('qr', (evt) => {
      try {
        const data = JSON.parse(evt.data || '{}');
        qrCodeData = data.qrCode || null;
        // no explicit UI push needed; content will request qr when opening modal
      } catch (_) {}
    });
    sse.onerror = () => {
      try { sse.close(); } catch (_) {}
      setTimeout(startEventStream, 3000);
    };
  } catch (_) {
    setTimeout(startEventStream, 3000);
  }
}
startEventStream();

// Initialize on extension load
initializeLocalService(); 