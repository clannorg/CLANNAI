# Web Apps Deployment

## Connecting to the WebApp VM (AWS EC2)

### **SSH Access**

**Instance:**  
- Name: `webapp-t3`
- Instance ID: `i-0b0abaf6fc947105d`
- Public IP: `52.214.173.0`
- OS: Ubuntu 22.04 LTS (Jammy Jellyfish)
- Instance Type: t3.micro
- Region: eu-west-1 (Europe - Ireland)

**SSH Key:**  
- Private key file: `~/.ssh/clannai-server-key.pem`
- Key name (in AWS): `clannai-server-key`

**Default SSH User:**  
- `ubuntu` (for Ubuntu AMIs)

**SSH Command:**
```bash
ssh -i ~/.ssh/clannai-server-key.pem ubuntu@52.214.173.0
```

### **DNS Configuration**
- `clannai.com` → 52.214.173.0
- `api.clannai.com` → 52.214.173.0

### **Current Applications**
- **Old App**: `web-app-clannai` (client + server) - POC deployment target
- **New App**: `1-clann-webapp` (frontend + backend) - Future deployment

### **Devopness Server Details**
- Server Name: `2024-11-28-webapp-clann`
- Cloud Provider: Amazon Web Services
- Disk Size: 60 GB
- Max Parallel Actions: 2
- Status: Running
- Created: November 28, 2024