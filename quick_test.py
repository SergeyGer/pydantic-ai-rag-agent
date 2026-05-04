#!/usr/bin/env python3
"""
Быстрый тест парсинга интернета
"""
import requests

BASE_URL = "http://localhost:8001"

print("\n=== Тест 1: Загрузка JSON ===")
r = requests.post(f"{BASE_URL}/load_url", json={"url": "https://httpbin.org/json"}, timeout=30)
print(f"✓ JSON загружен: {r.json()['message']}")

print("\n=== Тест 2: Загрузка HTML ===")
r = requests.post(f"{BASE_URL}/load_url", json={"url": "https://httpbin.org/html"}, timeout=30)
print(f"✓ HTML загружен: {r.json()['message']}")

print("\n=== Тест 3: Вопрос о HTML контенте ===")
r = requests.post(f"{BASE_URL}/ask", json={"question": "What HTML content was loaded?"}, timeout=30)
ans = r.json()['answer']
print(f"Ответ: {ans[:200]}...")

print("\n=== Тест 4: Вопрос о JSON контенте ===")
r = requests.post(f"{BASE_URL}/ask", json={"question": "What JSON data exists in the loaded content?"}, timeout=30)
ans = r.json()['answer']
print(f"Ответ: {ans[:200]}...")

print("\n✓ Все тесты завершены!")
