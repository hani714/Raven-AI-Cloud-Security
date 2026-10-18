from neo4j import AsyncGraphDatabase
from app.utils.load_env import Settings

settings = Settings()

class Neo4jClient:
    def __init__(self, uri = None, user = None, password = None, db_name = "awspentest"):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.db_name = db_name
        self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))

    async def get_session(self):
        return self.driver.session(database=self.db_name)

    async def close(self):
        await self.driver.close()
