import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import ClientAuthenticationError
import pandas as pd

# Load environment variables from .env file
load_dotenv()

def get_azure_credential():
    """Get Azure credential based on available environment variables."""
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([tenant_id, client_id, client_secret]):
        print("Warning: Service Principal credentials not found in environment variables.")
        print("Attempting to use DefaultAzureCredential...")
        return DefaultAzureCredential()

    try:
        return ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
    except Exception as e:
        print(f"Error creating ClientSecretCredential: {str(e)}")
        print("Falling back to DefaultAzureCredential...")
        return DefaultAzureCredential()

def get_storage_accounts(subscription_id):
    try:
        credential = get_azure_credential()
        storage_client = StorageManagementClient(credential, subscription_id)
        accounts = list(storage_client.storage_accounts.list())
        return accounts
    except ClientAuthenticationError as auth_error:
        print("\n❌ Authentication Error:")
        print(str(auth_error))
        print("\nPlease ensure your .env file contains the correct values for:")
        print("- AZURE_TENANT_ID")
        print("- AZURE_CLIENT_ID")
        print("- AZURE_CLIENT_SECRET")
        print("- AZURE_SUBSCRIPTION_ID")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error listing storage accounts: {str(e)}")
        sys.exit(1)

def get_used_capacity(subscription_id, resource_group_name, account_name):
    credential = DefaultAzureCredential()
    monitor_client = MonitorManagementClient(credential, subscription_id)

    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.Storage/storageAccounts/{account_name}"
    )

    try:
        metrics_data = monitor_client.metrics.list(
            resource_id,
            timespan="PT12H",
            interval="PT1H",
            metricnames="UsedCapacity",
            aggregation="Average",
            metricnamespace="Microsoft.Storage/storageAccounts"
        )

        for item in metrics_data.value:
            for timeseries in item.timeseries:
                for data in reversed(timeseries.data):  # Most recent first
                    if data.average is not None:
                        used_bytes = data.average
                        gb = used_bytes / (1024 ** 3)
                        tib = used_bytes / (1024 ** 4)

                        if tib >= 1:
                            return f"{round(tib, 2)} TiB"
                        else:
                            return f"{round(gb, 2)} GB"

        return "N/A"

    except Exception as e:
        print(f"❌ Error retrieving UsedCapacity for {account_name}: {str(e)}")
        return "N/A"

# Replace with your subscription ID or from environment
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
print(f"Using subscription ID: {subscription_id}")
if not subscription_id:
    raise ValueError("Please set the AZURE_SUBSCRIPTION_ID environment variable.")

accounts = get_storage_accounts(subscription_id)
storage_data = []

print("📦 Collecting storage account usage data...\n")

for account in accounts:
    account_name = account.name
    resource_group = account.id.split("/")[4]
    sub_id = account.id.split("/")[2]

    used_capacity_str = get_used_capacity(sub_id, resource_group, account_name)

    storage_data.append({
        'Storage Account': account_name,
        'Resource Group': resource_group,
        'Subscription ID': sub_id,
        'Used Capacity': used_capacity_str
    })

# Display the results
storage_list = pd.DataFrame(storage_data)
print(storage_list.to_string(index=False, justify='left'))

# Save to CSV (optional)
# storage_list.to_csv('storage_accounts_usage.csv', index=False)
# print("\n✅ Done. Data shows GB or TiB based on size.")
