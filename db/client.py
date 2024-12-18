from neomodel import db, config, StructuredNode

class Neo4jClient:
    def __init__(self,username: str, password: str,  uri: str, db_name: str):
        """
        Initialize the Neo4j connection.
        """
        config.DATABASE_URL = f"bolt://{username}:{password}@{uri}"
        # config.DATABASE_NAME = db_name

    def create_node(self, node_class: type[StructuredNode], properties) -> StructuredNode:
        """
        Create or update a node of the specified type.
        """
        with db.transaction:
            node = node_class(**properties)
            node.save()
            return node

    def get_node(self, node_class: type[StructuredNode], filters) -> StructuredNode:
        """
        Retrieve a node of the specified type by its properties.
        """
        with db.transaction:
            return node_class.nodes.get_or_none(**filters)

    def create_or_update_node(self, node_class: type[StructuredNode], properties: dict) -> StructuredNode:
        """
        Generalized Cypher-based function to create or update a node, ensuring no duplicates.
        """
        unique_field = getattr(node_class.Meta, 'unique_identifier', None)
        if not unique_field:
            raise ValueError(f"The model {node_class.__name__} does not define a unique_identifier in its Meta class.")

        unique_value = properties.get(unique_field)
        if not unique_value:
            raise ValueError(f"Missing required unique field '{unique_field}' in properties.")

        # Dynamically generate the MERGE query
        query = f"""
        MERGE (n:{node_class.__label__} {{{unique_field}: $unique_value}})
        ON CREATE SET {', '.join(f"n.{k} = ${k}" for k in properties.keys())}
        ON MATCH SET {', '.join(f"n.{k} = ${k}" for k in properties.keys())}
        RETURN n
        """
        params = {'unique_value': unique_value, **properties}

        with db.transaction:
            results, _ = db.cypher_query(query, params)
            return node_class.inflate(results[0][0])  # Convert raw result into node instance

    def delete_node(self, node_class: type[StructuredNode], **filters):
        """
        Delete a node of the specified type and its relationships.
        """
        with db.transaction:
            node = self.get_node(node_class, **filters)
            if node:
                node.delete()

    # old code
    # def create_relationship(
    #     self,
    #     from_node: StructuredNode,
    #     rel_name: str,
    #     to_node: StructuredNode,
    # ):
    #     """
    #     Create a relationship between two nodes dynamically.
    #     """
    #     with db.transaction:
    #         # Check if the relationship exists dynamically
    #         if not hasattr(from_node.__class__, rel_name):
    #             raise ValueError(f"Relationship '{rel_name}' not found on {from_node.__class__.__name__}")
    #
    #         # Access the relationship
    #         relationship = getattr(from_node, rel_name, None)
    #         # Connect the nodes
    #         relationship.connect(to_node)

    def create_relationship(
            self,
            from_node: StructuredNode,
            rel_name: str,
            to_node: StructuredNode,
    ):
        """
        Create a relationship between two nodes dynamically.
        """
        with db.transaction:
            # Ensure the relationship exists in the class
            if not hasattr(from_node.__class__, rel_name):
                raise ValueError(f"Relationship '{rel_name}' not found on {from_node.__class__.__name__}")

            # Extract unique identifiers for the nodes
            from_id = from_node.element_id  # Assuming `element_id` uniquely identifies the node
            to_id = to_node.element_id

            # Dynamically generate Cypher query to avoid Cartesian product
            query = f"""
            MATCH (us), (them)
            WHERE elementId(us) = $from_id AND elementId(them) = $to_id
            MERGE (us)-[r:{rel_name.upper()}]-(them)
            RETURN r
            """
            params = {"from_id": from_id, "to_id": to_id}

            # Execute query
            db.cypher_query(query, params)

    def get_related_nodes(self, node: StructuredNode, rel_name: str):
        """
        Get related nodes for a specified relationship.
        """
        with db.transaction:
            relationship = getattr(node, rel_name, None)
            if not relationship:
                raise ValueError(f"Relationship '{rel_name}' not found on {node.__class__.__name__}")
            return relationship.all()

    def health_check(self) -> bool:
        """
        Check the health of the database connection.
        Returns True if the connection is healthy, otherwise False.
        """
        try:
            # Test a simple query to check the connection
            db.cypher_query("RETURN 1")
            return True
        except Exception as e:
            print(f"Health check failed: {e}")  #TODO: Log error (optional)
            return False
