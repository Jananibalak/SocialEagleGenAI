#!/bin/bash

echo "🚀 EduPath Frontend - Quick Start Script"
echo "========================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file. Please update REACT_APP_API_URL if needed."
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your API URL"
echo "2. Run: npm start"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For detailed instructions, see SETUP_GUIDE.md"
echo ""
