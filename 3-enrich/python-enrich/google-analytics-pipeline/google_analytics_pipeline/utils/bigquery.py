def jsonschema_to_bq_schema(jsonschema):
    types = {
        "number": "FLOAT",
        "string": "STRING",
        "integer": "INTEGER",
        "boolean": "BOOLEAN"
    }

    schema = []
    for k, v in jsonschema.properties.items():
        if v.type == "object":
            schema.append({
                "name": k,
                "type": "RECORD",
                "fields": jsonschema_to_bq_schema(v)
            })
        elif v.type == "array":
            schema.append({
                "name": k,
                "type": "RECORD",
                "mode": "REPEATED",
                "fields": jsonschema_to_bq_schema(v.get("items"))
            })
        else:
            schema.append({
                "name": k,
                "type": types[v.type]
            })

    return schema
