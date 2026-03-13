from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from database import Base


class TrainerProfile(Base):
    __tablename__ = "trainer_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    certification = Column(String(255))
    experience_years = Column(Integer)
    bio = Column(Text)

    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    gender = Column(String(10))

    phone = Column(String(30))
    location = Column(String(150))

    profile_photo = Column(String(255))

    profile_completed = Column(Boolean, default=False)

    user = relationship("User")

    # 🔥 relación con especialidades
    specialties = relationship(
        "TrainerProfileSpecialty",
        back_populates="trainer"
    )

class TrainerSpecialty(Base):
    __tablename__ = "trainer_specialties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    trainers = relationship(
        "TrainerProfileSpecialty",
        back_populates="specialty"
    )

class TrainerProfileSpecialty(Base):
    __tablename__ = "trainer_profile_specialties"

    id = Column(Integer, primary_key=True, index=True)

    trainer_id = Column(Integer, ForeignKey("trainer_profiles.id"))
    specialty_id = Column(Integer, ForeignKey("trainer_specialties.id"))

    trainer = relationship(
        "TrainerProfile",
        back_populates="specialties"
    )

    specialty = relationship(
        "TrainerSpecialty",
        back_populates="trainers"
    )