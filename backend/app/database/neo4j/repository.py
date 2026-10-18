from .config import Neo4jClient
from . import queries

class Neo4jRepository:
    def __init__(self, client: Neo4jClient):
        self.client = client

    async def run_query(self, tx, query: str, **parameters):
        result = await tx.run(query, **parameters)
        await result.consume()  # Ensure the query is executed
        
    async def insert_paths(self, scan_id, exploitation_commands):
        async with await self.client.get_session() as session:
            for path in exploitation_commands:
                async with session.begin_transaction() as tx:
                    await self.run_query(tx, queries.CREATE_PATH, scan_id=scan_id, path_id=path["path_id"], title=path["path_title"])

                    prev_node_id = None

                    for cmd in path["commands"]:
                        node_id = f"{scan_id}-{path['path_id']}-{cmd['step']}"

                        await self.run_query(tx, queries.CREATE_COMMAND, id=node_id, step=cmd["step"], desc=cmd["description"], command=cmd["command"])

                        if prev_node_id is None:
                            await self.run_query(tx, queries.LINK_PATH_TO_COMMAND, scan_id=scan_id, path_id=path["path_id"], cid=node_id)
                        else:
                            await self.run_query(tx, queries.LINK_COMMANDS, prev=prev_node_id, curr=node_id)

                        prev_node_id = node_id