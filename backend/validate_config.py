#!/usr/bin/env python3
"""
Configuration validation script for CSV Knowledge Base API.
Run this script to validate your environment configuration.
"""

import os
from dotenv import load_dotenv

def validate_config():
    """Validate all required environment variables"""
    print("🔍 Validating CSV Knowledge Base API Configuration...")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Required configuration
    required_vars = {
        # Supabase Configuration
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_ANON_KEY': 'Supabase anonymous key',
        'SUPABASE_SERVICE_KEY': 'Supabase service role key',
        'DATABASE_URL': 'Supabase database URL',
        
        # LLM Configuration
        'GROQ_API_KEY': 'Groq API key for LLM processing'
    }
    
    # Optional configuration with defaults
    optional_vars = {
        'GROQ_MODEL': ('llama-3.1-8b-instant', 'LLM model to use'),
        'GROQ_BASE_URL': ('https://api.groq.com/openai/v1/chat/completions', 'Groq API endpoint'),
        'GROQ_TEMPERATURE': ('0.3', 'LLM temperature setting'),
        'GROQ_MAX_TOKENS': ('2000', 'Maximum tokens for LLM response'),
        'DEBUG': ('false', 'Debug mode setting'),
        'APP_NAME': ('CSV Upload and Knowledge Base API', 'Application name'),
        'APP_VERSION': ('2.0.0', 'Application version')
    }
    
    errors = []
    warnings = []
    
    # Check required variables
    print("📋 Checking Required Configuration:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var}: Missing - {description}")
            print(f"  ❌ {var}: MISSING")
        else:
            # Mask sensitive values
            if 'KEY' in var or 'URL' in var:
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
    
    print("\n📋 Checking Optional Configuration:")
    for var, (default, description) in optional_vars.items():
        value = os.getenv(var, default)
        print(f"  ℹ️  {var}: {value}")
        if not os.getenv(var):
            warnings.append(f"⚠️  {var}: Using default value '{default}'")
    
    # Validate Groq API key format
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        if not groq_key.startswith('gsk_'):
            warnings.append("⚠️  GROQ_API_KEY: Should start with 'gsk_'")
        if len(groq_key) < 50:
            warnings.append("⚠️  GROQ_API_KEY: Seems too short, verify it's correct")
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 Configuration Validation Results:")
    
    if errors:
        print(f"\n❌ {len(errors)} Critical Error(s):")
        for error in errors:
            print(f"  {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for warning in warnings:
            print(f"  {warning}")
    
    if not errors and not warnings:
        print("\n🎉 All configuration is valid!")
    elif not errors:
        print("\n✅ Configuration is valid (with warnings)")
    else:
        print("\n💥 Configuration has critical errors that must be fixed")
    
    # Provide next steps
    print("\n📚 Next Steps:")
    if errors:
        print("1. Fix the missing required environment variables")
        print("2. Get your Groq API key from: https://console.groq.com/keys")
        print("3. Update your .env file with the missing values")
        print("4. Run this script again to validate")
    else:
        print("1. Start the application: python main.py")
        print("2. Test the API: http://localhost:8000/docs")
        print("3. Run examples: python examples/metadata_examples.py")
    
    return len(errors) == 0

def test_imports():
    """Test if all required packages are installed"""
    print("\n🔧 Testing Package Imports:")
    
    packages = [
        ('fastapi', 'FastAPI web framework'),
        ('uvicorn', 'ASGI server'),
        ('supabase', 'Supabase client'),
        ('httpx', 'HTTP client for LLM API'),
        ('pandas', 'Data processing'),
        ('pydantic', 'Data validation'),
        ('python_dotenv', 'Environment variable loading')
    ]
    
    missing_packages = []
    
    for package, description in packages:
        try:
            if package == 'python_dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"  ✅ {package}: Available")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}: Missing - {description}")
    
    if missing_packages:
        print(f"\n💥 Missing {len(missing_packages)} required package(s)")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n🎉 All required packages are installed!")
        return True

def main():
    """Main validation function"""
    print("🚀 CSV Knowledge Base API - Configuration Validator")
    print("=" * 60)
    
    # Test package imports
    packages_ok = test_imports()
    
    if not packages_ok:
        print("\n❌ Cannot proceed with configuration validation due to missing packages")
        return False
    
    # Validate configuration
    config_ok = validate_config()
    
    print("\n" + "=" * 60)
    if config_ok:
        print("🎉 Configuration validation completed successfully!")
        print("Your CSV Knowledge Base API is ready to run!")
    else:
        print("💥 Configuration validation failed!")
        print("Please fix the errors above before starting the application.")
    
    return config_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)