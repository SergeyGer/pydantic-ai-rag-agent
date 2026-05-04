import requests
import json

BASE_URL = "http://localhost:8001"

def test_rag_with_web_content():
    """Test RAG retrieval with web content"""
    
    print("\n" + "="*70)
    print("RAG Test: Загрузка контента и поиск информации")
    print("="*70)
    
    # Step 1: Загрузим HTML страницу с информацией
    print("\n[Step 1] Загружаем HTML контент...")
    url = "https://httpbin.org/html"
    response = requests.post(
        f"{BASE_URL}/load_url",
        json={"url": url},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    print(f"Message: {response.json()['result'][:150]}...")
    
    # Step 2: Попросим информацию, которая находится в HTML
    print("\n[Step 2] Задаём вопрос о загруженном контенте...")
    questions = [
        "What HTML elements are on the page?",
        "What content was loaded?",
        "Describe the structure of the loaded HTML",
    ]
    
    for q in questions:
        print(f"\nВопрос: {q}")
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": q},
            timeout=30
        )
        result = response.json()
        print(f"Ответ: {result['answer'][:200]}...")
        print(f"Уверенность: {result['confidence']}")
        if result['sources']:
            print(f"Источники: {result['sources']}")
    
    # Step 3: Тест с JSON контентом
    print("\n" + "="*70)
    print("[Step 3] Тест с JSON контентом")
    print("="*70)
    
    url_json = "https://httpbin.org/json"
    print(f"\nЗагружаем JSON: {url_json}")
    response = requests.post(
        f"{BASE_URL}/load_url",
        json={"url": url_json},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    
    # Вопросы о JSON
    json_questions = [
        "What JSON data was loaded?",
        "Tell me about the JSON structure",
        "What information is in the slideshow?",
    ]
    
    for q in json_questions:
        print(f"\nВопрос: {q}")
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": q},
            timeout=30
        )
        result = response.json()
        print(f"Ответ: {result['answer'][:200]}...")

def test_direct_search():
    """Test direct content search"""
    print("\n" + "="*70)
    print("Тест: Прямой поиск в загруженном контенте")
    print("="*70)
    
    # Загрузим пример
    print("\nЗагружаем Example.com...")
    response = requests.post(
        f"{BASE_URL}/load_url",
        json={"url": "https://example.com"},
        timeout=30
    )
    print(f"Status: {response.status_code}")
    
    # Задаём вопросы о Example.com
    questions = [
        "What is shown on example domain?",
        "Describe the example website content",
        "What information is available about this example?",
    ]
    
    for q in questions:
        print(f"\nВопрос: {q}")
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": q},
            timeout=30
        )
        result = response.json()
        print(f"Ответ: {result['answer'][:250]}...")

if __name__ == "__main__":
    try:
        test_rag_with_web_content()
        test_direct_search()
        print("\n" + "="*70)
        print("✓ Все тесты завершены!")
        print("="*70)
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к API")
        print("Убедитесь, что API запущен: python src/api.py")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
