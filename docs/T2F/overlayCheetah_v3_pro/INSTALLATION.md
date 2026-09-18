# Overlay Cheetah V3 PRO - Installation Guide

**Version:** 3.1.0-pro  
**Release:** December 2025  
**Target:** Enterprise & Production Environments  

---

## 🚀 Quick Start Installation

### Minimum Requirements
- **Python:** 3.8+ (Python 3.9+ recommended for optimal performance)
- **Operating System:** Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 1GB available space (includes cache and logs)
- **Network:** Internet connection for initial setup and LLM integrations

### Basic Installation (Recommended)

1. **Download Overlay Cheetah V3 PRO**
   ```bash
   # Extract the commercial release package
   cd overlayCheetah_v3_pro/
   ```

2. **Install Core Dependencies**
   ```bash
   # Install required packages
   pip install -r requirements.txt
   
   # Alternative: Install core dependencies only
   pip install pyyaml jinja2 psutil requests pillow
   ```

3. **Verify Installation**
   ```bash
   # Run preflight checks
   python overlay_cheetah_v3_pro.py --preflight
   
   # Run self-tests
   python overlay_cheetah_v3_pro.py --test
   ```

4. **Performance Validation**
   ```bash
   # Test performance
   python overlay_cheetah_v3_pro.py --benchmark --warm
   ```

---

## 🔧 Detailed Installation

### Step 1: Environment Preparation

#### Python Environment Setup
```bash
# Create virtual environment (recommended)
python -m venv cheetah_v3_env

# Activate environment
# Windows:
cheetah_v3_env\Scripts\activate
# macOS/Linux:
source cheetah_v3_env/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### System Dependencies

**Windows:**
```powershell
# Install Git (if not present)
winget install Git.Git

# Install Node.js (for enhanced features)
winget install OpenJS.NodeJS

# Install Docker Desktop (optional, for containerization)
winget install Docker.DockerDesktop
```

**macOS:**
```bash
# Install Homebrew (if not present)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install git node docker
```

**Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install git nodejs npm docker.io python3-dev build-essential

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

### Step 2: Core Installation

#### Install Overlay Cheetah V3 PRO
```bash
# Navigate to installation directory
cd /path/to/overlayCheetah_v3_pro/

# Install all dependencies
pip install -r requirements.txt

# Or install minimal dependencies
pip install pyyaml>=6.0 jinja2>=3.1.0 psutil>=5.8.0 requests>=2.28.0
```

#### Optional AI/LLM Integration
```bash
# For Google Gemini support
pip install google-generativeai>=0.3.0

# For Ollama integration
pip install ollama>=0.1.0

# For OpenAI integration
pip install openai>=1.0.0
```

### Step 3: Configuration

#### Environment Variables (Optional)
```bash
# Create .env file for configuration
cat > .env << EOF
# LLM API Keys (optional)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Performance Configuration
CHEETAH_CACHE_SIZE=1024
CHEETAH_MONITOR_INTERVAL=1.0
CHEETAH_LOG_LEVEL=INFO

# Enterprise Features
CHEETAH_ENABLE_TELEMETRY=true
CHEETAH_ENABLE_MONITORING=true
EOF
```

#### Directory Structure Setup
```bash
# Create necessary directories
mkdir -p cache logs reports out templates/custom

# Set permissions (Unix-like systems)
chmod 755 cache logs reports out
chmod 644 overlay_cheetah_v3_pro.py
```

### Step 4: Validation

#### Comprehensive System Check
```bash
# Run preflight validation
python overlay_cheetah_v3_pro.py --preflight

# Expected output should show:
# ✓ Python interpreter available
# ✓ Required packages installed
# ✓ System resources sufficient
# ✓ Disk space available
```

#### Performance Benchmark
```bash
# Run performance validation
python overlay_cheetah_v3_pro.py --benchmark --cold

# Expected timing (varies by system):
# Cold start: 30-60 seconds
# Warm start: 20-45 seconds
```

#### Self-Test Suite
```bash
# Run all self-tests
python overlay_cheetah_v3_pro.py --test

# Expected results: All tests should PASS
# ✓ Path configuration test passed
# ✓ Cache test passed
# ✓ Template generation test passed
# ✓ Resource monitoring test passed
# ✓ Preflight validator test passed
```

---

## 🐳 Docker Installation (Enterprise)

### Docker Deployment

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create cache and logs directories
RUN mkdir -p cache logs reports out

# Set permissions
RUN chmod +x overlay_cheetah_v3_pro.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python overlay_cheetah_v3_pro.py --preflight || exit 1

# Default command
CMD ["python", "overlay_cheetah_v3_pro.py"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t overlay-cheetah-v3-pro:latest .

# Run with volume mounts
docker run -d \
    --name cheetah-v3-pro \
    -v $(pwd)/cache:/app/cache \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/reports:/app/reports \
    -e CHEETAH_ENABLE_MONITORING=true \
    overlay-cheetah-v3-pro:latest

# Run benchmark
docker run --rm \
    -v $(pwd)/cache:/app/cache \
    overlay-cheetah-v3-pro:latest \
    python overlay_cheetah_v3_pro.py --benchmark --warm
```

