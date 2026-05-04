import json
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Response import handle_maintenance_chat

if __name__ == '__main__':
    payload = json.load(sys.stdin)
    message = payload.get('message', '')
    session_id = payload.get('sessionId', 'default')
    result = handle_maintenance_chat(message, session_id)
    print(result)
