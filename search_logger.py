"""
Search Logger Module
Logs search queries, results, and user feedback for analysis
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any

class SearchLogger:
    def __init__(self, log_file: str = "search_logs.jsonl"):
        """
        Initialize the search logger
        
        Args:
            log_file: Path to the log file (JSONL format)
        """
        self.log_file = log_file
        self.ensure_log_file_exists()
    
    def ensure_log_file_exists(self):
        """Create log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', encoding='utf-8') as f:
                pass  # Create empty file
    
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
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "query_text": query,
            "total_results": len(results),
            "search_results": search_results,
            "user_feedback": None,  # Will be updated when user provides feedback
            "correct_answer_rank": None,
            "is_correct_answer_found": None
        }
        
        self._write_log_entry(log_entry)
        return session_id
    
    def log_user_feedback(self, session_id: str, correct_rank: Optional[int] = None):
        """
        Update log entry with user feedback
        
        Args:
            session_id: The session ID from log_search_query
            correct_rank: Rank of correct answer (1-10), or None if no correct answer
        """
        # Read existing logs
        logs = self._read_all_logs()
        
        # Find and update the matching log entry
        updated = False
        for log_entry in logs:
            if log_entry.get("session_id") == session_id:
                log_entry["user_feedback"] = {
                    "feedback_timestamp": datetime.now().isoformat(),
                    "correct_answer_rank": correct_rank,
                    "is_correct_answer_found": correct_rank is not None
                }
                log_entry["correct_answer_rank"] = correct_rank
                log_entry["is_correct_answer_found"] = correct_rank is not None
                updated = True
                break
        
        if updated:
            # Rewrite the entire log file
            self._write_all_logs(logs)
        else:
            print(f"Warning: Session ID {session_id} not found in logs")
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get search statistics from logs
        
        Returns:
            Dictionary with various statistics
        """
        logs = self._read_all_logs()
        
        total_searches = len(logs)
        searches_with_feedback = len([log for log in logs if log.get("user_feedback") is not None])
        correct_answers_found = len([log for log in logs if log.get("is_correct_answer_found") is True])
        
        # Query frequency analysis
        query_counts = {}
        for log in logs:
            query = log.get("query_text", "").lower()
            query_counts[query] = query_counts.get(query, 0) + 1
        
        # Rank distribution of correct answers
        rank_distribution = {}
        for log in logs:
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
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"search_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write a single log entry to file"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _read_all_logs(self) -> List[Dict[str, Any]]:
        """Read all log entries from file"""
        logs = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            logs.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            pass
        return logs
    
    def _write_all_logs(self, logs: List[Dict[str, Any]]):
        """Write all log entries to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            for log_entry in logs:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

# Global logger instance
search_logger = SearchLogger() 