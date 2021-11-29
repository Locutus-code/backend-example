#!/usr/bin/env python3

from chalicelib.models.database import SingleTable

if not SingleTable.exists():
    print("Creating DynamoDB table for system")
    SingleTable.create_table()
    exit(0)
print("DynamoDB Table already existed, no need to create")
