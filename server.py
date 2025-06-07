from mcp.server.fastmcp import FastMCP
import sys
import os
import time

from authentication import TOKEN_FILE, CREDENTIALS_FILE

# Add current directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))



#change this to your actual Credentials path & token path from authentication.py

CREDENTIALS_PATH = CREDENTIALS_FILE

#your token.pickle file will be generated after the first run, so run your code & copy the path

TOKEN_PATH = TOKEN_FILE

# Now import your custom modules
try:
    from docs import GoogleDocsClient
    print("Successfully imported GoogleDocsClient")
except ImportError as e:
    print(f"Failed to import GoogleDocsClient: {e}")
    GoogleDocsClient = None

# Initialize FastMCP Server
mcp = FastMCP("google-docs-mcp")


docs_client = None
last_auth_check = 0





@mcp.resource("debug://fs-inspect")
def fs_inspect():
    cwd = os.getcwd()
    files = os.listdir(cwd)
    return f"CWD: {cwd}\nFiles: {files}"

@mcp.tool()
def get_debugging_info():
    return fs_inspect()

@mcp.resource("debug://google-docs-client-status")
def debugging_info():
    return f"""
    Google Docs Client Status Debug Information:
    
    • Client initialized: {docs_client is not None}
    • Last auth check: {time.ctime(last_auth_check) if last_auth_check else 'Never'}
    • Token file exists: {os.path.exists(TOKEN_PATH)}
    • Credentials configured: {os.getenv(CREDENTIALS_PATH) is not None}
    
    If there are issues:
    1. Complete OAuth flow if token.pickle is missing
    2. Restart MCP server after OAuth completion
    3. Check that .env file has correct CREDENTIALS_PATH
    4. Ensure Google API permissions are granted
    
    You can also try the 'refresh_auth' tool to force re-authentication.
    """


def initialize_docs_client(force_refresh=False):
    """Initialize the Google Docs client with comprehensive error handling"""
    global docs_client, last_auth_check
    
    if not force_refresh and docs_client is not None:
        return True
    
    if GoogleDocsClient is None:
        print("❌ GoogleDocsClient class not available due to import error")
        return False
    
    try:
        print("🔄 Attempting to initialize Google Docs client...")
        
        # Check if token file exists and is recent
        token_file = TOKEN_PATH
        if os.path.exists(token_file):
            token_age = time.time() - os.path.getmtime(token_file)
            print(f"📝 Token file age: {token_age/60:.1f} minutes")
        
        docs_client = GoogleDocsClient()
        last_auth_check = time.time()
        print("✅ Google Docs client initialized successfully")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Credentials file not found: {e}")
        print("💡 Make sure your .env file has the correct CREDENTIALS_PATH")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize Google Docs client: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # If it's an auth error, suggest refreshing
        if "credentials" in str(e).lower() or "auth" in str(e).lower():
            print("💡 This looks like an authentication issue. Try:")
            print("   1. Restarting the MCP server")
            print("   2. Running the OAuth flow again")
            print("   3. Using the refresh_auth tool")
        
        return False

# Try to initialize the client on startup
print("🚀 Initial client initialization...")
client_initialized = initialize_docs_client()

@mcp.tool()
def refresh_auth() -> str:
    """Force refresh the authentication and reinitialize the client"""
    global docs_client
    
    print("🔄 Forcing authentication refresh...")
    
    # Clear the current client
    docs_client = None
    
    # Try to reinitialize
    if initialize_docs_client(force_refresh=True):
        return """✅ Authentication refreshed successfully!

The Google Docs client has been reinitialized. You can now use all document tools:
• create_google_doc
• add_content_to_doc  
• create_doc_with_content"""
    else:
        return """❌ Authentication refresh failed.

Please check:
1. Your .env file has the correct CREDENTIALS_PATH
2. The credentials file exists and is valid
3. You've completed the OAuth flow (token.pickle exists)
4. Your internet connection is working

You may need to run the OAuth flow again or restart the MCP server."""

