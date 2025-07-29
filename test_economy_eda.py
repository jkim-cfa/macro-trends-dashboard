#!/usr/bin/env python3
"""
Test script to identify where economy_eda.py is getting stuck
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔍 Testing environment variables...")
    load_dotenv()
    
    required_vars = [
        'GEMINI_API_KEY', 
        'POSTGRES_USER', 
        'POSTGRES_PASSWORD', 
        'POSTGRES_DB', 
        'POSTGRES_HOST', 
        'POSTGRES_PORT', 
        'EDA_DIR'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: SET")
        else:
            print(f"❌ {var}: NOT SET")
            missing.append(var)
    
    return missing

def test_database_connection():
    """Test database connection"""
    print("\n🔌 Testing database connection...")
    try:
        from sqlalchemy import create_engine
        import pandas as pd
        
        PG_USER = os.getenv("POSTGRES_USER")
        PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        PG_DB = os.getenv("POSTGRES_DB")
        PG_HOST = os.getenv("POSTGRES_HOST")
        PG_PORT = os.getenv("POSTGRES_PORT")
        
        if not all([PG_USER, PG_PASSWORD, PG_DB, PG_HOST, PG_PORT]):
            print("❌ Database connection failed: Missing environment variables")
            return False
        
        engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}")
        
        # Test connection
        test_query = "SELECT 1 as test"
        result = pd.read_sql(test_query, engine)
        print("✅ Database connection successful")
        
        # Test if required tables exist
        tables_to_check = [
            'economy_economy_confidence_processed',
            'economy_fx_rates_processed',
            'economy_leading_vs_coincident_kospi_processed'
        ]
        
        for table in tables_to_check:
            try:
                check_query = f"SELECT COUNT(*) FROM {table}"
                count = pd.read_sql(check_query, engine)
                print(f"✅ Table {table}: {count.iloc[0,0]} records")
            except Exception as e:
                print(f"❌ Table {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API"""
    print("\n🤖 Testing Gemini API...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Gemini API key not set")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Hello, this is a test.")
        print("✅ Gemini API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    print("🚀 Economy EDA Diagnostic Test")
    print("=" * 50)
    
    # Test environment
    missing_vars = test_environment()
    
    # Test database
    db_ok = test_database_connection()
    
    # Test Gemini API
    gemini_ok = test_gemini_api()
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 50)
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
    else:
        print("✅ All environment variables set")
    
    if db_ok:
        print("✅ Database connection OK")
    else:
        print("❌ Database connection failed")
    
    if gemini_ok:
        print("✅ Gemini API OK")
    else:
        print("❌ Gemini API failed")
    
    if not missing_vars and db_ok:
        print("\n✅ Ready to run economy_eda.py")
    else:
        print("\n❌ Fix issues above before running economy_eda.py")

if __name__ == "__main__":
    main() 