#!/bin/bash

# This script will be run on the EC2 instance to install the application
# We'll use AWS Systems Manager Session Manager instead of SSH

echo "Installing String Analyzer application..."

# Create the application files directly on the instance
cd /opt/string-analyzer

# Create main.py
cat > main.py << 'EOF'