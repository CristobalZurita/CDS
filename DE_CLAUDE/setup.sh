#!/bin/bash

# Diagnostic System - Initialization Script
# This script sets up the project for first-time use

set -e  # Exit on error

echo "======================================"
echo "🎹 Diagnostic System - Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create environment file
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your actual configuration${NC}"
else
    echo -e "${YELLOW}⚠ .env already exists${NC}"
fi
echo ""

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads
echo -e "${GREEN}✓ Uploads directory created${NC}"
echo ""

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs
chmod 755 logs
echo -e "${GREEN}✓ Logs directory created${NC}"
echo ""

# Initialize database
echo "Initializing database..."
python3 << EOF
from backend_api import Base, engine
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ Database initialized")
EOF
echo ""

# Seed database (optional)
read -p "Do you want to seed the database with sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Seeding database..."
    python3 << EOF
import asyncio
from sqlalchemy.orm import Session
from backend_api import SessionLocal, InstrumentModel

db = SessionLocal()

sample_instruments = [
    {
        "brand": "Moog",
        "model": "Minimoog Model D",
        "year": 1970,
        "type": "Analog Synthesizer",
        "estimated_value": 5000000,
        "complexity_tier": "vintage",
        "template_json": {
            "keys": 44,
            "knobs": 24,
            "switches": 18,
            "wheels": 2
        }
    },
    {
        "brand": "Roland",
        "model": "Jupiter-8",
        "year": 1981,
        "type": "Analog Synthesizer",
        "estimated_value": 8000000,
        "complexity_tier": "vintage",
        "template_json": {
            "keys": 61,
            "knobs": 36,
            "buttons": 24,
            "sliders": 8
        }
    },
    {
        "brand": "Korg",
        "model": "MS-20",
        "year": 1978,
        "type": "Semi-Modular Synthesizer",
        "estimated_value": 1500000,
        "complexity_tier": "complex",
        "template_json": {
            "keys": 37,
            "knobs": 19,
            "switches": 6,
            "cv_gate": 12
        }
    }
]

for inst_data in sample_instruments:
    existing = db.query(InstrumentModel).filter(
        InstrumentModel.brand == inst_data["brand"],
        InstrumentModel.model == inst_data["model"]
    ).first()
    
    if not existing:
        instrument = InstrumentModel(**inst_data)
        db.add(instrument)
        print(f"Added: {inst_data['brand']} {inst_data['model']}")

db.commit()
db.close()
print("✓ Database seeded")
EOF
    echo -e "${GREEN}✓ Database seeded with sample data${NC}"
fi
echo ""

# Create systemd service file (optional)
read -p "Do you want to create a systemd service file? (Linux only) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/diagnostic-system.service"
    CURRENT_DIR=$(pwd)
    CURRENT_USER=$(whoami)
    
    echo "Creating systemd service file..."
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Diagnostic System API
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/uvicorn backend_api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo -e "${GREEN}✓ Systemd service file created${NC}"
    echo ""
    echo "To enable and start the service:"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable diagnostic-system"
    echo "  sudo systemctl start diagnostic-system"
fi
echo ""

# Test installation
echo "Testing installation..."
python3 << EOF
try:
    import fastapi
    import sqlalchemy
    import cv2
    import PIL
    print("✓ All required packages are importable")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF
echo ""

# Final instructions
echo "======================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your .env file with actual configuration:"
echo "   nano .env"
echo ""
echo "2. Start the development server:"
echo "   source venv/bin/activate"
echo "   uvicorn backend_api:app --reload"
echo ""
echo "3. Access the application:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""
echo "4. For production deployment, see DOCUMENTATION.md"
echo ""
echo "======================================"
echo -e "${YELLOW}⚠ Remember to:${NC}"
echo "  - Configure your .env file"
echo "  - Set up SSL/TLS in production"
echo "  - Configure backups"
echo "  - Review security settings"
echo "======================================"
