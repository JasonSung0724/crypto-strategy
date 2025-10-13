#!/usr/bin/env python3
"""
加密貨幣走勢分析桌面應用程式
啟動腳本
"""

import sys
import os

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from app import main

    print("🚀 啟動加密貨幣走勢分析桌面應用程式...")
    main()
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
    print("請確保已安裝所有必要的依賴:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 應用程式錯誤: {e}")
