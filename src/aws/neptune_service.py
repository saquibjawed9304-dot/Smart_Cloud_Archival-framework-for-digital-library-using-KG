import boto3


class NeptuneService:

    def __init__(self, endpoint=None, region_name="ap-south-1"):
        self.endpoint = endpoint
        self.client = boto3.client("neptunedata", region_name=region_name)

    def create_node(self, node_id, node_type, properties):
        query = "MERGE (n:Entity {id: $id}) SET n.type = $type, n.properties = $properties"
        return self.client.execute_open_cypher_query(
            openCypherQuery=query,
            parameters={"id": node_id, "type": node_type, "properties": properties},
        )

    def create_relationship(
        self,
        source,
        relationship,
        target
    ):

        query = (
            "MATCH (a:Entity {id: $source}), (b:Entity {id: $target}) "
            "MERGE (a)-[r:RELATED {type: $relationship}]->(b)"
        )
        return self.client.execute_open_cypher_query(
            openCypherQuery=query,
            parameters={"source": source, "target": target, "relationship": relationship},
        )