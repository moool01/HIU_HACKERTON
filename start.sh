#!/bin/bash

# 1. React 앱 빌드
cd frontend
npm install
npm run build

# 2. Flask 백엔드 실행
cd ..
pip install -r requirements.txt
python backend/app.py
