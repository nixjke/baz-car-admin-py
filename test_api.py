"""
Простой тест API
"""
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"

def test_health():
    """Тест проверки здоровья"""
    response = requests.get("http://localhost:8080/health")
    print(f"Health check: {response.status_code}")
    print(response.json())

def test_register():
    """Тест регистрации"""
    user_data = {
        "email": "test@example.com",
        "password": "123456",
        "first_name": "Тест",
        "last_name": "Пользователь"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register: {response.status_code}")
    if response.status_code == 201:
        print("Регистрация успешна!")
        return response.json()["token"]
    else:
        print(f"Ошибка регистрации: {response.text}")
        return None

def test_login():
    """Тест входа"""
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        print("Вход успешен!")
        return response.json()["token"]
    else:
        print(f"Ошибка входа: {response.text}")
        return None

def test_cars(token):
    """Тест получения автомобилей"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cars", headers=headers)
    print(f"Get cars: {response.status_code}")
    if response.status_code == 200:
        cars = response.json()
        print(f"Найдено автомобилей: {len(cars)}")
    else:
        print(f"Ошибка получения автомобилей: {response.text}")

def test_create_car(token):
    """Тест создания автомобиля"""
    car_data = {
        "name": "Toyota Camry",
        "category": "sedan",
        "price": 5000,
        "description": "Комфортный седан"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/cars", json=car_data, headers=headers)
    print(f"Create car: {response.status_code}")
    if response.status_code == 201:
        print("Автомобиль создан успешно!")
        return response.json()["id"]
    else:
        print(f"Ошибка создания автомобиля: {response.text}")
        return None

if __name__ == "__main__":
    print("Запуск тестов API...")
    
    # Тест проверки здоровья
    test_health()
    print()
    
    # Тест регистрации
    token = test_register()
    print()
    
    if not token:
        # Если регистрация не удалась, пробуем войти
        token = test_login()
        print()
    
    if token:
        # Тест получения автомобилей
        test_cars(token)
        print()
        
        # Тест создания автомобиля
        car_id = test_create_car(token)
        print()
        
        if car_id:
            # Тест получения конкретного автомобиля
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/cars/{car_id}", headers=headers)
            print(f"Get car {car_id}: {response.status_code}")
            if response.status_code == 200:
                print("Автомобиль получен успешно!")
            else:
                print(f"Ошибка получения автомобиля: {response.text}")
    
    print("Тесты завершены!")
