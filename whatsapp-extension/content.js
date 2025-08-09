// Content script for CRM WhatsApp Integration
class CRMWhatsAppIntegration {
  constructor() {
    this.status = 'disconnected';
    this.qrCode = null;
    this.isInitialized = false;
    this.debugEnabled = true; // set to true for detailed debugging
    this.init();
  }

  async init() {
    this.debug('init:start', { href: window.location.href });
    // Wait for page to load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupIntegration());
    } else {
      this.setupIntegration();
    }

    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
      if (request.action === 'statusUpdate') {
        this.debug('bg:statusUpdate', { request });
        this.updateStatus(request.status, request.phoneNumber);
      }
    });

    // Listen for CRM page events
    document.addEventListener('crm-whatsapp-open-qr', () => {
      this.debug('evt:openQR');
      this.showQRModal();
    });
    document.addEventListener('crm-whatsapp-request-status', async () => {
      this.debug('evt:requestStatus');
      try {
        const response = await this.sendMessageToBackground('getStatus');
        const evt = new CustomEvent('crm-whatsapp-status', {
          detail: {
            status: response?.status || this.status,
            phoneNumber: response?.phoneNumber || null,
            qrCodeAvailable: !!response?.qrCode,
          },
        });
        this.debug('evt:dispatchStatus', evt.detail);
        document.dispatchEvent(evt);
      } catch (e) {}
    });

    // Direct send hook from page
    document.addEventListener('crm-whatsapp-send-direct', async (e) => {
      try {
        const detail = e.detail || {};
        const phone = detail.phone;
        const message = detail.message;
        const debugId = this.generateDebugId();
        this.debug('evt:sendDirect', { phone, messageLen: message?.length, debugId });

        if (!phone || !message) {
          const ev = new CustomEvent('crm-whatsapp-send', { detail: { success: false, error: 'Phone and message are required' } });
          document.dispatchEvent(ev);
          return;
        }

        if (this.status !== 'connected') {
          const ev = new CustomEvent('crm-whatsapp-send', { detail: { success: false, error: 'WhatsApp not connected' } });
          document.dispatchEvent(ev);
          this.showQRModal();
          return;
        }

        const response = await this.sendMessageToBackground('sendMessage', { phone, message, debugId });
        this.debug('bg:sendMessage:response', { response, debugId });
        const ev = new CustomEvent('crm-whatsapp-send', { detail: { success: !!response?.success, error: response?.error, debugId } });
        document.dispatchEvent(ev);
      } catch (error) {
        this.debug('bg:sendMessage:error', { error: error?.message });
        const ev = new CustomEvent('crm-whatsapp-send', { detail: { success: false, error: error.message } });
        document.dispatchEvent(ev);
      }
    });
  }

  async setupIntegration() {
    // Check if we're on a CRM page that needs WhatsApp integration
    if (this.isCRMPage()) {
      await this.initializeExtension();
      this.injectWhatsAppUI();
      this.setupEventListeners();
    }
  }

  isCRMPage() {
    // Check if we're on a CRM page that has WhatsApp functionality
    return window.location.href.includes('localhost:8000') || 
           window.location.href.includes('crm.localhost') ||
           window.location.href.includes('eshin.in') ||
           document.querySelector('[data-whatsapp-integration]');
  }

  async initializeExtension() {
    try {
      const response = await this.sendMessageToBackground('initialize');
      if (response.success) {
        this.isInitialized = true;
        console.log('WhatsApp extension initialized');
      }
    } catch (error) {
      console.error('Failed to initialize WhatsApp extension:', error);
    }
  }

  injectWhatsAppUI() {
    // Create WhatsApp integration container
    const container = document.createElement('div');
    container.id = 'crm-whatsapp-integration';
    container.innerHTML = `
      <div class="whatsapp-status-bar">
        <div class="status-indicator">
          <span class="status-dot ${this.status}"></span>
          <span class="status-text">WhatsApp: ${this.status}</span>
        </div>
        <button id="whatsapp-connect-btn" class="btn btn-primary btn-sm">
          Connect WhatsApp
        </button>
      </div>
      
      <div id="whatsapp-qr-modal" class="modal" style="display: none;">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Connect WhatsApp</h3>
            <span class="close">&times;</span>
          </div>
          <div class="modal-body">
            <div id="qr-code-container">
              <p>Scan this QR code with your WhatsApp mobile app</p>
              <div id="qr-code-image"></div>
            </div>
            <div id="connection-status">
              <p>Status: <span id="connection-status-text">Initializing...</span></p>
            </div>
          </div>
        </div>
      </div>
    `;

    // Add styles
    const styles = document.createElement('style');
    styles.textContent = `
      #crm-whatsapp-integration {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 10000;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      .whatsapp-status-bar {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      
      .status-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
      }
      
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
      }
      
      .status-dot.connected { background: #25D366; }
      .status-dot.disconnected { background: #ff4444; }
      .status-dot.connecting { background: #ffaa00; }
      
      .btn {
        padding: 5px 10px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
      }
      
      .btn-primary {
        background: #25D366;
        color: white;
      }
      
      .btn-primary:hover {
        background: #128C7E;
      }
      
      .modal {
        position: fixed;
        z-index: 10001;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
      }
      
      .modal-content {
        background-color: white;
        margin: 15% auto;
        padding: 20px;
        border-radius: 8px;
        width: 400px;
        max-width: 90%;
      }
      
      .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
      }
      
      .close {
        color: #aaa;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
      }
      
      .close:hover {
        color: #000;
      }
      
      #qr-code-image {
        text-align: center;
        margin: 20px 0;
      }
      
      #qr-code-image img {
        max-width: 200px;
        height: auto;
      }
    `;

    document.head.appendChild(styles);
    document.body.appendChild(container);
  }

  setupEventListeners() {
    // Connect button
    const connectBtn = document.getElementById('whatsapp-connect-btn');
    if (connectBtn) {
      connectBtn.addEventListener('click', () => this.showQRModal());
    }

    // Modal close button
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.hideQRModal());
    }

    // Close modal when clicking outside
    const modal = document.getElementById('whatsapp-qr-modal');
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          this.hideQRModal();
        }
      });
    }

    // Intercept existing WhatsApp send buttons
    this.interceptExistingWhatsAppButtons();
  }

  async showQRModal() {
    const modal = document.getElementById('whatsapp-qr-modal');
    if (modal) {
      modal.style.display = 'block';
      await this.loadQRCode();
    }
  }

  hideQRModal() {
    const modal = document.getElementById('whatsapp-qr-modal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  async loadQRCode() {
    try {
      const response = await this.sendMessageToBackground('getQRCode');
      if (response.qrCode) {
        this.displayQRCode(response.qrCode);
      }
    } catch (error) {
      console.error('Failed to load QR code:', error);
      this.updateConnectionStatus('Failed to load QR code');
    }
  }

  displayQRCode(qrCodeData) {
    const qrContainer = document.getElementById('qr-code-image');
    if (qrContainer) {
      qrContainer.innerHTML = `<img src="data:image/png;base64,${qrCodeData}" alt="WhatsApp QR Code">`;
    }
  }

  updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status-text');
    if (statusElement) {
      statusElement.textContent = status;
    }
  }

  updateStatus(newStatus, phoneNumber = null) {
    this.status = newStatus;
    this.debug('ui:updateStatus', { status: newStatus, phoneNumber });
    
    // Update status indicator
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (statusDot) {
      statusDot.className = `status-dot ${newStatus}`;
    }
    
    if (statusText) {
      let statusDisplay = `WhatsApp: ${newStatus}`;
      if (newStatus === 'connected' && phoneNumber) {
        statusDisplay += ` (${phoneNumber})`;
      }
      statusText.textContent = statusDisplay;
    }

    // Update connection status in modal
    this.updateConnectionStatus(newStatus);

    // Hide modal if connected
    if (newStatus === 'connected') {
      this.hideQRModal();
    }

    // Inform CRM page of current status
    const evt = new CustomEvent('crm-whatsapp-status', {
      detail: {
        status: newStatus,
        phoneNumber,
        qrCodeAvailable: this.qrCode != null,
      },
    });
    this.debug('evt:dispatchStatus', evt.detail);
    document.dispatchEvent(evt);
  }

  interceptExistingWhatsAppButtons() {
    // Find existing WhatsApp send buttons and intercept them
    const observer = new MutationObserver(() => {
      const whatsappButtons = document.querySelectorAll('[data-whatsapp-send], .whatsapp-send-btn');
      whatsappButtons.forEach(button => {
        if (!button.hasAttribute('data-intercepted')) {
          button.setAttribute('data-intercepted', 'true');
          button.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleWhatsAppSend(button);
          });
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  async handleWhatsAppSend(button) {
    // Extract phone and message from button or form
    const phone = button.getAttribute('data-phone') || 
                 button.closest('form')?.querySelector('[name="phone"]')?.value;
    const message = button.getAttribute('data-message') || 
                   button.closest('form')?.querySelector('[name="message"]')?.value;
    const debugId = this.generateDebugId();
    this.debug('btn:handleSend', { phone, messageLen: message?.length, debugId });

    if (!phone || !message) {
      alert('Phone number and message are required');
      return;
    }

    if (this.status !== 'connected') {
      alert('Please connect WhatsApp first');
      this.showQRModal();
      return;
    }

    try {
      const response = await this.sendMessageToBackground('sendMessage', {
        phone: phone,
        message: message,
        debugId,
      });

      // Dispatch a DOM event so the CRM UI can react (success/failure)
      const evt = new CustomEvent('crm-whatsapp-send', { detail: { success: !!response?.success, error: response?.error, debugId } });
      document.dispatchEvent(evt);
      this.debug('bg:sendMessage:response', { response, debugId });

      if (!response.success && response.error) {
        alert('Failed to send message: ' + response.error);
      }
    } catch (error) {
      const evt = new CustomEvent('crm-whatsapp-send', { detail: { success: false, error: error.message } });
      document.dispatchEvent(evt);
      this.debug('bg:sendMessage:error', { error: error?.message, debugId });
      alert('Error sending message: ' + error.message);
    }
  }

  sendMessageToBackground(action, data = {}) {
    return new Promise((resolve, reject) => {
      const payload = { action, ...data };
      this.debug('bg:message:send', payload);
      chrome.runtime.sendMessage(payload, (response) => {
        if (chrome.runtime.lastError) {
          this.debug('bg:message:error', { error: chrome.runtime.lastError.message });
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          this.debug('bg:message:recv', response);
          resolve(response);
        }
      });
    });
  }

  // Utilities
  debug(tag, data) {
    if (!this.debugEnabled) return;
    try {
      console.log('[CRM WhatsApp]', tag, data || '');
    } catch (e) {}
  }

  generateDebugId() {
    return 'dbg-' + Math.random().toString(36).slice(2) + Date.now().toString(36);
  }
}

// Initialize the integration
new CRMWhatsAppIntegration(); 