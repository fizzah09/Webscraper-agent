import os
from dotenv import load_dotenv
import facebook

# Load your credentials
load_dotenv()

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_ID')

def test_connection():
    """Test if your Facebook credentials work"""
    
    print("🔍 Testing Facebook Page Connection...")
    print("=" * 60)
    
    # Check if credentials exist
    if not FACEBOOK_ACCESS_TOKEN:
        print("❌ ERROR: FACEBOOK_ACCESS_TOKEN not found in .env file")
        return False
    
    if not FACEBOOK_PAGE_ID:
        print("❌ ERROR: FACEBOOK_PAGE_ID not found in .env file")
        return False
    
    print("✅ Credentials loaded from .env file")
    print(f"   Page ID: {FACEBOOK_PAGE_ID}")
    print(f"   Token: {FACEBOOK_ACCESS_TOKEN[:20]}...")
    
    try:
        # Initialize Facebook Graph API
        graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
        
        # Get page info
        print("\n📄 Fetching page information...")
        page_info = graph.get_object(id=FACEBOOK_PAGE_ID)
        
        print(f"✅ Successfully connected to page!")
        print(f"   Page Name: {page_info.get('name', 'N/A')}")
        print(f"   Page Category: {page_info.get('category', 'N/A')}")
        print(f"   Page Likes: {page_info.get('fan_count', 'N/A')}")
        
        # Test posting capability
        print("\n📝 Testing post capability...")
        response = graph.put_object(
            parent_object=FACEBOOK_PAGE_ID,
            connection_name='feed',
            message='🤖 Test post from my Tech Blog automation bot!\n\nIf you can see this, everything is working perfectly! 🚀'
        )
        
        post_id = response['id']
        print(f"✅ Successfully posted to your page!")
        print(f"   Post ID: {post_id}")
        print(f"   View at: https://www.facebook.com/{post_id}")
        
        # Ask if user wants to delete test post
        print("\n" + "=" * 60)
        delete_choice = input("Delete test post? (y/n): ").lower()
        
        if delete_choice == 'y':
            graph.delete_object(id=post_id)
            print("✅ Test post deleted")
        else:
            print("✅ Test post kept on your page")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Your setup is ready.")
        print("You can now run your CrewAI automation!")
        print("=" * 60)
        
        return True
        
    except facebook.GraphAPIError as e:
        print(f"\n❌ Facebook API Error: {e}")
        print("\nCommon solutions:")
        print("1. Make sure your access token hasn't expired")
        print("2. Verify you have 'pages_manage_posts' permission")
        print("3. Check that you're an admin of the page")
        print("4. Try regenerating your access token")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def check_token_info():
    """Check token permissions and expiry"""
    
    print("\n🔐 Checking token details...")
    
    try:
        graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)
        
        # Get token info
        token_info = graph.get_object(
            id='debug_token',
            fields='data',
            input_token=FACEBOOK_ACCESS_TOKEN
        )
        
        data = token_info.get('data', {})
        
        print(f"   App ID: {data.get('app_id', 'N/A')}")
        print(f"   Valid: {data.get('is_valid', False)}")
        print(f"   Expires: {data.get('expires_at', 'Never (Page Token)')}")
        
        # Get permissions
        permissions = graph.get_object('me/permissions')
        
        print("\n   Granted Permissions:")
        for perm in permissions.get('data', []):
            if perm['status'] == 'granted':
                print(f"      ✅ {perm['permission']}")
        
    except Exception as e:
        print(f"   ⚠️ Could not fetch token details: {e}")

if __name__ == "__main__":
    print("\n🚀 FACEBOOK PAGE AUTOMATION - CONNECTION TEST")
    print("=" * 60)
    
    # Run tests
    check_token_info()
    print("\n")
    test_connection()