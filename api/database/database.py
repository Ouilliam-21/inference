import psycopg2
import os
from database.models import ProcessingRiotEventJob, RiotEvent
from datetime import datetime

class Database:
    def __init__(self):

        print("🐟 Initializing Database")
        host, port, user, password, database = self._load_env()

        self.conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        self.cursor = self.conn.cursor()

        print("🐟 Database initialized")

    def _load_env(self):
        host = os.getenv("DIGITAL_OCEAN_DATABASE_HOST")
        port = os.getenv("DIGITAL_OCEAN_DATABASE_PORT")
        user = os.getenv("DIGITAL_OCEAN_DATABASE_USER")
        password = os.getenv("DIGITAL_OCEAN_DATABASE_PASSWORD")
        database = os.getenv("DIGITAL_OCEAN_DATABASE_NAME")

        if not host:
            raise ValueError("DIGITAL_OCEAN_DATABASE_HOST is not set")
        if not port:
            raise ValueError("DIGITAL_OCEAN_DATABASE_PORT is not set")
        if not user:
            raise ValueError("DIGITAL_OCEAN_DATABASE_USER is not set")
        if not password:
            raise ValueError("DIGITAL_OCEAN_DATABASE_PASSWORD is not set")
        if not database:
            raise ValueError("DIGITAL_OCEAN_DATABASE_NAME is not set")

        return host, port, user, password, database

    def get_riot_event_by_id(self, riot_event_id: str) -> RiotEvent:
        self.cursor.execute(
            "SELECT * FROM riot_events WHERE id = %s",
            (riot_event_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return RiotEvent(
                id=result[0],
                gameSessionId=result[1],
                riotEventId=result[2],
                eventName=result[3],
                eventData=result[4],
                createdAt=result[5]
            )

    def save_processing_riot_event_job(self, processing_riot_event_job: ProcessingRiotEventJob):
        
        processing_riot_event_job.updated_at = datetime.now()

        self.cursor.execute(
            "INSERT INTO processing_riot_events_jobs (id, riot_event_id, status, input_text, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (processing_riot_event_job.id, processing_riot_event_job.riot_event_id, processing_riot_event_job.status.value, processing_riot_event_job.input_text, processing_riot_event_job.created_at, processing_riot_event_job.updated_at)
        )
        self.conn.commit()

        return processing_riot_event_job


    def update_processing_riot_events_job(self, processing_riot_event_job: ProcessingRiotEventJob):
        
        processing_riot_event_job.updated_at = datetime.now()
        
        self.cursor.execute(
            """
                UPDATE processing_riot_events_jobs SET riot_event_id = %s,
                status = %s, input_text = %s, llm_started_at = %s, llm_completed_at = %s,
                llm_model_name = %s, llm_text = %s, error_message = %s, tts_started_at = %s,
                tts_completed_at = %s, tts_model_name = %s, audio_url = %s,
                audio_duration = %s, updated_at = %s
                WHERE id = %s;
            """,
            (
                processing_riot_event_job.riot_event_id,
                processing_riot_event_job.status.value,
                processing_riot_event_job.input_text,
                processing_riot_event_job.llm_started_at,
                processing_riot_event_job.llm_completed_at,
                processing_riot_event_job.llm_model_name,
                processing_riot_event_job.llm_text,
                processing_riot_event_job.error_message,
                processing_riot_event_job.tts_started_at,
                processing_riot_event_job.tts_completed_at,
                processing_riot_event_job.tts_model_name,
                processing_riot_event_job.audio_url,
                processing_riot_event_job.audio_duration,
                processing_riot_event_job.updated_at,
                processing_riot_event_job.id
            )
        )
        self.conn.commit()

        return processing_riot_event_job