#!/usr/bin/env python
import asyncio
import os
import sys
import uvicorn

# Set environment variable
os.environ['SKIP_EMBEDDINGS'] = '1'
os.environ['LLM_PROVIDER'] = 'ollama'

# Set event loop policy for Windows compatibility with psycopg async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Run uvicorn
if __name__ == '__main__':
    # Import app after setting the policy
    from backend_complete import app
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
        log_config=None  # We are not using access logs
    )
