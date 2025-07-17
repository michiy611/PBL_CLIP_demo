"""
Google Sheets Logger for CLIP Image Search Demo
Simple logging to Google Sheets with debug information
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
        self.debug_info = []
        
        self._add_debug("📊 SheetsLogger initialized")
        
        if SHEETS_AVAILABLE:
            self._add_debug("✅ Google Sheets libraries available")
            try:
                self._init_sheets()
            except Exception as e:
                self._add_debug(f"❌ Sheets initialization failed: {e}")
                st.warning(f"Sheets initialization failed: {e}")
        else:
            self._add_debug("❌ Google Sheets libraries not available")
    
    def _add_debug(self, message: str):
        """Add debug message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        debug_msg = f"[{timestamp}] {message}"
        self.debug_info.append(debug_msg)
        print(debug_msg)  # Console output for debugging
    
    def get_debug_info(self) -> List[str]:
        """Get all debug information"""
        return self.debug_info
    
    def _init_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            self._add_debug("🔧 Starting Google Sheets initialization...")
            
            # Streamlit Cloudでの認証
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                self._add_debug("🔑 Found Streamlit secrets")
                # Streamlit Cloud環境
                credentials_info = dict(st.secrets["gcp_service_account"])
                self._add_debug(f"📋 Project ID: {credentials_info.get('project_id', 'Not found')}")
                
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                self._add_debug("✅ Credentials created successfully")
                
                self.gc = gspread.authorize(credentials)
                self._add_debug("✅ Google Sheets client authorized")
                
                # スプレッドシートの開始/作成
                spreadsheet_name = "CLIP Search Logs"
                self._add_debug(f"📊 Looking for spreadsheet: {spreadsheet_name}")
                
                try:
                    spreadsheet = self.gc.open(spreadsheet_name)
                    self._add_debug(f"✅ Found existing spreadsheet: {spreadsheet_name}")
                except gspread.SpreadsheetNotFound:
                    self._add_debug(f"📝 Creating new spreadsheet: {spreadsheet_name}")
                    spreadsheet = self.gc.create(spreadsheet_name)
                    self._add_debug(f"✅ Created new spreadsheet: {spreadsheet_name}")
                
                # ワークシートの取得/作成
                worksheet_name = "Search Logs"
                self._add_debug(f"📄 Looking for worksheet: {worksheet_name}")
                
                try:
                    self.worksheet = spreadsheet.worksheet(worksheet_name)
                    self._add_debug(f"✅ Found existing worksheet: {worksheet_name}")
                except gspread.WorksheetNotFound:
                    self._add_debug(f"📝 Creating new worksheet: {worksheet_name}")
                    self.worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
                    self._add_debug(f"✅ Created new worksheet: {worksheet_name}")
                    
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
                    self._add_debug("✅ Headers added to worksheet")
                    
            else:
                self._add_debug("🔑 No Streamlit secrets found, trying local file...")
                # ローカル環境での認証
                if os.path.exists("service-account-key.json"):
                    self._add_debug("📁 Found local service account file")
                    scope = [
                        'https://spreadsheets.google.com/feeds',
                        'https://www.googleapis.com/auth/drive'
                    ]
                    credentials = Credentials.from_service_account_file("service-account-key.json", scopes=scope)
                    self.gc = gspread.authorize(credentials)
                    self._add_debug("✅ Local credentials authorized")
                    
                    # 同様の処理...
                    spreadsheet_name = "CLIP Search Logs"
                    try:
                        spreadsheet = self.gc.open(spreadsheet_name)
                        self._add_debug(f"✅ Found existing spreadsheet (local): {spreadsheet_name}")
                    except gspread.SpreadsheetNotFound:
                        spreadsheet = self.gc.create(spreadsheet_name)
                        self._add_debug(f"✅ Created new spreadsheet (local): {spreadsheet_name}")
                    
                    try:
                        self.worksheet = spreadsheet.worksheet("Search Logs")
                        self._add_debug("✅ Found existing worksheet (local)")
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
                        self._add_debug("✅ Headers added to worksheet (local)")
                else:
                    self._add_debug("❌ No service account file found")
                
        except Exception as e:
            self._add_debug(f"❌ Google Sheets setup error: {e}")
            st.error(f"Google Sheets setup error: {e}")
    
    def log_search_query(self, query: str, results: List[Tuple]) -> str:
        """Log search query with results"""
        session_id = f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()
        
        self._add_debug(f"🔍 Logging search query: '{query}' (Session: {session_id})")
        
        # Session cache for feedback
        self.session_cache[session_id] = {
            'timestamp': timestamp,
            'query': query,
            'results': results,
            'correct_rank': None
        }
        
        self._add_debug(f"📝 Session cached. Total sessions: {len(self.session_cache)}")
        
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int]):
        """Log user feedback (correct rank or None for no correct answer)"""
        self._add_debug(f"👤 Logging feedback for session: {session_id}, rank: {correct_rank}")
        
        if session_id not in self.session_cache:
            self._add_debug(f"❌ Session not found in cache: {session_id}")
            st.error("Session not found")
            return
        
        session_data = self.session_cache[session_id]
        session_data['correct_rank'] = correct_rank
        
        self._add_debug(f"📊 Preparing data for Google Sheets...")
        
        # Prepare row data
        row_data = [
            session_data['timestamp'],
            session_id,
            session_data['query'],
            correct_rank if correct_rank is not None else "no_correct_answer"
        ]
        
        # Add results data (up to 10 results)
        results = session_data['results']
        self._add_debug(f"📋 Processing {len(results)} search results...")
        
        for i in range(10):
            if i < len(results):
                similarity, image_id, filename, category, description, file_path = results[i]
                row_data.extend([filename, f"{similarity:.3f}", category])
                self._add_debug(f"   Result {i+1}: {filename} ({similarity:.3f}, {category})")
            else:
                row_data.extend(["", "", ""])
        
        # Try to write to Google Sheets with fresh connection
        try:
            self._add_debug("📤 Creating fresh connection for reliable write...")
            
            # Create fresh connection (same as test_connection)
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                credentials_info = dict(st.secrets["gcp_service_account"])
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                gc = gspread.authorize(credentials)
                
                # Access spreadsheet and worksheet
                spreadsheet_name = "CLIP Search Logs"
                spreadsheet = gc.open(spreadsheet_name)
                worksheet = spreadsheet.worksheet("Search Logs")
                
                self._add_debug("✅ Fresh connection established")
                
                # Write data
                self._add_debug(f"📤 Writing row with {len(row_data)} columns...")
                worksheet.append_row(row_data)
                
                self._add_debug("✅ Successfully logged to Google Sheets!")
                st.success("✅ Logged to Google Sheets")
                
            else:
                self._add_debug("❌ No secrets available for fresh connection")
                raise Exception("Streamlit secrets not available")
                
        except Exception as e:
            self._add_debug(f"❌ Fresh connection write failed: {e}")
            
            # Fallback: try original self.worksheet
            if self.worksheet:
                try:
                    self._add_debug("📤 Trying fallback to self.worksheet...")
                    self.worksheet.append_row(row_data)
                    self._add_debug("✅ Fallback write successful!")
                    st.success("✅ Logged to Google Sheets (fallback)")
                except Exception as e2:
                    self._add_debug(f"❌ Fallback write also failed: {e2}")
                    st.error(f"Sheets logging error: {e2}")
                    # Store in fallback logs
                    self._store_fallback_log(session_data, correct_rank, results)
            else:
                self._add_debug("❌ No worksheet available for fallback")
                st.error(f"Sheets logging error: {e}")
                # Store in fallback logs
                self._store_fallback_log(session_data, correct_rank, results)
    
    def get_session_count(self) -> int:
        """Get total session count"""
        return len(self.session_cache)
    
    def get_feedback_count(self) -> int:
        """Get feedback count"""
        return len([s for s in self.session_cache.values() if s['correct_rank'] is not None])
    
    def get_secrets_diagnostic(self) -> dict:
        """Detailed diagnostic of Streamlit secrets configuration"""
        diagnostic = {
            'streamlit_has_secrets': hasattr(st, 'secrets'),
            'gcp_section_exists': False,
            'required_fields_present': {},
            'field_values_safe': {},
            'missing_fields': [],
            'empty_fields': [],
            'diagnostic_message': ""
        }
        
        try:
            if hasattr(st, 'secrets'):
                diagnostic['streamlit_has_secrets'] = True
                self._add_debug("✅ st.secrets is available")
                
                # Check if gcp_service_account section exists
                if 'gcp_service_account' in st.secrets:
                    diagnostic['gcp_section_exists'] = True
                    self._add_debug("✅ gcp_service_account section found")
                    
                    # Required fields for Google Sheets API
                    required_fields = [
                        'type', 'project_id', 'private_key_id', 'private_key',
                        'client_email', 'client_id', 'auth_uri', 'token_uri',
                        'auth_provider_x509_cert_url', 'client_x509_cert_url'
                    ]
                    
                    gcp_secrets = st.secrets["gcp_service_account"]
                    
                    for field in required_fields:
                        if field in gcp_secrets:
                            diagnostic['required_fields_present'][field] = True
                            value = gcp_secrets[field]
                            if value and str(value).strip():
                                # Store safe representation of field values
                                if field == 'private_key':
                                    diagnostic['field_values_safe'][field] = f"Present ({len(str(value))} chars)"
                                elif field == 'client_email':
                                    diagnostic['field_values_safe'][field] = str(value)
                                elif field == 'project_id':
                                    diagnostic['field_values_safe'][field] = str(value)
                                else:
                                    diagnostic['field_values_safe'][field] = f"Present ({len(str(value))} chars)"
                                self._add_debug(f"✅ Field '{field}': Present")
                            else:
                                diagnostic['empty_fields'].append(field)
                                diagnostic['field_values_safe'][field] = "Empty"
                                self._add_debug(f"❌ Field '{field}': Empty")
                        else:
                            diagnostic['required_fields_present'][field] = False
                            diagnostic['missing_fields'].append(field)
                            self._add_debug(f"❌ Field '{field}': Missing")
                    
                    # Generate diagnostic message
                    if not diagnostic['missing_fields'] and not diagnostic['empty_fields']:
                        diagnostic['diagnostic_message'] = "✅ All required fields are present and non-empty"
                    else:
                        msg_parts = []
                        if diagnostic['missing_fields']:
                            msg_parts.append(f"Missing fields: {', '.join(diagnostic['missing_fields'])}")
                        if diagnostic['empty_fields']:
                            msg_parts.append(f"Empty fields: {', '.join(diagnostic['empty_fields'])}")
                        diagnostic['diagnostic_message'] = "❌ " + "; ".join(msg_parts)
                        
                else:
                    diagnostic['gcp_section_exists'] = False
                    diagnostic['diagnostic_message'] = "❌ [gcp_service_account] section not found in secrets"
                    self._add_debug("❌ gcp_service_account section not found")
                    
            else:
                diagnostic['streamlit_has_secrets'] = False
                diagnostic['diagnostic_message'] = "❌ st.secrets is not available"
                self._add_debug("❌ st.secrets is not available")
                
        except Exception as e:
            diagnostic['diagnostic_message'] = f"❌ Error reading secrets: {e}"
            self._add_debug(f"❌ Error in secrets diagnostic: {e}")
            
        return diagnostic

    def test_connection(self) -> dict:
        """Test Google Sheets connection and return detailed status"""
        status = {
            'libraries_available': SHEETS_AVAILABLE,
            'secrets_found': False,
            'credentials_valid': False,
            'client_authorized': False,
            'spreadsheet_accessible': False,
            'worksheet_accessible': False,
            'can_write': False,
            'error_message': None
        }
        
        try:
            # Check if secrets are available
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                status['secrets_found'] = True
                self._add_debug("✅ Secrets found for connection test")
                
                # Test credentials
                credentials_info = dict(st.secrets["gcp_service_account"])
                scope = [
                    'https://spreadsheets.google.com/feeds',
                    'https://www.googleapis.com/auth/drive'
                ]
                credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
                status['credentials_valid'] = True
                self._add_debug("✅ Credentials valid")
                
                # Test client authorization
                gc = gspread.authorize(credentials)
                status['client_authorized'] = True
                self._add_debug("✅ Client authorized")
                
                # Test spreadsheet access
                spreadsheet_name = "CLIP Search Logs"
                try:
                    spreadsheet = gc.open(spreadsheet_name)
                    status['spreadsheet_accessible'] = True
                    self._add_debug(f"✅ Spreadsheet accessible: {spreadsheet_name}")
                    
                    # Test worksheet access
                    worksheet = spreadsheet.worksheet("Search Logs")
                    status['worksheet_accessible'] = True
                    self._add_debug("✅ Worksheet accessible")
                    
                    # Test write capability
                    test_data = ["TEST", datetime.now().isoformat(), "connection_test", "test_rank"]
                    # Add empty values for remaining columns (up to 34 columns total)
                    test_data.extend([""] * 30)
                    worksheet.append_row(test_data)
                    status['can_write'] = True
                    self._add_debug("✅ Write test successful")
                    
                except gspread.SpreadsheetNotFound:
                    self._add_debug(f"❌ Spreadsheet not found: {spreadsheet_name}")
                    status['error_message'] = f"Spreadsheet '{spreadsheet_name}' not found"
                except gspread.WorksheetNotFound:
                    self._add_debug("❌ Worksheet 'Search Logs' not found")
                    status['error_message'] = "Worksheet 'Search Logs' not found"
                except Exception as e:
                    self._add_debug(f"❌ Write test failed: {e}")
                    status['error_message'] = f"Write test failed: {e}"
                    
            else:
                self._add_debug("❌ No secrets found for connection test")
                status['error_message'] = "Streamlit secrets not found"
                
        except Exception as e:
            status['error_message'] = str(e)
            self._add_debug(f"❌ Connection test failed: {e}")
            
        return status

    def _store_fallback_log(self, session_data: dict, correct_rank: Optional[int], results: List):
        """Store log data in fallback storage"""
        self.fallback_logs.append({
            'timestamp': session_data['timestamp'],
            'session_id': session_data.get('session_id', 'unknown'),
            'query': session_data['query'],
            'correct_rank': correct_rank,
            'results': results
        })
        self._add_debug(f"📁 Logged to fallback storage. Total fallback logs: {len(self.fallback_logs)}")
        st.info("📝 Logged locally (Sheets unavailable)")

# グローバルインスタンス
search_logger = SheetsLogger() 