"""
Cloud Logger Module - Google Cloud Logging Integration
Logs search queries, results, and user feedback to Google Cloud
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

# Google Cloud Logging用のクラス
class CloudSearchLogger:
    def __init__(self, use_cloud_logging: bool = True, project_id: str = None, credentials=None):
        """
        Initialize the cloud search logger
        
        Args:
            use_cloud_logging: Whether to use Google Cloud Logging (requires credentials)
            project_id: Google Cloud Project ID (auto-detected if None)
            credentials: Google Cloud credentials object (for Streamlit Cloud)
        """
        self.use_cloud_logging = use_cloud_logging
        self.fallback_file = "search_logs_fallback.jsonl"
        
        if use_cloud_logging:
            try:
                from google.cloud import logging as cloud_logging
                
                # Initialize client with custom credentials if provided
                if credentials:
                    self.cloud_client = cloud_logging.Client(project=project_id, credentials=credentials)
                else:
                    self.cloud_client = cloud_logging.Client(project=project_id)
                
                self.logger = self.cloud_client.logger("clip-search-demo")
                self._test_connection()
                print("✅ Google Cloud Logging connected successfully")
            except ImportError:
                print("⚠️ google-cloud-logging not installed, falling back to local file")
                self.use_cloud_logging = False
            except Exception as e:
                print(f"⚠️ Cloud Logging connection failed: {e}, falling back to local file")
                self.use_cloud_logging = False
        
        if not self.use_cloud_logging:
            self._ensure_fallback_file_exists()
    
    def _test_connection(self):
        """Test cloud logging connection"""
        test_entry = {
            "message": "Cloud logger initialized",
            "timestamp": datetime.now().isoformat(),
            "severity": "INFO"
        }
        if self.use_cloud_logging:
            self.logger.log_struct(test_entry)
    
    def _ensure_fallback_file_exists(self):
        """Create fallback log file if it doesn't exist"""
        if not os.path.exists(self.fallback_file):
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                pass
    
    def log_search_query(self, query: str, results: List[tuple]) -> str:
        """
        Log a search query with initial results
        
        Args:
            query: The search query text
            results: List of tuples (similarity, image_id, filename, category, description, file_path)
        
        Returns:
            session_id: Unique identifier for this search session
        """
        session_id = self._generate_session_id()
        
        # Prepare results data
        search_results = []
        for i, (similarity, image_id, filename, category, description, file_path) in enumerate(results):
            search_results.append({
                "rank": i + 1,
                "image_filename": filename,
                "similarity_score": float(similarity),
                "category": category,
                "description": description,
                "file_path": file_path
            })
        
        log_entry = {
            "event_type": "search_query",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "query_text": query,
            "total_results": len(results),
            "search_results": search_results,
            "user_feedback": None,
            "correct_answer_rank": None,
            "is_correct_answer_found": None,
            "severity": "INFO"
        }
        
        self._write_log_entry(log_entry)
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int] = None):
        """
        Log user feedback for a search session
        
        Args:
            session_id: The session ID from log_search_query
            correct_rank: Rank of correct answer (1-10), or None if no correct answer
        """
        feedback_entry = {
            "event_type": "user_feedback",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "feedback_timestamp": datetime.now().isoformat(),
            "correct_answer_rank": correct_rank,
            "is_correct_answer_found": correct_rank is not None,
            "severity": "INFO"
        }
        
        self._write_log_entry(feedback_entry)
    
    def log_search_statistics(self, stats: Dict[str, Any]):
        """
        Log search statistics
        
        Args:
            stats: Dictionary with search statistics
        """
        stats_entry = {
            "event_type": "search_statistics",
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "severity": "INFO"
        }
        
        self._write_log_entry(stats_entry)
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write log entry to cloud or fallback file"""
        if self.use_cloud_logging:
            try:
                # Google Cloud Loggingに送信
                self.logger.log_struct(log_entry)
            except Exception as e:
                print(f"Cloud logging failed: {e}, writing to fallback file")
                self._write_to_fallback_file(log_entry)
        else:
            self._write_to_fallback_file(log_entry)
    
    def _write_to_fallback_file(self, log_entry: Dict[str, Any]):
        """Write to local fallback file"""
        with open(self.fallback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def get_search_statistics_from_fallback(self) -> Dict[str, Any]:
        """
        Get search statistics from fallback file
        (Cloud logging would use BigQuery for analytics)
        """
        if not os.path.exists(self.fallback_file):
            return {
                "total_searches": 0,
                "searches_with_feedback": 0,
                "correct_answers_found": 0,
                "accuracy_rate": 0,
                "feedback_rate": 0,
                "popular_queries": [],
                "correct_answer_rank_distribution": {}
            }
        
        search_logs = []
        feedback_logs = []
        
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            if entry.get("event_type") == "search_query":
                                search_logs.append(entry)
                            elif entry.get("event_type") == "user_feedback":
                                feedback_logs.append(entry)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        
        # Create feedback lookup
        feedback_by_session = {log["session_id"]: log for log in feedback_logs}
        
        # Calculate statistics
        total_searches = len(search_logs)
        searches_with_feedback = len(feedback_logs)
        correct_answers_found = len([log for log in feedback_logs if log.get("is_correct_answer_found") is True])
        
        # Query frequency analysis
        query_counts = {}
        for log in search_logs:
            query = log.get("query_text", "").lower()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Rank distribution of correct answers
        rank_distribution = {}
        for log in feedback_logs:
            rank = log.get("correct_answer_rank")
            if rank is not None:
                rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
        
        return {
            "total_searches": total_searches,
            "searches_with_feedback": searches_with_feedback,
            "correct_answers_found": correct_answers_found,
            "accuracy_rate": correct_answers_found / searches_with_feedback if searches_with_feedback > 0 else 0,
            "feedback_rate": searches_with_feedback / total_searches if total_searches > 0 else 0,
            "popular_queries": sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "correct_answer_rank_distribution": rank_distribution
        }

# Logtail Logger (Better Stack)
class LogtailSearchLogger:
    def __init__(self, logtail_token: str = None):
        """
        Initialize Logtail logger
        
        Args:
            logtail_token: Logtail source token from Better Stack
        """
        self.logtail_token = logtail_token
        self.logtail_url = "https://in.logs.betterstack.com"
        self.fallback_file = "search_logs_logtail.jsonl"
        
        if logtail_token:
            self.use_logtail = True
            print(f"✅ Logtail logging configured")
        else:
            self.use_logtail = False
            print("⚠️ Logtail token not provided, using local file")
            self._ensure_fallback_file_exists()
    
    def _ensure_fallback_file_exists(self):
        """Create fallback log file if it doesn't exist"""
        if not os.path.exists(self.fallback_file):
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                pass
    
    def log_search_query(self, query: str, results: List[tuple]) -> str:
        """Log search query to Logtail or fallback file"""
        session_id = self._generate_session_id()
        
        search_results = []
        for i, (similarity, image_id, filename, category, description, file_path) in enumerate(results):
            search_results.append({
                "rank": i + 1,
                "image_filename": filename,
                "similarity_score": float(similarity),
                "category": category,
                "description": description
            })
        
        log_message = {
            "app": "clip-search-demo",
            "event_type": "search_query",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "query_text": query,
            "total_results": len(results),
            "search_results": search_results,
            "level": "info"
        }
        
        self._send_log(log_message)
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int] = None):
        """Log user feedback to Logtail or fallback file"""
        log_message = {
            "app": "clip-search-demo",
            "event_type": "user_feedback",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "correct_answer_rank": correct_rank,
            "is_correct_answer_found": correct_rank is not None,
            "level": "info"
        }
        
        self._send_log(log_message)
    
    def log_search_statistics(self, stats: Dict[str, Any]):
        """Log search statistics to Logtail"""
        log_message = {
            "app": "clip-search-demo",
            "event_type": "search_statistics",
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "level": "info"
        }
        
        self._send_log(log_message)
    
    def _send_log(self, log_message: Dict[str, Any]):
        """Send log to Logtail or write to fallback file"""
        if self.use_logtail:
            try:
                import requests
                
                headers = {
                    'Authorization': f'Bearer {self.logtail_token}',
                    'Content-Type': 'application/json'
                }
                
                # Logtailに送信
                response = requests.post(
                    self.logtail_url,
                    json=log_message,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code != 202:
                    print(f"Logtail logging failed with status {response.status_code}")
                    self._write_to_fallback_file(log_message)
                    
            except Exception as e:
                print(f"Logtail logging failed: {e}, writing to fallback file")
                self._write_to_fallback_file(log_message)
        else:
            self._write_to_fallback_file(log_message)
    
    def _write_to_fallback_file(self, log_message: Dict[str, Any]):
        """Write to local fallback file"""
        with open(self.fallback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_message, ensure_ascii=False) + '\n')
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def get_search_statistics_from_fallback(self) -> Dict[str, Any]:
        """Get search statistics from fallback file"""
        if not os.path.exists(self.fallback_file):
            return {
                "total_searches": 0,
                "searches_with_feedback": 0,
                "correct_answers_found": 0,
                "accuracy_rate": 0,
                "feedback_rate": 0,
                "popular_queries": [],
                "correct_answer_rank_distribution": {}
            }
        
        search_logs = []
        feedback_logs = []
        
        try:
            with open(self.fallback_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            if entry.get("event_type") == "search_query":
                                search_logs.append(entry)
                            elif entry.get("event_type") == "user_feedback":
                                feedback_logs.append(entry)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        
        # Calculate statistics
        total_searches = len(search_logs)
        searches_with_feedback = len(feedback_logs)
        correct_answers_found = len([log for log in feedback_logs if log.get("is_correct_answer_found") is True])
        
        # Query frequency analysis
        query_counts = {}
        for log in search_logs:
            query = log.get("query_text", "").lower()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Rank distribution of correct answers
        rank_distribution = {}
        for log in feedback_logs:
            rank = log.get("correct_answer_rank")
            if rank is not None:
                rank_distribution[rank] = rank_distribution.get(rank, 0) + 1
        
        return {
            "total_searches": total_searches,
            "searches_with_feedback": searches_with_feedback,
            "correct_answers_found": correct_answers_found,
            "accuracy_rate": correct_answers_found / searches_with_feedback if searches_with_feedback > 0 else 0,
            "feedback_rate": searches_with_feedback / total_searches if total_searches > 0 else 0,
            "popular_queries": sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "correct_answer_rank_distribution": rank_distribution
        }

# Alternative: Papertrail Logger (simpler, HTTP-based)
class PapertrailSearchLogger:
    def __init__(self, papertrail_host: str = None, papertrail_port: int = None):
        """
        Initialize Papertrail logger
        
        Args:
            papertrail_host: Papertrail host (e.g., logs.papertrailapp.com)
            papertrail_port: Papertrail port number
        """
        self.papertrail_host = papertrail_host
        self.papertrail_port = papertrail_port
        self.fallback_file = "search_logs_papertrail.jsonl"
        
        if papertrail_host and papertrail_port:
            self.use_papertrail = True
            print(f"✅ Papertrail logging configured: {papertrail_host}:{papertrail_port}")
        else:
            self.use_papertrail = False
            print("⚠️ Papertrail credentials not provided, using local file")
            self._ensure_fallback_file_exists()
    
    def _ensure_fallback_file_exists(self):
        """Create fallback log file if it doesn't exist"""
        if not os.path.exists(self.fallback_file):
            with open(self.fallback_file, 'w', encoding='utf-8') as f:
                pass
    
    def log_search_query(self, query: str, results: List[tuple]) -> str:
        """Log search query to Papertrail or fallback file"""
        session_id = self._generate_session_id()
        
        search_results = []
        for i, (similarity, image_id, filename, category, description, file_path) in enumerate(results):
            search_results.append({
                "rank": i + 1,
                "image_filename": filename,
                "similarity_score": float(similarity),
                "category": category
            })
        
        log_message = {
            "app": "clip-search-demo",
            "event": "search_query",
            "session_id": session_id,
            "query_text": query,
            "total_results": len(results),
            "search_results": search_results
        }
        
        self._send_log(log_message)
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int] = None):
        """Log user feedback to Papertrail or fallback file"""
        log_message = {
            "app": "clip-search-demo",
            "event": "user_feedback",
            "session_id": session_id,
            "correct_answer_rank": correct_rank,
            "is_correct_answer_found": correct_rank is not None
        }
        
        self._send_log(log_message)
    
    def _send_log(self, log_message: Dict[str, Any]):
        """Send log to Papertrail or write to fallback file"""
        if self.use_papertrail:
            try:
                import socket
                import json
                
                # Send to Papertrail via syslog
                message = json.dumps(log_message, ensure_ascii=False)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(message.encode('utf-8'), (self.papertrail_host, self.papertrail_port))
                sock.close()
            except Exception as e:
                print(f"Papertrail logging failed: {e}, writing to fallback file")
                self._write_to_fallback_file(log_message)
        else:
            self._write_to_fallback_file(log_message)
    
    def _write_to_fallback_file(self, log_message: Dict[str, Any]):
        """Write to local fallback file"""
        log_message["timestamp"] = datetime.now().isoformat()
        with open(self.fallback_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_message, ensure_ascii=False) + '\n')
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

