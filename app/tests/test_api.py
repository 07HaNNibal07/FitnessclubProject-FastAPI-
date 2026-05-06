from fastapi.testclient import TestClient
from app.main import app
import asyncio

import pytest


@pytest.mark.asyncio
async def test_health(user):
    response = await user.get("/clients/all_clients")
    assert response.status_code in (200, 404)
    
    
@pytest.mark.asyncio
async def test_register(user):
    response = await user.post(
        "/clients/register_client",
        json={
            "name": "Ilgar",
            "surname": "Test",
            "email": "test@test.com",
            "password": "StrongPass1",  
            "age": 20,
            "number": "1234567890",
            "trainer_id": None
        }
    )

    assert response.status_code in (200, 201)

@pytest.mark.asyncio
async def test_register_trainer(user):
    response = await user.post(
        "/trainers/create_trainer",
        json={
            "name": "Trainer",
            "surname": "Test",
            "email": "trainer@test.com",
            "password": "StrongPass1",  
            "info": 'The best trainer in the gym',
            "age": 20,
            "number": "1234567890"
        }
    )

    assert response.status_code in (200, 201)

@pytest.mark.asyncio
async def test_register_invalid_password(user):
    response = await user.post(
        "/clients/register_client",
        json={
            "name": "Ilgar",
            "surname": "Test",
            "email": "bad@test.com",
            "password": "123",  # слабый пароль
            "age": 20,
            "number": "1234567890",
            "trainer_id": None
        }
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login(user):
    response = await user.post(
        '/login',
        data = {
            "username":"test@test.com",
            "password": "StrongPass1"
        }
        )
    assert response.status_code ==200

@pytest.mark.asyncio
async def test_invalid_login(user):
    response = await user.post(
        '/login',
        data = {
            "username":"test@test.com",
            "password": "StrongPass1уау"
        }
        )
    assert response.status_code == 403