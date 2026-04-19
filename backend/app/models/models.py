from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    learning_progress = Column(JSON, nullable=True)
    conversations = relationship("Conversation", back_populates="user")

class Graph(Base):
    __tablename__ = 'graphs'
    graph_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    data_json = Column(JSON) # Lưu {nodes: [], edges: []}
    is_template = Column(Boolean, default=False)
    execution_states = relationship("ExecutionState", back_populates="graph")

class AlgorithmStep(Base):
    __tablename__ = 'algorithm_steps'
    algo_step_id = Column(Integer, primary_key=True, index=True)
    algo_name = Column(String)
    step_order = Column(Integer)
    pseudo_code = Column(Text)
    execution_states = relationship("ExecutionState", back_populates="algo_step")

class ExecutionState(Base):
    __tablename__ = 'execution_states'
    state_id = Column(Integer, primary_key=True, index=True)
    graph_id = Column(Integer, ForeignKey('graphs.graph_id'))
    algo_step_id = Column(Integer, ForeignKey('algorithm_steps.algo_step_id'))
    step_data_json = Column(JSON) # SNAPSHOT: lưu dist[], visited[]...
    explanation = Column(Text)
    
    graph = relationship("Graph", back_populates="execution_states")
    algo_step = relationship("AlgorithmStep", back_populates="execution_states")
    conversations = relationship("Conversation", back_populates="execution_state")

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    state_id = Column(Integer, ForeignKey('execution_states.state_id'))
    convo_id = Column(String, unique=True)
    vector_id_ref = Column(String)
    
    user = relationship("User", back_populates="conversations")
    execution_state = relationship("ExecutionState", back_populates="conversations")