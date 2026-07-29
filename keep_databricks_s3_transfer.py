# import json
# import os
# from datetime import datetime, timezone
# from pathlib import Path

# import boto3
# from boto3.s3.transfer import TransferConfig
# from botocore.config import Config

# dbutils.widgets.text("dataset_id", "production")
# dbutils.widgets.text("target_bucket", "waterdip-data-lake")
# dbutils.widgets.dropdown("overwrite", "false", ["false", "true"])

# dataset_id = dbutils.widgets.get("dataset_id").strip()
# target_bucket = dbutils.widgets.get("target_bucket").strip()
# overwrite = dbutils.widgets.get("overwrite").lower() == "true"

# SOURCE_VOLUME = Path(
#     "/Volumes/equinor_asa_volve_data_village/public/volvezipfiles"
# )

# DATASETS = {
#     "production": {
#         "filename": "Volve_Production_data.zip",
#         "target_key": "raw/volve/production/Volve_Production_data.zip",
#     },
#     "reports": {
#         "filename": "Volve_Reports.zip",
#         "target_key": "raw/volve/reports/Volve_Reports.zip",
#     },
#     "technical": {
#         "filename": "Volve_Well_technical_data.zip",
#         "target_key": "raw/volve/technical/Volve_Well_technical_data.zip",
#     },
#     "geophysics": {
#         "filename": "Volve_Geophysical_Interpretations.zip",
#         "target_key": (
#             "raw/volve/geophysics/"
#             "Volve_Geophysical_Interpretations.zip"
#         ),
#     },
#     "eclipse": {
#         "filename": "Volve_Reservoir_Model-Eclipse_model.zip",
#         "target_key": (
#             "raw/volve/eclipse/"
#             "Volve_Reservoir_Model-Eclipse_model.zip"
#         ),
#     },
#     "rms": {
#         "filename": "Volve_Reservoir_Model-RMS_model.zip",
#         "target_key": (
#             "raw/volve/rms/"
#             "Volve_Reservoir_Model-RMS_model.zip"
#         ),
#     },
#     "drilling": {
#         "filename": "Volve_WITSML Realtime drilling data.zip",
#         "target_key": (
#             "raw/volve/drilling/"
#             "Volve_WITSML Realtime drilling data.zip"
#         ),
#     },
#     "well_logs": {
#         "filename": "Volve_Well_logs.zip",
#         "target_key": "raw/volve/well_logs/Volve_Well_logs.zip",
#     },
#     "well_logs_per_well": {
#         "filename": "Volve_Well_logs_pr_WELL.zip",
#         "target_key": (
#             "raw/volve/well_logs_per_well/"
#             "Volve_Well_logs_pr_WELL.zip"
#         ),
#     },
#     "seismic_vsp": {
#         "filename": "Volve_Seismic_VSP.zip",
#         "target_key": (
#             "raw/volve/geophysics/seismic_vsp/"
#             "Volve_Seismic_VSP.zip"
#         ),
#     },
# }




# if dataset_id not in DATASETS:
#     valid = ", ".join(sorted(DATASETS))
#     raise ValueError(
#         f"Unknown dataset_id {dataset_id!r}. Valid values: {valid}"
#     )

# dataset = DATASETS[dataset_id]
# source_path = SOURCE_VOLUME / dataset["filename"]
# target_key = dataset["target_key"]

# print(f"Dataset: {dataset_id}")
# print(f"Source: {source_path}")
# print(f"Target: s3://{target_bucket}/{target_key}")
# print(f"Overwrite: {overwrite}")


# if not source_path.is_file():
#     raise FileNotFoundError(
#         f"Marketplace source file was not found: {source_path}"
#     )

# source_size = source_path.stat().st_size

# print(f"Source exists: {source_path}")
# print(f"Size: {source_size:,} bytes")
# print(f"Size: {source_size / (1024 ** 3):,.3f} GiB")


# dbutils.secrets.list("waterdip-aws")

# access_key = dbutils.secrets.get(
#     scope="waterdip-aws",
#     key="access-key-id",
# )

