#check s3_connector_works.
from app.data_platform.connectors.s3 import S3Connector

s3_connector = S3Connector(bucket="waterdip-data-lake")
s3_connector.write_bytes("raw/volve/production/s3connector_test.txt", b"hello from s3 connector")
print(s3_connector.exists("raw/volve/production/s3connector_test.txt"))
print(s3_connector.read_bytes("raw/volve/production/s3connector_test.txt").decode())

#build inventory from abstracted data platform (our inventory does not care about where the data-source is hosted in order to build it).
from app.data_platform.inventory.file_inventory import build_file_inventory

inventory = build_file_inventory(
    connector=s3_connector,
    prefix="raw/volve",
)

for item in inventory:
    print(item.path, item.size_bytes, item.source)