### Kubernetes Deployment (Advanced)

#### Create deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: overlay-cheetah-v3-pro
  labels:
    app: cheetah-v3-pro
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cheetah-v3-pro
  template:
    metadata:
      labels:
        app: cheetah-v3-pro
    spec:
      containers:
      - name: cheetah-v3-pro
        image: overlay-cheetah-v3-pro:latest
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        volumeMounts:
        - name: cache-volume
          mountPath: /app/cache
        - name: logs-volume
          mountPath: /app/logs
        env:
        - name: CHEETAH_ENABLE_MONITORING
          value: "true"
        - name: CHEETAH_LOG_LEVEL
          value: "INFO"
      volumes:
      - name: cache-volume
        emptyDir: {}
      - name: logs-volume
        emptyDir: {}
```

---

## ⚡ Performance Optimization

### System Optimization

#### Windows Performance Tuning
```powershell
# Increase Python buffer sizes
setx PYTHONUNBUFFERED 1
setx PYTHONDONTWRITEBYTECODE 1

# Optimize Windows for performance
# Run as Administrator
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
```

#### Linux/macOS Performance Tuning
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python performance
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=random

# Add to ~/.bashrc or ~/.zshrc for persistence
```

### Cache Optimization
```bash
# Pre-warm cache for better performance
python overlay_cheetah_v3_pro.py --benchmark --warm

# Clear cache if needed
rm -rf cache/*
python overlay_cheetah_v3_pro.py --benchmark --cold
```

---

## 🔍 Troubleshooting Installation

### Common Issues and Solutions

#### Issue: "Module not found" errors
```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Or install specific missing module
pip install module_name
```

#### Issue: Permission denied errors (Unix-like systems)
```bash
# Solution: Fix permissions
chmod +x overlay_cheetah_v3_pro.py
chmod 755 . cache logs reports out
```

#### Issue: Python version incompatibility
```bash
# Solution: Check Python version
python --version

# If below 3.8, upgrade Python or use pyenv
pyenv install 3.9.18
pyenv local 3.9.18
```

#### Issue: Performance issues
```bash
# Solution: Check system resources
python overlay_cheetah_v3_pro.py --preflight

# Check available memory and disk space
# Ensure at least 2GB RAM and 1GB disk space available
```

#### Issue: Network connectivity problems
```bash
# Solution: Test network connectivity
ping google.com

# Check firewall settings
# Ensure outbound HTTPS (443) is allowed for LLM APIs
```

### Diagnostic Commands
```bash
# Full system diagnostic
python overlay_cheetah_v3_pro.py --preflight --verbose

# Performance diagnostic
python overlay_cheetah_v3_pro.py --benchmark --cold

# Self-test diagnostic
python overlay_cheetah_v3_pro.py --test

# Check Python environment
python -c "import sys; print(sys.path); print(sys.version)"
```

---

## 📊 Verification and Testing

### Installation Verification Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] All required dependencies installed successfully
- [ ] Preflight checks pass without critical errors
- [ ] Self-tests complete successfully (5/5 passed)
- [ ] Benchmark completes in expected time range (30-80s)
- [ ] Cache directory is writable
- [ ] Logs directory is writable
- [ ] Network connectivity available (for LLM features)

### Performance Validation
```bash
# Expected performance ranges (varies by system):
# Cold start: 30-80 seconds
# Warm start: 20-50 seconds
# Memory usage: 1-3GB peak
# Cache efficiency: >80% hit rate after warmup
```

### Post-Installation Testing
```bash
# Test core functionality
python overlay_cheetah_v3_pro.py --test

# Test performance
python overlay_cheetah_v3_pro.py --benchmark --warm

# Test GUI (if running in desktop environment)
python overlay_cheetah_v3_pro.py

# Test CLI interface
python overlay_cheetah_v3_pro.py --help
```

---

## 🚀 Next Steps

### After Successful Installation

1. **Read Documentation**: Review README.md and API documentation
2. **Run Benchmarks**: Establish baseline performance metrics
3. **Configure Environment**: Set up LLM API keys and preferences
4. **Test Integration**: Integrate with your development workflow
5. **Monitor Performance**: Set up performance tracking and alerting

### Enterprise Deployment

1. **Production Setup**: Configure for production environment
2. **Monitoring Integration**: Set up Prometheus/Grafana dashboards
3. **Backup Strategy**: Configure cache and logs backup
4. **Security Review**: Implement enterprise security policies
5. **Team Training**: Train development team on features and best practices

### Support Resources

- **Documentation**: Complete guides in `/docs` folder
- **Benchmarks**: Performance reports in `/benchmarks` folder
- **Examples**: Sample configurations and use cases
- **Support**: Enterprise support contact information

---

**Installation Complete!** 🎉

Your Overlay Cheetah V3 PRO installation is ready for production use.

For questions or enterprise support, contact our support team.