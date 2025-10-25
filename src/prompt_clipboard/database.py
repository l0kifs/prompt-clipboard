import uuid
from datetime import datetime, timezone

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


class Setting(SQLModel, table=True):
    key: str = Field(primary_key=True)
    value: str
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        SQLModel.metadata.create_all(self.engine)

    def add_prompt(self, body):
        with Session(self.engine) as session:
            prompt = Prompt(body=body)
            session.add(prompt)
            session.commit()
            session.refresh(prompt)
            return prompt.id

    def update_prompt(self, pid, body):
        with Session(self.engine) as session:
            prompt = session.get(Prompt, pid)
            if prompt:
                prompt.body = body
                prompt.updated_at = datetime.now(timezone.utc).isoformat()
                session.commit()

    def increment_usage(self, pid):
        with Session(self.engine) as session:
            prompt = session.get(Prompt, pid)
            if prompt:
                prompt.usage_count += 1
                session.commit()

    def delete_prompt(self, pid):
        with Session(self.engine) as session:
            prompt = session.get(Prompt, pid)
            if prompt:
                session.delete(prompt)
                session.commit()

    def get_all_prompts(self):
        with Session(self.engine) as session:
            return session.exec(
                select(Prompt).order_by(-Prompt.usage_count, Prompt.created_at)
            ).all()

    def search_prompts(self, q, limit=50):
        words = q.strip().split()
        if not words:
            return []
        with Session(self.engine) as session:
            query = select(Prompt)
            for word in words:
                query = query.where(Prompt.body.contains(word))
            return session.exec(query.order_by(-Prompt.usage_count).limit(limit)).all()

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
