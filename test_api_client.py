import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_load_url(url: str):
    """Test loading content from URL"""
    print(f"\n{'='*60}")
    print(f"Loading: {url}")
    print('='*60)
    
    response = requests.post(
        f"{BASE_URL}/load_url",
        json={"url": url},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Success: {result['message']}")
        print(f"Result: {result['result'][:200]}...")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Details: {response.text}")
    
    time.sleep(2)  # Delay between requests

def test_ask_question(question: str):
    """Test asking a question about loaded content"""
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print('='*60)
    
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"question": question},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Answer: {result['answer'][:300]}...")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources: {result['sources']}")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Details: {response.text}")
    
    time.sleep(2)

def main():
    print("\n" + "="*60)
    print("Web Scraping and RAG Testing")
    print("="*60)
    
    # Test URLs
    test_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",
        "https://example.com",
    ]
    
    # Load content from URLs
    for url in test_urls:
        test_load_url(url)
    
    # Ask questions about loaded content
    test_questions = [
        "What information did you load from the web?",
        "Summarize the web content you found.",
        "What are the main topics covered in the loaded content?",
        "Tell me about the example website.",
    ]
    
    print("\n" + "="*60)
    print("Testing Questions on Loaded Content")
    print("="*60)
    
    for question in test_questions:
        test_ask_question(question)
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API at localhost:8001")
        print("Please ensure the API is running: python src/api.py")
    except Exception as e:
        print(f"Error: {str(e)}")
