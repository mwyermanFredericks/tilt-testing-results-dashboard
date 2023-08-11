from __future__ import annotations

import os

from dash import CeleryManager, DiskcacheManager


class CacheSingleton:
    background_callback_manager: CeleryManager | DiskcacheManager
    _instance: "CacheSingleton" | None = None

    def __new__(cls, *args, **kwargs):
        if CacheSingleton._instance is None:
            CacheSingleton._instance = object.__new__(cls)

            if "REDIS_URL" in os.environ:
                # Use Redis & Celery if REDIS_URL set as an env variable
                from celery import Celery

                celery_app = Celery(
                    __name__,
                    broker=os.environ["REDIS_URL"],
                    backend=os.environ["REDIS_URL"],
                )
                CacheSingleton._instance.background_callback_manager = CeleryManager(
                    celery_app
                )
            else:
                # Diskcache for non-production apps when developing locally
                import diskcache

                cache = diskcache.Cache("./cache")
                CacheSingleton._instance.background_callback_manager = DiskcacheManager(
                    cache
                )

        return CacheSingleton._instance
