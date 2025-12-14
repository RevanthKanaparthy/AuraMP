#!/usr/bin/env python
import os
import subprocess
import sys

# Set environment variable
os.environ['SKIP_EMBEDDINGS'] = '1'

# Run uvicorn
if __name__ == '__main__':
    subprocess.run([
        sys.executable, '-m', 'uvicorn',
        'backend_complete:app',
        '--host', '0.0.0.0',
        '--port', '8000',
        '--no-access-log'
    ])
