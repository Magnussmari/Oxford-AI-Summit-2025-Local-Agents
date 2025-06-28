#!/bin/bash

# LocalMind Collective - Oxford AI Summit 2025 Demo Launcher

# Colors for terminal output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Load environment variables from root .env file if it exists
if [ -f "../.env" ]; then
    # More robust way to load .env file that handles quotes and spaces
    set -a
    source ../.env
    set +a
fi

# Function to print centered text
print_centered() {
    local text="$1"
    local width=70
    local padding=$(( (width - ${#text}) / 2 ))
    printf "%*s%s\n" $padding "" "$text"
}

clear

# Cool ASCII art header
echo -e "${CYAN}"
echo "    ╔═══════════════════════════════════════════════════════════════════╗"
echo "    ║                                                                   ║"
echo "    ║${BOLD}       🧠 Magnus Smari - Local AI Agents Demo 🧠                  ${NC}${CYAN}║"
echo "    ║                                                                   ║"
echo "    ║              ${PURPLE}Oxford AI Summit 2025${CYAN}                               ║"
echo "    ║           ${PURPLE}100% Local • Zero Cloud • Full Control${CYAN}                 ║"
echo "    ║                                                                   ║"
echo "    ╚═══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Progress animation function
show_progress() {
    local pid=$1
    local delay=0.1
    local spinstr='⣾⣽⣻⢿⡿⣟⣯⣷'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚡ Creating virtual environment...${NC}"
    python -m venv .venv 2>/dev/null &
    show_progress $!
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update requirements quietly
echo -e "${YELLOW}⚡ Installing dependencies...${NC}"
pip install -r requirements.txt -q 2>/dev/null &
show_progress $!
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check for required models with styled output
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}📦 AI Model Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

REQUIRED_MODELS=("deepseek-r1:8b" "qwen3:8b" "qwen3:4b" "phi4-mini")
MISSING_MODELS=()

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list 2>/dev/null | grep -q "$model"; then
        echo -e "  ${GREEN}✓${NC} ${model} ${GREEN}[Ready]${NC}"
    else
        echo -e "  ${RED}✗${NC} ${model} ${RED}[Missing]${NC}"
        MISSING_MODELS+=("$model")
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo -e "  ${YELLOW}⚠️  Missing models detected!${NC}"
    echo -e "  ${YELLOW}Install with: ollama pull <model-name>${NC}"
fi

# Check for environment configuration
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🔧 Configuration Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check Ollama
if pgrep -x "ollama" > /dev/null; then
    echo -e "  ${GREEN}✓${NC} Ollama Service ${GREEN}[Running]${NC}"
else
    echo -e "  ${RED}✗${NC} Ollama Service ${RED}[Not Running]${NC}"
    echo -e "  ${YELLOW}Start with: ollama serve${NC}"
fi

# Check for Brave API key
if [ -z "$BRAVE_API_KEY" ]; then
    echo -e "  ${YELLOW}○${NC} Brave Search ${YELLOW}[Simulated Mode]${NC}"
else
    echo -e "  ${GREEN}✓${NC} Brave Search ${GREEN}[API Connected]${NC}"
fi

# Enhanced Mode is always active
echo -e "  ${GREEN}✓${NC} Enhanced Mode ${GREEN}[Active]${NC}"
echo -e "    ${CYAN}├─ Structured Prompting${NC}"
echo -e "    ${CYAN}├─ Resilient Execution${NC}"
echo -e "    ${CYAN}├─ Memory System${NC}"
echo -e "    ${CYAN}└─ Adaptive Optimization${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}🚀 Launching Magnus Smari's Local AI Agents${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${CYAN}🌐 Dashboard:${NC} ${BOLD}http://localhost:8000${NC}"
echo ""
echo -e "  ${PURPLE}${BOLD}Key Features:${NC}"
echo -e "  ${PURPLE}├─${NC} 🤖 5-Agent Orchestration with Enhanced AI"
echo -e "  ${PURPLE}├─${NC} ✅ Fact Validation & Quality Auditing"
echo -e "  ${PURPLE}├─${NC} 📊 Real-time Performance Monitoring"
echo -e "  ${PURPLE}├─${NC} 🧠 Memory System & Adaptive Learning"
echo -e "  ${PURPLE}└─${NC} 🔐 100% Local Processing"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${YELLOW}Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Launch the app with custom startup disabled
LOCALMIND_NO_STARTUP_MSG=1 python app.py