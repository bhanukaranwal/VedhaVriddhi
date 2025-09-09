from pydantic import BaseSettings
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "climate-intelligence-service"
    service_version: str = "4.0.0"
    service_port: int = 8204
    debug: bool = False
    
    # Carbon Accounting Configuration
    carbon_negativity_target: float = -0.1  # 10% carbon negative target
    automatic_offset_purchasing: bool = True
    offset_buffer_percentage: float = 0.2  # 20% buffer for offsets
    verification_threshold_tons: float = 10.0  # Verify emissions > 10 tons
    
    # Supported Carbon Standards
    accepted_offset_standards: List[str] = [
        "VCS", "Gold Standard", "Climate Action Reserve", 
        "American Carbon Registry", "Plan Vivo"
    ]
    
    # Biodiversity Tracking
    biodiversity_monitoring_enabled: bool = True
    minimum_data_quality_threshold: str = "medium"
    endangered_species_alerts: bool = True
    habitat_connectivity_analysis: bool = True
    
    # Climate Risk Analysis
    climate_scenario_models: List[str] = [
        "RCP2.6", "RCP4.5", "RCP6.0", "RCP8.5"
    ]
    physical_risk_assessment: bool = True
    transition_risk_assessment: bool = True
    climate_var_analysis: bool = True
    
    # Renewable Energy Optimization
    renewable_project_screening: bool = True
    energy_storage_optimization: bool = True
    grid_integration_analysis: bool = True
    
    # Real-time Monitoring
    emission_monitoring_frequency: int = 60  # seconds
    offset_purchasing_frequency: int = 3600  # seconds
    biodiversity_check_frequency: int = 86400  # daily
    
    # Data Sources
    emission_factor_database: str = "EPA_eGRID"
    biodiversity_data_sources: List[str] = [
        "GBIF", "iNaturalist", "eBird", "IUCN_RedList"
    ]
    climate_data_providers: List[str] = [
        "NOAA", "NASA_GISS", "Copernicus", "Berkeley_Earth"
    ]
    
    # Marketplace Integration
    carbon_offset_marketplaces: List[str] = [
        "Verra", "Gold_Standard_Registry", "Climate_Action_Reserve"
    ]
    biodiversity_credit_platforms: List[str] = [
        "Natural_Capital_Exchange", "Biodiversity_Credit_Alliance"
    ]
    
    # Financial Integration
    climate_risk_integration: bool = True
    esg_scoring_enabled: bool = True
    nature_positive_screening: bool = True
    
    # Database Configuration
    climate_db_url: str = "postgresql://vedhavriddhi:vedhavriddhi123@localhost:5432/vedhavriddhi_climate"
    redis_url: str = "redis://localhost:6379/14"
    
    # External Services
    weather_api_key: str = ""
    satellite_imagery_api_key: str = ""
    carbon_offset_api_key: str = ""
    
    # Alerts and Notifications
    carbon_positive_alerts: bool = True
    biodiversity_risk_alerts: bool = True
    climate_risk_threshold: float = 0.7  # 70% risk threshold
    
    # Reporting
    sustainability_reporting_enabled: bool = True
    tcfd_reporting: bool = True  # Task Force on Climate-related Financial Disclosures
    sbtn_alignment: bool = True  # Science Based Targets Network
    
    class Config:
        env_file = ".env"
        case_sensitive = False
