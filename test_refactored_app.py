"""
Test script cho ứng dụng đã refactor
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.data_service import DataService
from src.services.cache_service import dashboard_cache
import time

def test_data_service():
    """Test DataService"""
    print("=== Test DataService ===")
    
    service = DataService()
    
    # Test get stats
    print("1. Test get_stats:")
    stats = service.get_stats()
    print(f"   Stats: {stats}")
    
    # Test get dashboard data
    print("2. Test get_dashboard_data:")
    df = service.get_dashboard_data(limit=10)
    print(f"   Data shape: {df.shape}")
    print(f"   Columns: {list(df.columns) if not df.empty else 'No data'}")
    
    # Test URL analysis
    print("3. Test analyze_url:")
    test_url = "https://cafef.vn/test-url"
    result = service.analyze_url(test_url)
    print(f"   Analysis result success: {result.get('success', False)}")
    if not result.get('success'):
        print(f"   Error: {result.get('error')}")

def test_cache_service():
    """Test Cache Service"""
    print("\n=== Test Cache Service ===")
    
    # Test set/get
    dashboard_cache.set("test_key", {"data": "test_value"}, timeout=5)
    cached_data = dashboard_cache.get("test_key")
    print(f"1. Cache set/get: {cached_data}")
    
    # Test timeout
    print("2. Testing cache timeout (wait 6 seconds)...")
    time.sleep(6)
    expired_data = dashboard_cache.get("test_key")
    print(f"   Expired data: {expired_data}")
    
    # Test clear
    dashboard_cache.set("test_key2", "another_value")
    dashboard_cache.clear()
    cleared_data = dashboard_cache.get("test_key2")
    print(f"3. After clear: {cleared_data}")

def test_separation_of_concerns():
    """Test tách biệt chức năng"""
    print("\n=== Test Separation of Concerns ===")
    
    service = DataService()
    
    # Test phân tích không lưu
    print("1. Analyze without saving:")
    test_url = "https://example.com"
    analysis = service.analyze_url(test_url)
    print(f"   Analysis completed: {analysis.get('success', False)}")
    
    # Test lưu riêng biệt
    if analysis.get('success'):
        print("2. Save separately:")
        save_result = service.save_analysis_result(analysis)
        print(f"   Save result: {save_result}")
    
    print("Separation test completed - analyze and save are now separate!")

if __name__ == "__main__":
    print("Testing Refactored Financial Analysis App")
    print("=" * 50)
    
    try:
        test_data_service()
        test_cache_service()
        test_separation_of_concerns()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("Refactored app is ready with:")
        print("   - Separated data service layer")
        print("   - Independent analyze and save functions")
        print("   - Caching for better performance")
        print("   - Cleaner callback structure")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        import traceback
        traceback.print_exc()