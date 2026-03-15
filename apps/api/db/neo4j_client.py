"""Neo4j 图数据库客户端"""

from neo4j import AsyncGraphDatabase
from config import settings


class Neo4jClient:
    def __init__(self):
        self._driver = None

    async def connect(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        # 验证连接
        try:
            await self._driver.verify_connectivity()
            print(f"✅ Neo4j connected: {settings.neo4j_uri}")
        except Exception as e:
            print(f"⚠️ Neo4j connection failed (will retry on demand): {e}")

    async def close(self):
        if self._driver:
            await self._driver.close()

    @property
    def driver(self):
        return self._driver

    async def execute_read(self, query: str, params: dict | None = None):
        """执行只读 Cypher 查询 — 使用显式读事务"""
        if not self._driver:
            raise RuntimeError("Neo4j not connected. Call connect() first.")
        async with self._driver.session() as session:
            async def _work(tx):
                result = await tx.run(query, params or {})
                return [record.data() async for record in result]
            return await session.execute_read(_work)

    async def execute_write(self, query: str, params: dict | None = None):
        """执行写入 Cypher 查询 — 使用显式写事务"""
        if not self._driver:
            raise RuntimeError("Neo4j not connected. Call connect() first.")
        async with self._driver.session() as session:
            async def _work(tx):
                result = await tx.run(query, params or {})
                return [record.data() async for record in result]
            return await session.execute_write(_work)


neo4j_client = Neo4jClient()