# secret_key = dbutils.secrets.get(
#     scope="waterdip-aws",
#     key="secret-access-key",
# )

# print("Access key loaded:", bool(access_key))
# print("Secret key loaded:", bool(secret_key))

# import boto3
# from botocore.config import Config

# s3 = boto3.client(
#     "s3",
#     aws_access_key_id=access_key,
#     aws_secret_access_key=secret_key,
#     config=Config(
#         retries={
#             "max_attempts": 10,
#             "mode": "adaptive",
#         }
#     ),
# )

# response = s3.list_objects_v2(
#     Bucket="waterdip-data-lake",
#     Prefix="raw/volve/",
#     MaxKeys=10,
# )

# print("S3 connection successful")
# print("Objects found:", response.get("KeyCount", 0))

# test_key = "manifests/databricks_transfers/connection_test.txt"

# s3.put_object(
#     Bucket="waterdip-data-lake",
#     Key=test_key,
#     Body=b"Databricks connection to WaterDIP S3 succeeded.",
# )

# metadata = s3.head_object(
#     Bucket="waterdip-data-lake",
#     Key=test_key,
# )

# print("Write successful")
# print("Bytes written:", metadata["ContentLength"])

# from pathlib import Path

# source_root = Path(
#     "/Volumes/equinor_asa_volve_data_village/public/volvezipfiles"
# )

# for path in sorted(source_root.iterdir()):
#     print(path.name, path.stat().st_size)

# from boto3.s3.transfer import TransferConfig

# source_path = (
#     source_root
#     / "Volve_Production_data.zip"
# )

# target_bucket = "waterdip-data-lake"
# target_key = (
#     "raw/volve/production/"
#     "Volve_Production_data.zip"
# )

# if not source_path.is_file():
#     raise FileNotFoundError(
#         f"Source file not found: {source_path}"
#     )

# source_size = source_path.stat().st_size

# print("Source:", source_path)
# print("Source size:", source_size)
# print("Target:", f"s3://{target_bucket}/{target_key}")

# transfer_config = TransferConfig(
#     multipart_threshold=64 * 1024 * 1024,
#     multipart_chunksize=64 * 1024 * 1024,
#     max_concurrency=4,
#     use_threads=True,
# )

# s3.upload_file(
#     Filename=str(source_path),
#     Bucket=target_bucket,
#     Key=target_key,
#     Config=transfer_config,
# )

# print("Upload completed")

# uploaded = s3.head_object(
#     Bucket=target_bucket,
#     Key=target_key,
# )

# target_size = int(uploaded["ContentLength"])

# print("Source size:", source_size)
# print("Target size:", target_size)

# if target_size != source_size:
#     raise RuntimeError(
#         "Transfer verification failed: sizes do not match"
#     )

# print("Transfer verified successfully")


# import json
# from datetime import datetime, timezone

# completed_at = datetime.now(timezone.utc)

# manifest = {
#     "dataset_id": "production",
#     "source_system": "databricks_marketplace",
#     "source_catalog": "equinor_asa_volve_data_village",
#     "source_path": str(source_path),
#     "source_size_bytes": source_size,
#     "target_bucket": target_bucket,
#     "target_key": target_key,
#     "target_size_bytes": target_size,
#     "status": "completed",
#     "completed_at_utc": completed_at.isoformat(),
# }

# manifest_key = (
#     "manifests/databricks_transfers/"
#     f"production_{completed_at:%Y%m%dT%H%M%SZ}.json"
# )

# s3.put_object(
#     Bucket=target_bucket,
#     Key=manifest_key,
#     Body=json.dumps(manifest, indent=2).encode("utf-8"),
#     ContentType="application/json",
# )

# print(f"Manifest written to s3://{target_bucket}/{manifest_key}")


# job_result = {
#     "dataset_id": dataset_id,
#     "target_bucket": target_bucket,
#     "target_key": target_key,
#     "source_size_bytes": source_size,
#     "target_size_bytes": target_size,
#     "manifest_key": manifest_key,
#     "status": "completed",
# }

# dbutils.notebook.exit(json.dumps(job_result))
