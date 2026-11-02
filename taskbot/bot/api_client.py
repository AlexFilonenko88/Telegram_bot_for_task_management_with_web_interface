import httpx
from typing import List, Optional

from bot.config import API_URL, BOT_SECRET


class APIClient:
    def __init__(self):
        self.base_url = API_URL
        self.headers = {"X-Bot-Secret": BOT_SECRET}

    async def register_user(self, telegram_id: int, username: str, first_name: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/users/register",
                json={
                    "telegram_id": telegram_id,
                    "username": username,
                    "first_name": first_name
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_tasks(self, user_id: int, limit: int = 100, offset: int = 0) -> List[dict]:
        """Постраничный список задач пользователя.

        Returns:
            Элементы страницы (поле items пагинированного ответа).
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/tasks",
                params={"user_id": user_id, "limit": limit, "offset": offset},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["items"]

    async def create_task(self, title: str, description: Optional[str], user_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/tasks",
                json={
                    "title": title,
                    "description": description,
                    "user_id": user_id
                },
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def complete_task(self, task_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/api/tasks/{task_id}/complete",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