@mcp.tool()
def create_google_doc(title: str) -> str:
    """Create a new Google Document with a specified title"""
    global docs_client
    
    # Try to reinitialize if client is None
    if not docs_client:
        print("🔄 Docs client not available, attempting to reinitialize...")
        if not initialize_docs_client():
            return """❌ Google Docs client is not available. 

🔧 **Quick Fixes:**
1. **Restart the MCP server** - This often resolves authentication state issues
2. **Check token file** - Ensure token.pickle exists and is recent
3. **Use refresh_auth tool** - Force authentication refresh
4. **Verify credentials** - Check your .env file and credentials.json

If the problem persists, you may need to complete the OAuth flow again."""
    
    try:
        print(f"📝 Creating document with title: {title}")
        result = docs_client.create_doc(title)
        
        if result['success']:
            return f"""✅ Google Doc Created Successfully!

📄 **Title:** {result['title']}
🆔 **Document ID:** {result['doc_id']}
🔗 **URL:** {result['url']}

The document is ready for editing. You can access it using the URL above."""
        else:
            # Check if it's an auth error
            error_msg = result['error']
            if "credentials" in error_msg.lower() or "auth" in error_msg.lower():
                return f"""❌ Authentication Error: {error_msg}

🔧 **Try these solutions:**
1. Use the `refresh_auth` tool
2. Restart the MCP server
3. Complete OAuth flow again if token.pickle is missing"""
            else:
                return f"❌ **Error creating document:** {error_msg}"
    
    except Exception as e:
        error_str = str(e)
        if "credentials" in error_str.lower() or "auth" in error_str.lower():
            return f"""❌ Authentication Exception: {error_str}

🔧 **This is likely an authentication timing issue. Try:**
1. **Restart the MCP server** (most common fix)
2. Use the `refresh_auth` tool
3. Check that token.pickle exists and is recent"""
        else:
            return f"❌ **Error executing create_google_doc:** {error_str}"

@mcp.tool()
def add_content_to_doc(document_id: str, content: str, position: str = "end") -> str:
    """Add content to an existing Google Document
    
    Args:
        document_id: The ID of the Google Document to update
        content: The content to add to the document
        position: Where to add the content ("beginning" or "end", default: "end")
    """
    global docs_client
    

    
    if not docs_client:
        if not initialize_docs_client():
            return "❌ Google Docs client is not available. Try using `refresh_auth` or restarting the MCP server."
    
    # Validate position parameter
    if position not in ["beginning", "end"]:
        return "❌ **Error:** Position must be either 'beginning' or 'end'"
    
    try:
        result = docs_client.add_info_to_existing_doc(
            document_id=document_id,
            information=content,
            position=position
        )
        
        if result['success']:
            return f"""✅ Content Added Successfully!

📝 **Added to:** Document ID {document_id}
📍 **Position:** {position.title()}
📊 **Characters added:** {len(content)}
🔗 **URL:** {result['url']}

The content has been added to your document."""
        else:
            return f"❌ **Error adding content:** {result['error']}"
    
    except Exception as e:
        return f"❌ **Error executing add_content_to_doc:** {str(e)}"

@mcp.tool()
def create_doc_with_content(title: str, content: str) -> str:
    """Create a new Google Document with initial content
    
    Args:
        title: The title for the new Google Document
        content: Initial content to add to the document
    """
    global docs_client
    
    # Smart auth refresh
    
    
    if not docs_client:
        if not initialize_docs_client():
            return "❌ Google Docs client is not available. Try using `refresh_auth` or restarting the MCP server."
    
    try:
        # First create the document
        create_result = docs_client.create_doc(title)
        
        if not create_result['success']:
            return f"❌ **Error creating document:** {create_result['error']}"
        
        # Then add content to it
        doc_id = create_result['doc_id']
        add_result = docs_client.add_info_to_existing_doc(
            document_id=doc_id,
            information=content,
            position="beginning"
        )
        
        if add_result['success']:
            return f"""✅ Google Doc Created with Content!

📄 **Title:** {create_result['title']}
🆔 **Document ID:** {doc_id}
📝 **Content added:** {len(content)} characters
🔗 **URL:** {create_result['url']}

Your document has been created and populated with the provided content."""
        else:
            return f"""⚠️ Document created but content addition failed:

📄 **Title:** {create_result['title']}
🆔 **Document ID:** {doc_id}
🔗 **URL:** {create_result['url']}
❌ **Content Error:** {add_result['error']}

You can manually add content to the document using the URL above."""
    
    except Exception as e:
        return f"❌ **Error executing create_doc_with_content:** {str(e)}"

def main():
    """Main function to run the MCP server"""
    print("🚀 Starting Google Docs MCP Server...")
    print("📋 Available tools:")
    
    tools = [
        "• create_google_doc - Create a new Google Document",
        "• add_content_to_doc - Add content to existing document", 
        "• create_doc_with_content - Create document with initial content"
    ]
    
    for tool in tools:
        print(f"  {tool}")
    
    if docs_client:
        print("✅ Google Docs client ready!")
    else:
        print("⚠️  Client will initialize on first use or use `refresh_auth`")
    
    print(f"\n🎯 Server ready!")
    print("💡 Example: 'Create a new Google doc called Meeting Notes'")
    print("🔧 If you have auth issues, restart the server, or check credentials path & token path")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()