"""Local NuNER Zero engine using GLiNER."""

from __future__ import annotations

import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from typing import Iterable

from gliner import GLiNER

from app.config.settings import NER_LABELS
from app.entities.models import Entity

MODEL_LOCAL_PATH = (
    "/root/.cache/huggingface/hub/"
    "models--numind--NuNerZero/snapshots/"
    "c90187673f464518dca09f41689184ed6976242c"
)

class NuNerEngine:
    """Load NuNER Zero directly from the local Hugging Face snapshot."""

    def __init__(self) -> None:
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return

        self._model = GLiNER.from_pretrained(
            MODEL_LOCAL_PATH,
            local_files_only=True,
        )

    def detect(
        self,
        text: str,
        selected_types: Iterable[str],
        threshold: float = 0.40,
    ) -> list[Entity]:

        selected_set = set(selected_types)

        selected = [
            label
            for label in ("PER", "ORG", "LOC")
            if label in selected_set
        ]

        if not text.strip() or not selected:
            return []

        self._load()

        labels = [
            NER_LABELS[label].lower()
            for label in selected
        ]

        predictions = self._model.predict_entities(
            text,
            labels,
            threshold=threshold,
        )

        label_to_code = {
            value.lower(): key
            for key, value in NER_LABELS.items()
        }

        results: list[Entity] = []

        for prediction in predictions:
            label_text = str(
                prediction.get("label", "")
            ).strip().lower()

            canonical = label_to_code.get(label_text)

            start = int(prediction.get("start", -1))
            end = int(prediction.get("end", -1))
            entity_text = str(prediction.get("text", ""))

            if (
                canonical is None
                or start < 0
                or end <= start
                or end > len(text)
            ):
                continue

            observed = text[start:end]

            if observed != entity_text:
                entity_text = observed

            results.append(
                Entity(
                    text=entity_text,
                    label=canonical,
                    start=start,
                    end=end,
                    score=float(
                        prediction.get("score", 0.0)
                    ),
                    source="ner",
                )
            )

        return results
