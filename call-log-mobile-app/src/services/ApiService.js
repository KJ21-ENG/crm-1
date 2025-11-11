import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

class ApiService {
  constructor() {
    // Default to production CRM base URL; can be overridden via AsyncStorage 'server_url'
    this.baseURL = 'https://eshin.in';
    this.sessionId = null;
  }

  // Initialize API service with stored session
  async init() {
    try {
      const serverUrl = await AsyncStorage.getItem('server_url');
      const sessionId = await SecureStore.getItemAsync('session_id');
      
      // If a server URL was previously stored, honor it; otherwise keep default
      if (serverUrl) {
        this.baseURL = serverUrl;
      }
      
      if (sessionId) {
        this.sessionId = sessionId;
      }
      
      console.log('ApiService initialized:', { 
        baseURL: this.baseURL, 
        hasSession: !!this.sessionId 
      });
    } catch (error) {
      console.error('Failed to initialize ApiService:', error);
    }
  }

  // Set base URL for API calls
  setBaseURL(url) {
    this.baseURL = url.replace(/\/$/, ''); // Remove trailing slash
  }

  // Set session ID for authenticated calls
  setSessionId(sessionId) {
    this.sessionId = sessionId;
  }

  // Clear session
  clearSession() {
    this.sessionId = null;
  }

  // Generic API call method
  async apiCall(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    // Add session cookie if available
    if (this.sessionId) {
      defaultHeaders['Cookie'] = `sid=${this.sessionId}`;
    }

    const config = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    console.log('API Call:', {
      url,
      method: config.method || 'GET',
      hasSession: !!this.sessionId,
    });

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText,
        });
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }

      const data = await response.json();
      console.log('API Response:', { endpoint, success: true });
      return data;
    } catch (error) {
      console.error('API Call Failed:', { endpoint, error: error.message });
      throw error;
    }
  }

  // Get list of documents with filters
  async getDocumentList(doctype, filters = {}, fields = [], limit = 20, order_by = null) {
    const body = {
      doctype,
      fields: fields.length > 0 ? JSON.stringify(fields) : undefined,
      filters: Object.keys(filters).length > 0 ? JSON.stringify(filters) : undefined,
      limit_page_length: limit,
    };

    if (order_by) {
      body.order_by = order_by;
    }

    // Remove undefined values
    Object.keys(body).forEach(key => {
      if (body[key] === undefined) {
        delete body[key];
      }
    });

    return this.apiCall('/api/method/frappe.client.get_list', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Get single document
  async getDocument(doctype, name) {
    return this.apiCall('/api/method/frappe.client.get', {
      method: 'POST',
      body: JSON.stringify({
        doctype,
        name,
      }),
    });
  }

  // Create new document
  async createDocument(doctype, data) {
    const doc = {
      doctype,
      ...data,
    };

    return this.apiCall('/api/method/frappe.client.insert', {
      method: 'POST',
      body: JSON.stringify({ doc }),
    });
  }

  // Update existing document
  async updateDocument(doctype, name, data) {
    const doc = {
      doctype,
      name,
      ...data,
    };

    return this.apiCall('/api/method/frappe.client.save', {
      method: 'POST',
      body: JSON.stringify({ doc }),
    });
  }

  // Delete document
  async deleteDocument(doctype, name) {
    return this.apiCall('/api/method/frappe.client.delete', {
      method: 'POST',
      body: JSON.stringify({
        doctype,
        name,
      }),
    });
  }

  // Call log specific methods
  async getCallLogs(filters = {}, limit = 50) {
    const defaultFields = [
      'name',
      'from',
      'to',
      'type',
      'status',
      'duration',
      'start_time',
      'end_time',
      'recording_url',
      'creation',
      'modified',
    ];

    // Add ordering to get newest call logs first
    const options = {
      fields: defaultFields,
      filters,
      limit_page_length: limit,
      order_by: 'start_time desc'
    };

    return this.getDocumentList('CRM Call Log', options.filters, options.fields, options.limit_page_length, options.order_by);
  }

  async createCallLog(callLogData) {
    return this.createDocument('CRM Call Log', callLogData);
  }

  // Mobile sync specific methods
  async syncCallLogs(callLogsArray) {
    return this.apiCall('/api/method/crm.api.mobile_sync.sync_call_logs', {
      method: 'POST',
      body: JSON.stringify({ call_logs_data: callLogsArray }),
    });
  }

  async getUserCallLogs(limit = 50, fromDate = null, toDate = null) {
    const params = { limit };
    if (fromDate) params.from_date = fromDate;
    if (toDate) params.to_date = toDate;

    return this.apiCall('/api/method/crm.api.mobile_sync.get_user_call_logs', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getSyncStats() {
    return this.apiCall('/api/method/crm.api.mobile_sync.get_sync_stats', {
      method: 'POST',
    });
  }

  async getUserProfile() {
    return this.apiCall('/api/method/crm.api.mobile_sync.get_user_profile', {
      method: 'POST',
    });
  }

  async testMobileSync() {
    return this.apiCall('/api/method/crm.api.mobile_sync.test_mobile_sync', {
      method: 'POST',
    });
  }

  async updateCallLog(name, callLogData) {
    return this.updateDocument('CRM Call Log', name, callLogData);
  }

  async getCallLog(name) {
    return this.getDocument('CRM Call Log', name);
  }

  // Search for contacts/leads by phone number
  async searchByPhone(phoneNumber) {
    try {
      // Clean phone number for search
      const cleanPhone = phoneNumber.replace(/[^\d+]/g, '');
      
      // Search in contacts and leads
      const [contactsResponse, leadsResponse] = await Promise.all([
        this.getDocumentList('Contact', {
          phone: ['like', `%${cleanPhone}%`],
        }, ['name', 'first_name', 'last_name', 'phone', 'mobile_no']),
        this.getDocumentList('Lead', {
          phone: ['like', `%${cleanPhone}%`],
        }, ['name', 'lead_name', 'phone', 'mobile_no']),
      ]);

      return {
        contacts: contactsResponse.message || [],
        leads: leadsResponse.message || [],
      };
    } catch (error) {
      console.error('Phone search failed:', error);
      return { contacts: [], leads: [] };
    }
  }

  // Test API connection
  async testConnection() {
    try {
      await this.apiCall('/api/method/ping');
      return true;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  }

  // Check if user is authenticated
  async isAuthenticated() {
    try {
      const sessionData = await SecureStore.getItemAsync('session_id');
      if (!sessionData) {
        return false;
      }
      
      // Validate the session with the server
      const validation = await this.validateSession();
      return validation.valid;
    } catch (error) {
      console.error('Authentication check failed:', error);
      return false;
    }
  }

  // Validate current session
  async validateSession() {
    try {
      const response = await this.apiCall('/api/method/frappe.auth.get_logged_user');
      return {
        valid: !!response.message,
        user: response.message,
      };
    } catch (error) {
      console.error('Session validation failed:', error);
      return { valid: false, user: null };
    }
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService; 