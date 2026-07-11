# firestore_checkpointer.py
import base64
from langgraph.checkpoint.base import (
    BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from firebase_admin import firestore

class FirestoreCheckpointSaver(BaseCheckpointSaver):
    def __init__(self, firestore_client: firestore.Client):
        super().__init__()
        self.collection = firestore_client.collection("chats")
        self.serde = JsonPlusSerializer()

    def _checkpoints_ref(self, thread_id: str):
        return self.collection.document(thread_id).collection("checkpoints")

    def _encode(self, obj) -> dict:
        type_str, data_bytes = self.serde.dumps_typed(obj)
        return {"type": type_str, "data": base64.b64encode(data_bytes).decode("ascii")}

    def _decode(self, encoded: dict):
        type_str = encoded["type"]
        data_bytes = base64.b64decode(encoded["data"])
        return self.serde.loads_typed((type_str, data_bytes))

    def put(self, config, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions) -> dict:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]

        self._checkpoints_ref(thread_id).document(checkpoint_id).set({
            "checkpoint": self._encode(checkpoint),
            "metadata": self._encode(metadata),
            "parent_id": config["configurable"].get("checkpoint_id"),
            "updated_at": firestore.SERVER_TIMESTAMP,
        })
        self.collection.document(thread_id).set(
            {"latest_checkpoint_id": checkpoint_id, "updated_at": firestore.SERVER_TIMESTAMP},
            merge=True
        )
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}}

    def put_writes(self, config, writes, task_id, task_path="") -> None:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"]["checkpoint_id"]
        doc_ref = self._checkpoints_ref(thread_id).document(checkpoint_id)
        doc_ref.collection("writes").document(task_id).set({
            "writes": self._encode(writes),
            "task_path": task_path,
        })

    def get_tuple(self, config) -> CheckpointTuple | None:
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = config["configurable"].get("checkpoint_id")

        if not checkpoint_id:
            doc = self.collection.document(thread_id).get()
            if not doc.exists:
                return None
            checkpoint_id = doc.to_dict().get("latest_checkpoint_id")
            if not checkpoint_id:
                return None

        cp_doc = self._checkpoints_ref(thread_id).document(checkpoint_id).get()
        if not cp_doc.exists:
            return None

        data = cp_doc.to_dict()
        return CheckpointTuple(
            config={"configurable": {"thread_id": thread_id, "checkpoint_id": checkpoint_id}},
            checkpoint=self._decode(data["checkpoint"]),
            metadata=self._decode(data["metadata"]),
            parent_config={"configurable": {"thread_id": thread_id, "checkpoint_id": data["parent_id"]}}
                if data.get("parent_id") else None,
        )

    def list(self, config, *, filter=None, before=None, limit=None):
        thread_id = config["configurable"]["thread_id"]
        query = self._checkpoints_ref(thread_id).order_by(
            "updated_at", direction=firestore.Query.DESCENDING
        )
        if limit:
            query = query.limit(limit)
        for doc in query.stream():
            data = doc.to_dict()
            yield CheckpointTuple(
                config={"configurable": {"thread_id": thread_id, "checkpoint_id": doc.id}},
                checkpoint=self._decode(data["checkpoint"]),
                metadata=self._decode(data["metadata"]),
                parent_config=None,
            )