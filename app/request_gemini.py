import sys

from dotenv import load_dotenv
load_dotenv()

import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
sys.stdout.write(GEMINI_API_KEY)