# Configuration and factory function
def create_logger(service: str = "cloud", **kwargs):
    """
    Factory function to create appropriate logger
    
    Args:
        service: "cloud" for Google Cloud Logging, "logtail" for Logtail/Better Stack, "papertrail" for Papertrail
        **kwargs: Service-specific configuration
    
    Returns:
        Logger instance
    """
    if service == "cloud":
        return CloudSearchLogger(**kwargs)
    elif service == "logtail":
        return LogtailSearchLogger(**kwargs)
    elif service == "papertrail":
        return PapertrailSearchLogger(**kwargs)
    else:
        raise ValueError(f"Unknown logging service: {service}")

def create_streamlit_logger():
    """
    Create logger with Streamlit Cloud secrets support
    
    Returns:
        Logger instance configured for Streamlit Cloud
    """
    try:
        import streamlit as st
        import json
        from google.oauth2 import service_account
        
        # Check if running in Streamlit and secrets are available
        if hasattr(st, 'secrets') and "gcp" in st.secrets:
            project_id = st.secrets["gcp"]["project_id"]
            
            # Parse credentials from secrets
            credentials_info = json.loads(st.secrets["gcp"]["credentials"])
            credentials = service_account.Credentials.from_service_account_info(credentials_info)
            
            print(f"✅ Using Streamlit secrets for project: {project_id}")
            return create_logger("cloud", project_id=project_id, credentials=credentials)
        
        # Fallback to environment variables
        print("⚠️ Streamlit secrets not found, trying environment variables")
        return create_logger("cloud")
        
    except ImportError:
        # Not running in Streamlit environment
        print("⚠️ Not in Streamlit environment, using environment variables")
        return create_logger("cloud")
    except Exception as e:
        print(f"⚠️ Streamlit secrets failed: {e}, falling back to environment variables")
        return create_logger("cloud")

# Default instance (you can change this based on your preference)
# For Logtail (recommended):
# search_logger = create_logger("logtail", logtail_token="your-logtail-token")

# For Google Cloud Logging:
# search_logger = create_logger("cloud", project_id="your-project-id")

# For Papertrail:
# search_logger = create_logger("papertrail", 
#                              papertrail_host="logs.papertrailapp.com", 
#                              papertrail_port=12345)

# Configuration: Create logger with Streamlit Cloud support
# This will automatically detect Streamlit secrets or fall back to environment variables
search_logger = create_streamlit_logger() 