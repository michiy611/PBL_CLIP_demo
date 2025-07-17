"""
Google Sheets Logger for CLIP Image Search Demo
Simple logging to Google Sheets
"""

import os
import json
from datetime import datetime
from typing import List, Tuple, Optional
import streamlit as st

# Streamlit Cloud での Google Sheets API 使用
try:
    import gspread
    from google.oauth2.service_account import Credentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

class SheetsLogger:
    def __init__(self):
        self.fallback_logs = []
        self.gc = None
        self.worksheet = None
        self.session_cache = {}
        
        if SHEETS_AVAILABLE:
            try:
                self._init_sheets()
            except Exception as e:
                st.warning(f"Sheets initialization failed: {e}")
    
    def _init_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Streamlit Cloudでの認証
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                # Streamlit Cloud環境
                credentials_info = dict(st.secrets["gcp_service_account"])
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                self.gc = gspread.authorize(credentials)
                
                # スプレッドシートの開始/作成
                spreadsheet_name = "CLIP Search Logs"
                try:
                    spreadsheet = self.gc.open(spreadsheet_name)
                except gspread.SpreadsheetNotFound:
                    spreadsheet = self.gc.create(spreadsheet_name)
                
                # ワークシートの取得/作成
                try:
                    self.worksheet = spreadsheet.worksheet("Search Logs")
                except gspread.WorksheetNotFound:
                    self.worksheet = spreadsheet.add_worksheet(title="Search Logs", rows="1000", cols="20")
                    # ヘッダーを設定
                    headers = [
                        "timestamp", "session_id", "query_text", "correct_rank", 
                        "result_1_filename", "result_1_similarity", "result_1_category",
                        "result_2_filename", "result_2_similarity", "result_2_category",
                        "result_3_filename", "result_3_similarity", "result_3_category",
                        "result_4_filename", "result_4_similarity", "result_4_category",
                        "result_5_filename", "result_5_similarity", "result_5_category",
                        "result_6_filename", "result_6_similarity", "result_6_category",
                        "result_7_filename", "result_7_similarity", "result_7_category",
                        "result_8_filename", "result_8_similarity", "result_8_category",
                        "result_9_filename", "result_9_similarity", "result_9_category",
                        "result_10_filename", "result_10_similarity", "result_10_category"
                    ]
                    self.worksheet.append_row(headers)
                    
            else:
                # ローカル環境での認証
                if os.path.exists("service-account-key.json"):
                    scope = [
                        'https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    credentials = Credentials.from_service_account_file("service-account-key.json", scopes=scope)
                    self.gc = gspread.authorize(credentials)
                    
                    # 同様の処理...
                    spreadsheet_name = "CLIP Search Logs"
                    try:
                        spreadsheet = self.gc.open(spreadsheet_name)
                    except gspread.SpreadsheetNotFound:
                        spreadsheet = self.gc.create(spreadsheet_name)
                    
                    try:
                        self.worksheet = spreadsheet.worksheet("Search Logs")
                    except gspread.WorksheetNotFound:
                        self.worksheet = spreadsheet.add_worksheet(title="Search Logs", rows="1000", cols="20")
                        headers = [
                            "timestamp", "session_id", "query_text", "correct_rank", 
                            "result_1_filename", "result_1_similarity", "result_1_category",
                            "result_2_filename", "result_2_similarity", "result_2_category",
                            "result_3_filename", "result_3_similarity", "result_3_category",
                            "result_4_filename", "result_4_similarity", "result_4_category",
                            "result_5_filename", "result_5_similarity", "result_5_category",
                            "result_6_filename", "result_6_similarity", "result_6_category",
                            "result_7_filename", "result_7_similarity", "result_7_category",
                            "result_8_filename", "result_8_similarity", "result_8_category",
                            "result_9_filename", "result_9_similarity", "result_9_category",
                            "result_10_filename", "result_10_similarity", "result_10_category"
                        ]
                        self.worksheet.append_row(headers)
                
        except Exception as e:
            st.error(f"Google Sheets setup error: {e}")
    
    def log_search_query(self, query: str, results: List[Tuple]) -> str:
        """Log search query with results"""
        session_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()
        
        # Session cache for feedback
        self.session_cache[session_id] = {
            'timestamp': timestamp,
            'query': query,
            'results': results,
            'correct_rank': None
        }
        
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int]):
        """Log user feedback (correct rank or None for no correct answer)"""
        if session_id not in self.session_cache:
            st.error("Session not found")
            return
        
        session_data = self.session_cache[session_id]
        session_data['correct_rank'] = correct_rank
        
        # Prepare row data
        row_data = [
            session_data['timestamp'],
            session_id,
            session_data['query'],
            correct_rank if correct_rank is not None else "no_correct_answer"
        ]
        
        # Add results data (up to 10 results)
        results = session_data['results']
        for i in range(10):
            if i < len(results):
                similarity, image_id, filename, category, description, file_path = results[i]
                row_data.extend([filename, f"{similarity:.3f}", category])
            else:
                row_data.extend(["", "", ""])
        
        # Log to Google Sheets
        if self.worksheet:
            try:
                self.worksheet.append_row(row_data)
                st.success("✅ Logged to Google Sheets")
            except Exception as e:
                st.error(f"Sheets logging error: {e}")
                # Fallback to local storage
                self.fallback_logs.append({
                    'timestamp': session_data['timestamp'],
                    'session_id': session_id,
                    'query': session_data['query'],
                    'correct_rank': correct_rank,
                    'results': results
                })
        else:
            # Fallback to local storage
            self.fallback_logs.append({
                'timestamp': session_data['timestamp'],
                'session_id': session_id,
                'query': session_data['query'],
                'correct_rank': correct_rank,
                'results': results
            })
            st.info("📝 Logged locally (Sheets unavailable)")
    
    def get_session_count(self) -> int:
        """Get total session count"""
        return len(self.session_cache)
    
    def get_feedback_count(self) -> int:
        """Get feedback count"""
        return len([s for s in self.session_cache.values() if s['correct_rank'] is not None])

# グローバルインスタンス
search_logger = SheetsLogger() 