"""One-off manual verification script for matchmaking + live duel gameplay.

Not part of the app; registers two throwaway users, queues them both for a
duel, plays through it (always picking option A), and prints the final
scores/rating deltas so a human can sanity-check the whole real-time flow.
"""

from __future__ import annotations

import asyncio
import json
import time

import httpx
import websockets

BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"


async def register_or_login(client: httpx.AsyncClient, suffix: str) -> str:
    payload = {
        "name": f"Duel Bot {suffix}",
        "email": f"duelbot{suffix}@example.com",
        "username": f"duelbot{suffix}",
        "password": "TestPass123!",
    }
    resp = await client.post(f"{BASE}/api/auth/register", json=payload)
    if resp.status_code == 409:
        resp = await client.post(f"{BASE}/api/auth/login", json={"email_or_username": payload["email"], "password": payload["password"]})
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print(f"[{suffix}] authenticated, rating={resp.json()['user']['user_rating']}")
    return token


async def play(suffix: str, token: str, results: dict) -> None:
    async with websockets.connect(f"{WS_BASE}/api/ws/matchmaking?token={token}") as mm:
        msg = json.loads(await mm.recv())
        assert msg["type"] == "queued", msg
        print(f"[{suffix}] queued")
        while True:
            msg = json.loads(await mm.recv())
            if msg["type"] == "match_found":
                duel_id = msg["duel_id"]
                print(f"[{suffix}] matched -> duel {duel_id}, opponent={msg['opponent']}")
                break

    async with websockets.connect(f"{WS_BASE}/api/ws/duels/{duel_id}?token={token}") as duel:
        while True:
            msg = json.loads(await duel.recv())
            t = msg["type"]
            if t in ("waiting_for_opponent", "opponent_joined"):
                print(f"[{suffix}] {t}")
            elif t == "question":
                print(f"[{suffix}] Q{msg['index'] + 1}/{msg['total']}: {msg['question']['text'][:50]}")
                await asyncio.sleep(0.2)
                await duel.send(json.dumps({"type": "answer", "index": msg["index"], "answer": "A"}))
            elif t == "score_update":
                pass
            elif t == "reveal":
                print(f"[{suffix}] reveal: correct={msg['correct_answer']} scores={msg['scores']}")
            elif t == "duel_end":
                print(f"[{suffix}] DUEL END: {msg}")
                results[suffix] = msg
                return
            elif t == "opponent_left":
                print(f"[{suffix}] opponent left!")
                results[suffix] = msg
                return


async def main() -> None:
    suffix = str(int(time.time()))[-5:]
    async with httpx.AsyncClient() as client:
        token_a = await register_or_login(client, f"a{suffix}")
    async with httpx.AsyncClient() as client:
        token_b = await register_or_login(client, f"b{suffix}")

    results: dict = {}
    await asyncio.gather(
        play(f"A-{suffix}", token_a, results),
        play(f"B-{suffix}", token_b, results),
    )
    print("\n=== RESULTS ===")
    for k, v in results.items():
        print(k, v)


if __name__ == "__main__":
    asyncio.run(main())
