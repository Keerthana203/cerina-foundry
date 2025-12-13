from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class ProtocolRequest(Base):
    __tablename__ = "protocol_requests"

    id = Column(Integer, primary_key=True)
    user_intent = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending | running | halted | approved | completed
    created_at = Column(DateTime, default=datetime.utcnow)

    blackboard_states = relationship(
        "BlackboardState", back_populates="request", cascade="all, delete-orphan"
    )
    events = relationship(
        "EventLog", back_populates="request", cascade="all, delete-orphan"
    )


class BlackboardState(Base):
    __tablename__ = "blackboard_states"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("protocol_requests.id"), nullable=False)

    version = Column(Integer, nullable=False)
    draft_text = Column(Text, default="")
    state_metadata = Column(JSON, default=dict)
    safety_score = Column(Float, default=0.0)
    empathy_score = Column(Float, default=0.0)
    iteration = Column(Integer, default=0)
    notes = Column(JSON, default=list)

    finalized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ProtocolRequest", back_populates="blackboard_states")



class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("protocol_requests.id"), nullable=False)

    event_type = Column(String, nullable=False)
    payload = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("ProtocolRequest", back_populates="events")
