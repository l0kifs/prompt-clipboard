import uuid
from datetime import datetime, timezone

from loguru import logger
from sqlmodel import Field, Session, SQLModel, create_engine, select


# SQLModel
class Prompt(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    body: str
    usage_count: int = Field(default=0)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class PromptRelation(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    prompt_id_1: str = Field(foreign_key="prompt.id")
    prompt_id_2: str = Field(foreign_key="prompt.id")
    strength: int = Field(default=1)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Setting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        try:
            self.engine = create_engine(f"sqlite:///{db_path}")
            SQLModel.metadata.create_all(self.engine)
            logger.info("Database initialized successfully", db_path=str(db_path))
        except Exception as e:
            logger.error(
                "Failed to initialize database", db_path=str(db_path), error=str(e)
            )
            raise

    def add_prompt(self, body):
        try:
            with Session(self.engine) as session:
                prompt = Prompt(body=body)
                session.add(prompt)
                session.commit()
                session.refresh(prompt)
                logger.debug("Prompt added", prompt_id=prompt.id, body_length=len(body))
                return prompt.id
        except Exception as e:
            logger.error("Failed to add prompt", error=str(e), body_length=len(body))
            raise

    def update_prompt(self, pid, body):
        try:
            with Session(self.engine) as session:
                prompt = session.get(Prompt, pid)
                if prompt:
                    prompt.body = body
                    prompt.updated_at = datetime.now(timezone.utc).isoformat()
                    session.commit()
                    logger.debug("Prompt updated", prompt_id=pid, body_length=len(body))
                else:
                    logger.warning("Prompt not found for update", prompt_id=pid)
        except Exception as e:
            logger.error("Failed to update prompt", prompt_id=pid, error=str(e))
            raise

    def increment_usage(self, pid):
        with Session(self.engine) as session:
            prompt = session.get(Prompt, pid)
            if prompt:
                prompt.usage_count += 1
                session.commit()

    def delete_prompt(self, pid):
        try:
            with Session(self.engine) as session:
                # First, delete all relations involving this prompt
                relations = session.exec(
                    select(PromptRelation).where(
                        (PromptRelation.prompt_id_1 == pid)
                        | (PromptRelation.prompt_id_2 == pid)
                    )
                ).all()

                relations_count = len(relations)
                for relation in relations:
                    session.delete(relation)

                # Then delete the prompt itself
                prompt = session.get(Prompt, pid)
                if prompt:
                    session.delete(prompt)
                    session.commit()
                    logger.info(
                        "Prompt deleted",
                        prompt_id=pid,
                        relations_deleted=relations_count,
                    )
                else:
                    logger.warning("Prompt not found for deletion", prompt_id=pid)
        except Exception as e:
            logger.error("Failed to delete prompt", prompt_id=pid, error=str(e))
            raise

    def get_all_prompts(self):
        with Session(self.engine) as session:
            return session.exec(
                select(Prompt).order_by(Prompt.usage_count.desc(), Prompt.created_at)
            ).all()

    def search_prompts(self, q, limit=50):
        """Search prompts by words (all words must be present, order doesn't matter)."""
        search_text = q.strip().lower()
        if not search_text:
            return []

        # Split by whitespace to get individual words
        words = search_text.split()
        if not words:
            return []

        try:
            with Session(self.engine) as session:
                # Get all prompts and filter on Python side for proper Unicode support
                # SQLite's LOWER() doesn't work correctly with Cyrillic and other non-ASCII characters
                all_prompts = session.exec(
                    select(Prompt).order_by(Prompt.usage_count.desc())
                ).all()

                # Filter prompts that contain all words (case-insensitive)
                matched = []
                for prompt in all_prompts:
                    body_lower = prompt.body.lower()
                    if all(word in body_lower for word in words):
                        matched.append(prompt)
                        if len(matched) >= limit:
                            break

                if not matched:
                    logger.debug(
                        "No prompts matched search", query=q, words_count=len(words)
                    )
                    return []

                logger.debug("Search completed", query=q, matched_count=len(matched))

                # Get IDs of matched prompts
                matched_ids = {p.id for p in matched}

                # Find all relations involving matched prompts
                all_relations = session.exec(
                    select(PromptRelation)
                    .where(
                        (PromptRelation.prompt_id_1.in_(matched_ids))
                        | (PromptRelation.prompt_id_2.in_(matched_ids))
                    )
                    .order_by(PromptRelation.strength.desc())
                ).all()

                # Build maps: related prompts and cross-references between matched prompts
                related_map = {}  # {matched_id: [(related_prompt, strength), ...]}
                cross_refs = {}  # {matched_id: [(matched_prompt, strength), ...]}

                for rel in all_relations:
                    # Determine which end is in matched and which is the other
                    if (
                        rel.prompt_id_1 in matched_ids
                        and rel.prompt_id_2 in matched_ids
                    ):
                        # Both are matched - add to cross_refs for both
                        if rel.prompt_id_1 not in cross_refs:
                            cross_refs[rel.prompt_id_1] = []
                        if rel.prompt_id_2 not in cross_refs:
                            cross_refs[rel.prompt_id_2] = []

                        prompt2 = session.get(Prompt, rel.prompt_id_2)
                        prompt1 = session.get(Prompt, rel.prompt_id_1)
                        if prompt2:
                            cross_refs[rel.prompt_id_1].append((prompt2, rel.strength))
                        if prompt1:
                            cross_refs[rel.prompt_id_2].append((prompt1, rel.strength))

                    elif rel.prompt_id_1 in matched_ids:
                        # prompt_id_1 is matched, prompt_id_2 is related
                        other_prompt = session.get(Prompt, rel.prompt_id_2)
                        if other_prompt:
                            if rel.prompt_id_1 not in related_map:
                                related_map[rel.prompt_id_1] = []
                            related_map[rel.prompt_id_1].append(
                                (other_prompt, rel.strength)
                            )

                    elif rel.prompt_id_2 in matched_ids:
                        # prompt_id_2 is matched, prompt_id_1 is related
                        other_prompt = session.get(Prompt, rel.prompt_id_1)
                        if other_prompt:
                            if rel.prompt_id_2 not in related_map:
                                related_map[rel.prompt_id_2] = []
                            related_map[rel.prompt_id_2].append(
                                (other_prompt, rel.strength)
                            )

                return matched, related_map, cross_refs
        except Exception as e:
            logger.error("Search failed", query=q, error=str(e))
            raise

    def get_all_prompts_grouped(self):
        """Get all prompts ordered by usage count."""
        return self.get_all_prompts()

    def add_prompt_relations(self, prompt_ids: list[str]):
        """Create or strengthen relations between selected prompts."""
        if len(prompt_ids) < 2:
            return

        try:
            with Session(self.engine) as session:
                relations_updated = 0
                relations_created = 0

                # Create relations for all pairs
                for i in range(len(prompt_ids)):
                    for j in range(i + 1, len(prompt_ids)):
                        id1, id2 = sorted([prompt_ids[i], prompt_ids[j]])

                        # Check if relation exists
                        existing = session.exec(
                            select(PromptRelation).where(
                                (PromptRelation.prompt_id_1 == id1)
                                & (PromptRelation.prompt_id_2 == id2)
                            )
                        ).first()

                        if existing:
                            existing.strength += 1
                            existing.updated_at = datetime.now(timezone.utc).isoformat()
                            relations_updated += 1
                        else:
                            relation = PromptRelation(
                                prompt_id_1=id1, prompt_id_2=id2, strength=1
                            )
                            session.add(relation)
                            relations_created += 1

                session.commit()
                logger.debug(
                    "Prompt relations updated",
                    prompts_count=len(prompt_ids),
                    relations_created=relations_created,
                    relations_updated=relations_updated,
                )
        except Exception as e:
            logger.error(
                "Failed to add prompt relations", prompt_ids=prompt_ids, error=str(e)
            )
            raise

    def is_empty(self):
        with Session(self.engine) as session:
            return not session.exec(select(Prompt)).first()

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with Session(self.engine) as session:
            setting = session.get(Setting, key)
            return setting.value if setting else default

    def set_setting(self, key: str, value: str):
        with Session(self.engine) as session:
            setting = session.get(Setting, key)
            if setting:
                setting.value = value
                setting.updated_at = datetime.now(timezone.utc).isoformat()
            else:
                setting = Setting(key=key, value=value)
                session.add(setting)
            session.commit()
