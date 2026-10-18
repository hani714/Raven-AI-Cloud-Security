from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv

# Ensure environment variables from .env are available
load_dotenv()

@dataclass
class MongoSettings:
    database: str = "awspentest"
    host: str = "localhost"
    port: int = 27017
    username: Optional[str] = None
    password: Optional[str] = None
    replica_set: Optional[str] = None
    auth_source: Optional[str] = None
    tls: bool = False
    direct_connection: bool = False
    app_name: str = "awspentest-backend"
    connect_timeout_ms: int = 10000
    socket_timeout_ms: int = 10000
    read_preference: Optional[str] = None
    srv_uri: Optional[str] = None

    @property
    def uri(self) -> str:
        explicit_uri = self.srv_uri or os.getenv("MONGODB_URI")
        if explicit_uri:
            return explicit_uri

        credentials = ""
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}@"

        query_params = []
        if self.replica_set:
            query_params.append(f"replicaSet={self.replica_set}")
        if self.auth_source:
            query_params.append(f"authSource={self.auth_source}")
        if self.tls:
            query_params.append("tls=true")
        if self.direct_connection:
            query_params.append("directConnection=true")
        if self.app_name:
            query_params.append(f"appName={self.app_name}")
        if self.read_preference:
            query_params.append(f"readPreference={self.read_preference}")

        query = ""
        if query_params:
            query = "?" + "&".join(query_params)

        return f"mongodb://{credentials}{self.host}:{self.port}/{self.database}{query}"

    @classmethod
    def from_env(cls) -> "MongoSettings":
        def as_bool(value: Optional[str], default: bool = False) -> bool:
            if value is None:
                return default
            return value.strip().lower() in {"1", "true", "yes", "on"}

        def as_int(value: Optional[str], default: int) -> int:
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default

        return cls(
            database=os.getenv("MONGODB_DATABASE", "awspentest"),
            host=os.getenv("MONGODB_HOST", "localhost"),
            port=as_int(os.getenv("MONGODB_PORT"), 27017),
            username=os.getenv("MONGODB_USERNAME"),
            password=os.getenv("MONGODB_PASSWORD"),
            replica_set=os.getenv("MONGODB_REPLICA_SET"),
            auth_source=os.getenv("MONGODB_AUTH_SOURCE"),
            tls=as_bool(os.getenv("MONGODB_TLS"), False),
            direct_connection=as_bool(os.getenv("MONGODB_DIRECT_CONNECTION"), False),
            app_name=os.getenv("MONGODB_APP_NAME", "awspentest-backend"),
            connect_timeout_ms=as_int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS"), 10000),
            socket_timeout_ms=as_int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS"), 10000),
            read_preference=os.getenv("MONGODB_READ_PREFERENCE"),
            srv_uri=os.getenv("MONGODB_URI"),
        )

@lru_cache(maxsize=1)
def get_settings() -> MongoSettings:
    return MongoSettings.from_env()
