from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Numeric
from sqlalchemy.orm import declarative_base
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class CarbonEmissionRecord(Base):
    __tablename__ = 'carbon_emission_records'

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String, unique=True, index=True)
    entity_id = Column(String, index=True)
    emission_scope = Column(String, index=True)  # scope_1, scope_2, scope_3
    activity_type = Column(String, index=True)
    activity_data = Column(JSON)
    emission_amount = Column(Numeric(precision=15, scale=6))  # tons CO2e
    emission_unit = Column(String, default='metric_tons_co2e')
    emission_factor = Column(Float)
    calculation_method = Column(String)
    data_quality = Column(String, default='medium')  # low, medium, high
    verification_status = Column(String, default='unverified')
    verification_date = Column(DateTime, nullable=True)
    emission_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class CarbonOffset(Base):
    __tablename__ = 'carbon_offsets'
    
    id = Column(Integer, primary_key=True, index=True)
    offset_id = Column(String, unique=True, index=True)
    project_id = Column(String, index=True)
    project_name = Column(String)
    offset_type = Column(String)  # forestry, renewable_energy, methane_capture, etc.
    amount_tons = Column(Numeric(precision=15, scale=6))
    vintage_year = Column(Integer, index=True)
    verification_standard = Column(String)  # VCS, Gold Standard, etc.
    project_location = Column(JSON)  # {country, region, coordinates}
    price_per_ton = Column(Numeric(precision=10, scale=2))
    purchase_date = Column(DateTime)
    retirement_date = Column(DateTime, nullable=True)
    retirement_reason = Column(String, nullable=True)
    additionality_verified = Column(Boolean, default=True)
    permanence_rating = Column(String, default='high')
    co_benefits = Column(JSON)  # biodiversity, community, etc.
    registry_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BiodiversityMeasurement(Base):
    __tablename__ = 'biodiversity_measurements'
    
    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(String, unique=True, index=True)
    location = Column(JSON)  # {latitude, longitude, region}
    ecosystem_type = Column(String, index=True)
    measurement_method = Column(String)
    area_hectares = Column(Float)
    species_data = Column(JSON)  # {species_name: count}
    biodiversity_metrics = Column(JSON)  # shannon_diversity, simpson_index, etc.
    measurement_date = Column(DateTime)
    data_quality = Column(String, default='medium')
    verification_status = Column(String, default='unverified')
    observer_id = Column(String, nullable=True)
    weather_conditions = Column(JSON, nullable=True)
    habitat_conditions = Column(JSON, nullable=True)
    threats_identified = Column(JSON, nullable=True)
    conservation_status = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConservationProject(Base):
    __tablename__ = 'conservation_projects'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True)
    project_name = Column(String)
    project_type = Column(String)  # habitat_restoration, species_protection, etc.
    location = Column(JSON)
    target_ecosystem = Column(String)
    target_species = Column(JSON)
    area_hectares = Column(Float)
    funding_required = Column(Numeric(precision=15, scale=2))
    funding_secured = Column(Numeric(precision=15, scale=2), default=0)
    expected_impact = Column(JSON)
    timeline_years = Column(Integer)
    project_status = Column(String, default='planning')  # planning, active, completed
    progress_metrics = Column(JSON, nullable=True)
    partners = Column(JSON)
    monitoring_schedule = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=True)
    completion_date = Column(DateTime, nullable=True)
