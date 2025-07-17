#!/usr/bin/env python3
"""
Google Cloud Logging Test Script
Test the Google Cloud Logging functionality for CLIP search demo
"""

import os
import sys
from datetime import datetime

def test_gcp_logging():
    """Test Google Cloud Logging functionality"""
    print("☁️ Google Cloud Logging Test Script")
    print("=" * 60)
    
    # Check environment variables
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    print("🔍 Environment Check:")
    if credentials_path:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
        if os.path.exists(credentials_path):
            print(f"✅ Credentials file exists")
        else:
            print(f"❌ Credentials file not found: {credentials_path}")
    else:
        print("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set")
    
    if project_id:
        print(f"✅ GOOGLE_CLOUD_PROJECT: {project_id}")
    else:
        print("⚠️ GOOGLE_CLOUD_PROJECT not set")
    
    # Check for alternative authentication methods
    if not credentials_path:
        service_account_file = "service-account-key.json"
        if os.path.exists(service_account_file):
            print(f"✅ Found local service account file: {service_account_file}")
        else:
            print("❌ No authentication method found")
    
    try:
        # Import the logger
        from cloud_logger import search_logger
        print("\n✅ Logger imported successfully")
        
        # Check if Google Cloud Logging is being used
        if hasattr(search_logger, 'use_cloud_logging'):
            if search_logger.use_cloud_logging:
                print("✅ Using Google Cloud Logging")
            else:
                print("⚠️ Falling back to local file logging")
        
        # Test 1: Search query log
        print("\n📝 Test 1: Search query logging")
        test_results = [
            (0.85, 1, "test_image_1.jpg", "テストカテゴリ", "テスト画像1", "data/img/test/test_image_1.jpg"),
            (0.75, 2, "test_image_2.jpg", "テストカテゴリ", "テスト画像2", "data/img/test/test_image_2.jpg"),
            (0.65, 3, "test_image_3.jpg", "テストカテゴリ", "テスト画像3", "data/img/test/test_image_3.jpg")
        ]
        
        session_id = search_logger.log_search_query("Google Cloud テスト検索", test_results)
        print(f"✅ Search query logged with session ID: {session_id}")
        
        # Test 2: User feedback log
        print("\n👍 Test 2: User feedback logging")
        search_logger.log_user_feedback(session_id, 2)  # Second result was correct
        print("✅ User feedback logged (correct answer: rank 2)")
        
        # Test 3: Another search with no correct answer
        print("\n🔍 Test 3: Search with no correct answer")
        session_id_2 = search_logger.log_search_query("Cloud Logging テスト", test_results)
        search_logger.log_user_feedback(session_id_2, None)  # No correct answer
        print("✅ Search with 'no correct answer' logged")
        
        # Test 4: Error log test
        print("\n🚨 Test 4: Error logging")
        try:
            # Simulate an error
            raise Exception("Test error for logging")
        except Exception as e:
            error_log = {
                "event_type": "error",
                "error_message": str(e),
                "error_type": type(e).__name__,
                "severity": "ERROR"
            }
            if hasattr(search_logger, '_write_log_entry'):
                search_logger._write_log_entry(error_log)
                print("✅ Error log entry created")
        
        # Test 5: Statistics (from fallback if using cloud logging)
        print("\n📊 Test 5: Statistics retrieval")
        if hasattr(search_logger, 'get_search_statistics_from_fallback'):
            stats = search_logger.get_search_statistics_from_fallback()
            print(f"✅ Statistics retrieved:")
            print(f"   - Total searches: {stats['total_searches']}")
            print(f"   - Searches with feedback: {stats['searches_with_feedback']}")
            print(f"   - Correct answers found: {stats['correct_answers_found']}")
            print(f"   - Accuracy rate: {stats['accuracy_rate']:.2%}")
        else:
            print("⚠️ Local statistics not available (using cloud logging)")
        
        print("\n🎉 All tests passed!")
        
        # Show where to check logs
        if search_logger.use_cloud_logging and project_id:
            print(f"\n🌐 Check your Google Cloud Console logs:")
            print(f"   https://console.cloud.google.com/logs/query;query=logName%3D%22projects%2F{project_id}%2Flogs%2Fclip-search-demo%22")
            print(f"\n   Or go to: Google Cloud Console → Logging → Logs Explorer")
            print(f"   Filter: logName=\"projects/{project_id}/logs/clip-search-demo\"")
        else:
            print("\n📁 Check the fallback log file:")
            print("   search_logs_fallback.jsonl")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install google-cloud-logging requests")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def show_setup_instructions():
    """Show setup instructions"""
    print("\n📋 Google Cloud Logging Setup Instructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Cloud Logging API")
    print("4. Create service account with 'Logs Writer' role")
    print("5. Download JSON key file")
    print("6. Set environment variables:")
    print("   Windows:")
    print("     set GOOGLE_APPLICATION_CREDENTIALS=path\\to\\service-account-key.json")
    print("     set GOOGLE_CLOUD_PROJECT=your-project-id")
    print("   Mac/Linux:")
    print("     export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json")
    print("     export GOOGLE_CLOUD_PROJECT=your-project-id")
    print("7. Run this test script again")
    print("\nDetailed instructions: See GOOGLE_CLOUD_SETUP.md")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import google.cloud.logging
        print("✅ google-cloud-logging installed")
    except ImportError:
        print("❌ google-cloud-logging not installed")
        print("Install with: pip install google-cloud-logging")
        return False
    
    try:
        import requests
        print("✅ requests installed")
    except ImportError:
        print("❌ requests not installed")
        print("Install with: pip install requests")
        return False
    
    return True

def main():
    """Main function"""
    print(f"🕐 Test started at: {datetime.now().isoformat()}")
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them and try again.")
        sys.exit(1)
    
    success = test_gcp_logging()
    
    if not success:
        show_setup_instructions()
        sys.exit(1)
    
    # Check if proper authentication is set up
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not credentials_path and not os.path.exists("service-account-key.json"):
        print("\n💡 Tip: Set up Google Cloud authentication for full cloud logging")
        show_setup_instructions()
    elif not project_id:
        print("\n💡 Tip: Set GOOGLE_CLOUD_PROJECT environment variable")
        print("Example: set GOOGLE_CLOUD_PROJECT=your-project-id")

if __name__ == "__main__":
    main() 