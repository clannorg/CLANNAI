#!/usr/bin/env python3
"""
Test API Key Account Type
Check what account/project the current API key is associated with
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent.parent / "0_utils"))
from dotenv import load_dotenv

# Load environment
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

def test_api_key_account():
    """Test the API key to determine account type and quota"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ No GEMINI_API_KEY found in environment")
        return
    
    print("🔍 TESTING API KEY ACCOUNT TYPE")
    print("=" * 50)
    print()
    
    # API key info
    print("🔑 API KEY INFO:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Format: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    # Test with a simple API call (list models)
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        print("📡 TESTING API CONNECTION...")
        response = requests.get(models_url, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API KEY IS VALID")
            print()
            
            # Check available models
            if 'models' in data:
                models = data['models']
                print(f"🤖 AVAILABLE MODELS: {len(models)} models")
                
                for model in models[:5]:  # Show first 5
                    name = model.get('name', '').replace('models/', '')
                    print(f"   • {name}")
                
                if len(models) > 5:
                    print(f"   ... and {len(models) - 5} more")
                print()
            
            # Test a minimal generation to check quota behavior
            print("🧪 TESTING QUOTA TYPE...")
            test_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
            test_payload = {
                "contents": [{
                    "parts": [{"text": "What is 2+2? (one word answer)"}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 10
                }
            }
            
            test_response = requests.post(
                f"{test_url}?key={api_key}",
                headers={"Content-Type": "application/json"},
                json=test_payload,
                timeout=10
            )
            
            print(f"   Generation Status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                print("✅ GENERATION SUCCESSFUL")
                test_data = test_response.json()
                
                # Check usage metadata
                if 'usageMetadata' in test_data:
                    usage = test_data['usageMetadata']
                    print("📊 USAGE METADATA:")
                    print(f"   Prompt tokens: {usage.get('promptTokenCount', 'N/A')}")
                    print(f"   Response tokens: {usage.get('candidatesTokenCount', 'N/A')}")
                    print(f"   Total tokens: {usage.get('totalTokenCount', 'N/A')}")
                
                print()
                print("🎯 ACCOUNT TYPE ANALYSIS:")
                print("   ✅ API key is working")
                print("   ✅ Can generate content")
                print("   ✅ No immediate quota blocks")
                print("   💡 Likely PAID or high-quota account")
                
            elif test_response.status_code == 429:
                print("⚠️  QUOTA EXCEEDED")
                error_data = test_response.json()
                print("📊 QUOTA INFO:")
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown')}")
                
                if 'free_tier' in str(error_data).lower():
                    print("   🆓 Account Type: FREE TIER")
                    print("   📅 Resets: Every 24 hours")
                else:
                    print("   💳 Account Type: PAID (quota exceeded)")
                    
            else:
                print(f"❌ Generation failed: {test_response.status_code}")
                try:
                    error_data = test_response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw response: {test_response.text}")
                    
        elif response.status_code == 403:
            print("❌ API KEY FORBIDDEN")
            print("   Possible issues:")
            print("   • API not enabled for this project")
            print("   • Invalid key")
            print("   • Billing not set up")
            
        elif response.status_code == 400:
            print("❌ BAD REQUEST")
            print("   API key format may be invalid")
            
        else:
            print(f"❌ API CALL FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️  REQUEST TIMEOUT")
        print("   API may be slow or unavailable")
        
    except requests.exceptions.ConnectionError:
        print("🌐 CONNECTION ERROR")
        print("   Check internet connection")
        
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {str(e)}")
    
    print()
    print("🔗 COMPARISON WITH GCLOUD:")
    print(f"   gcloud project: clann-app-a1")
    print(f"   gcloud account: thomasbradley859@gmail.com") 
    print(f"   API key project: Unknown (need to check)")

if __name__ == "__main__":
    test_api_key_account() 