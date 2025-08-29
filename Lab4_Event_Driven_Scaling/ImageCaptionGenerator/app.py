import os, threading, time, json, io, base64
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient, BlobClient
import requests

# Setting Environment Variables

# Storage Account Variables
storage_account_url = os.environ.get("storage-account-url")
storage_account_connection_string = os.environ.get("storage-account-connection-string")
container_name = os.environ.get("container-name")
batch_size = int(os.environ.get("batch-size", 4))
blob_prefix = os.environ.get("blob-prefix", "incoming-")

# Azure OpenAI variables
azure_openai_endpoint = os.environ.get("azure-openai-endpoint")
azure_openai_deployment = os.environ.get("azure-openai-deployment")
azure_openai_api_version = os.environ.get("azure-openai-api-version", "2024-12-01-preview")
azure_openai_api_key = os.environ.get("azure-openai-api-key")

# Creating the storage account clients
blob_service_client = BlobServiceClient.from_connection_string(storage_account_connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Creating the Azure OpenAI Client
azure_openai_client = AzureOpenAI(
    api_version=azure_openai_api_version,
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key,
)

app = Flask(__name__)
stats = {"processed": 0, "errors": 0, "last_error": None}

def get_url_for_blob(blob_name: str) -> str:
    """Generate a URL for the blob."""
    return f"{storage_account_url}/{container_name}/{blob_name}"

def describe_image_with_aoai(image_url: str) -> str:
    """
    Call Azure OpenAI Chat Completions with an image URL.
    """

    response = azure_openai_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "text", "text": "Generate a concise, human-friendly caption."},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]},
        ],
        max_tokens=8192,
        temperature=0.7,
        top_p=0.95,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        model=azure_openai_deployment,
    )

    return response.choices[0].message.content.strip()

def process_one_blob(blob_name: str):
    # Acquire a short lease to avoid duplicate processing across replicas

    bc: BlobClient = container_client.get_blob_client(blob_name)
    lease = bc.acquire_lease(lease_duration=15)  # lease duration in "seconds"
    try:
        try:
            image_url = get_url_for_blob(blob_name)
            caption = describe_image_with_aoai(image_url)
        
        except Exception as e:
            data = bc.download_blob().readall()
            b64 = base64.b64encode(data).decode("utf-8")
            caption = describe_image_with_aoai(f"data:image/jpeg;base64,{b64}")
        
        # Write caption JSON into captions/<name>.json
        caption_blob = f"captions/{os.path.basename(blob_name)}.json"
        container_client.upload_blob(
                name=caption_blob,
                data=json.dumps({"blob": blob_name, "caption": caption}),
                overwrite=True,
            )
        
        # Move original to processed/
        new_name = f"processed/{os.path.basename(blob_name)}"
        container_client.get_blob_client(new_name).start_copy_from_url(bc.url)
        bc.delete_blob(delete_snapshots="include", lease=lease)

        stats["processed"] += 1

    finally:
        try:
            lease.release()
        except Exception:
            pass


def worker_loop():
    while True:
        try:
            # Pull a small batch each tick
            batch = []
            for b in container_client.list_blobs(name_starts_with=blob_prefix):
                batch.append(b.name)
                if len(batch) >= batch_size:
                    break
            if not batch:
                time.sleep(2)  # idle; scaler may scale to 0
                continue

            for name in batch:
                try:
                    process_one_blob(name)
                except Exception as e:
                    stats["errors"] += 1
                    stats["last_error"] = repr(e)
        except Exception as e:
            stats["errors"] += 1
            stats["last_error"] = repr(e)
            time.sleep(3)

@app.route("/healthz")
def healthz():
    return "ok"

@app.route("/stats")
def get_stats():
    return jsonify(stats)

if __name__ == "__main__":
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)