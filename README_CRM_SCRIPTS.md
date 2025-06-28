# 🚀 Frappe CRM Development Scripts

This directory contains automated scripts to manage your Frappe CRM development environment.

## 📋 Available Scripts

### 🟢 `./start_crm_dev.sh` - Start All Services
**One-click startup for your entire CRM development environment**

**What it does:**
- ✅ Starts MariaDB database
- ✅ Starts Redis (default + cache + queue instances)  
- ✅ Starts Frappe Bench backend server
- ✅ Starts Vue.js frontend development server with hot-reload
- ✅ Runs everything in background screen sessions
- ✅ Verifies all services are running
- ✅ Shows you access URLs and login credentials

**Usage:**
```bash
./start_crm_dev.sh
```

**After running, access your CRM at:**
- 🔥 **Development (Hot Reload):** http://127.0.0.1:8080
- 🌐 **Production Build:** http://127.0.0.1:8000/crm
- ⚙️ **Admin Panel:** http://127.0.0.1:8000

---

### 🔴 `./stop_crm_dev.sh` - Stop All Services
**Gracefully shut down your entire CRM development environment**

**What it does:**
- 🛑 Stops frontend development server
- 🛑 Stops Frappe Bench backend
- 🛑 Stops Redis cache and queue instances
- 🛑 Optionally stops MariaDB and default Redis
- 🧹 Cleans up screen sessions

**Usage:**
```bash
./stop_crm_dev.sh
```

---

### 📊 `./status_crm_dev.sh` - Check Status
**Quick status check of all CRM services**

**What it shows:**
- 📊 Status of each service (running/stopped)
- 📱 Access URLs (if services are running)
- 📺 Active screen sessions
- 🎯 Overall environment status

**Usage:**
```bash
./status_crm_dev.sh
```

---

## 🔄 Daily Development Workflow

### **Starting Development (After Reboot)**
```bash
# 1. Navigate to project directory
cd /Volumes/MacSSD/Development/CursorAI_Project/crm-1

# 2. Start everything with one command
./start_crm_dev.sh

# 3. Open browser and start coding!
# Development URL: http://127.0.0.1:8080
```

### **Checking Status**
```bash
./status_crm_dev.sh
```

### **Stopping Development**
```bash
./stop_crm_dev.sh
```

---

## 🖥️ Screen Sessions Management

The scripts use **screen sessions** to run services in the background:

### **View Logs:**
```bash
# View Frappe Bench logs
screen -r frappe_bench

# View Frontend Dev Server logs  
screen -r crm_frontend

# Exit screen session (without stopping service)
# Press: Ctrl+A, then D
```

### **List All Sessions:**
```bash
screen -ls
```

### **Stop Specific Session:**
```bash
screen -S frappe_bench -X quit
screen -S crm_frontend -X quit
```

---

## 🔐 Login Credentials

**Username:** `Administrator`  
**Password:** `admin`

---

## 🛠️ Development Paths

### **Frontend Development:**
```
frappe-bench/apps/crm/frontend/src/
├── components/     # Vue.js components
├── pages/         # CRM pages (Leads, Deals, etc.)
├── stores/        # State management
└── App.vue        # Main app
```

### **Backend Development:**
```
frappe-bench/apps/crm/crm/
├── api/           # API endpoints
├── fcrm/          # DocTypes (database models)
└── hooks.py       # App configuration
```

---

## 🚨 Troubleshooting

### **Script Permission Error:**
```bash
chmod +x start_crm_dev.sh stop_crm_dev.sh status_crm_dev.sh
```

### **Port Already in Use:**
- Run `./stop_crm_dev.sh` first
- Or check `./status_crm_dev.sh` to see what's running

### **Database Connection Issues:**
```bash
# Restart MariaDB
brew services restart mariadb
```

### **Frontend Not Loading:**
```bash
# Navigate to CRM app and rebuild
cd /Volumes/MacSSD/Development/CursorAI_Project/frappe-bench/apps/crm
yarn dev
```

### **Manual Service Management:**
```bash
# View running processes
ps aux | grep -E "(frappe|bench|redis|mariadb)"

# Kill specific process
kill -9 <process_id>
```

---

## 💡 Pro Tips

1. **Bookmark Development URL:** http://127.0.0.1:8080
2. **Use Hot Reload:** Frontend changes reflect instantly at dev URL
3. **Check Status First:** Always run `./status_crm_dev.sh` before starting
4. **Clean Shutdown:** Use `./stop_crm_dev.sh` instead of Ctrl+C
5. **Screen Sessions:** Learn basic screen commands for debugging

---

## 🎯 Next Steps

1. **Test the scripts** - Run `./start_crm_dev.sh` and verify everything works
2. **Bookmark URLs** - Save development and production URLs
3. **Start customizing** - Modify frontend components in `/frontend/src/`
4. **Create features** - Add new pages, modify existing ones
5. **Build your CRM** - Remove unwanted features, add client requirements

---

**Happy Coding! 🚀** 