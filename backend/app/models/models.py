from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    learning_progress = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    conversations = relationship("Conversation", back_populates="user")
    graphs = relationship("Graph", back_populates="user")
    algo_sessions = relationship("AlgoSession", back_populates="user")

class Graph(Base):
    __tablename__ = 'graphs'
    graph_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    name = Column(String)
    data_json = Column(JSON)
    is_template = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="graphs")
    algo_sessions = relationship("AlgoSession", back_populates="graph")
    execution_states = relationship("ExecutionState", back_populates="graph")

class AlgoSession(Base):
    __tablename__ = 'algo_sessions'
    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    graph_id = Column(Integer, ForeignKey('graphs.graph_id'), nullable=False, index=True)
    algo_name = Column(String, nullable=False, default="Dijkstra")
    start_node = Column(String, nullable=False)
    total_steps = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="algo_sessions")
    graph = relationship("Graph", back_populates="algo_sessions")
    execution_states = relationship("ExecutionState", back_populates="algo_session", cascade="all, delete-orphan")

class ExecutionState(Base):
    __tablename__ = 'execution_states'
    state_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('algo_sessions.session_id'), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    graph_id = Column(Integer, ForeignKey('graphs.graph_id'))
    step_data_json = Column(JSON, nullable=False) 
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('session_id', 'step_index', name='uq_session_step'),
    )

    graph = relationship("Graph", back_populates="execution_states")
    algo_session = relationship("AlgoSession", back_populates="execution_states")
    conversations = relationship("Conversation", back_populates="execution_state")

class AiExplanation(Base):
    __tablename__ = 'ai_explanations'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey('algo_sessions.session_id'), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)
    explanation_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('session_id', 'step_index', name='uq_explanation_step'),
    )

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    state_id = Column(Integer, ForeignKey('execution_states.state_id'))
    convo_id = Column(String, unique=True)
    vector_id_ref = Column(String)
    
    user = relationship("User", back_populates="conversations")
    execution_state = relationship("ExecutionState", back_populates="conversations")