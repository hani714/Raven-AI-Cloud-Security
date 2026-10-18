CREATE_PATH = """
MERGE (p:Path {scan_id: $scan_id, path_id: $path_id})
SET p.title = $title
"""

CREATE_COMMAND = """
MERGE (c:Command {id: $id})
SET c.step = $step,
    c.description = $desc,
    c.command = $command
"""

LINK_PATH_TO_COMMAND = """
MATCH (p:Path {scan_id: $scan_id, path_id: $path_id}), (c:Command {id: $cid})
MERGE (p)-[:STARTS_WITH]->(c)
"""

LINK_COMMANDS = """
[MATCH (a:Command {id: $prev}), (b:Command {id: $curr}) MERGE (a)-[:NEXT]->(b)]
"""