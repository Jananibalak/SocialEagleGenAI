#!/usr/bin/env python
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app import app

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 EDUPATH API SERVER")
    print("=" * 70)
    print("Server: http://localhost:5000")
    print("Health: http://localhost:5000/health")
    print("Docs: http://localhost:5000/docs")
    print("=" * 70)

    app.run(host='0.0.0.0', port=5000, debug=True)
