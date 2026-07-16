#!/bin/bash
# =============================================================
# ResumeAtlas — Oracle Cloud Free Tier Setup Script
# Run this once on a fresh Ubuntu 22.04 ARM VM
# =============================================================

set -e

echo "🚀 ResumeAtlas — Oracle Cloud Setup"
echo "====================================="

# ── 1. System update ─────────────────────────────────────────
echo "📦 Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

# ── 2. Install Docker ────────────────────────────────────────
echo "🐳 Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg lsb-release

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker

echo "✅ Docker $(docker --version) installed"

# ── 3. Open firewall ports ───────────────────────────────────
echo "🔓 Configuring firewall..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80   -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443  -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo netfilter-persistent save

# ── 4. Clone the repo ────────────────────────────────────────
echo "📥 Cloning ResumeLens repository..."
cd ~
git clone https://github.com/itsrajdeep/ResumeLens.git
cd ResumeLens

# ── 5. Configure environment ─────────────────────────────────
echo ""
echo "🔑 Environment Configuration"
echo "----------------------------"
cp .env.example .env

read -p "Enter your GEMINI_API_KEY: " GEMINI_KEY
read -s -p "Enter a secure POSTGRES_PASSWORD: " PG_PASS
echo ""

sed -i "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=${GEMINI_KEY}/" .env
sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${PG_PASS}/" .env

echo "✅ .env configured"

# ── 6. Start services ────────────────────────────────────────
echo "🐳 Starting all services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo ""
echo "✅ ResumeAtlas is running!"
echo ""
echo "   API docs  →  http://$(curl -s ifconfig.me):8000/docs"
echo "   Frontend  →  http://$(curl -s ifconfig.me):3000"
echo ""
echo "Trigger the first crawl:"
echo "   curl -X POST http://$(curl -s ifconfig.me):8000/api/crawl/trigger"
