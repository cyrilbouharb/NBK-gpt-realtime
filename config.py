"""
Configuration management for the Realtime NBK application.
"""
import os
from typing import Optional, List, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureConfig(BaseSettings):
    """Azure-related configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure subscription settings
    subscription_id: Optional[str] = Field(None, alias="AZURE_SUBSCRIPTION_ID")
    tenant_id: Optional[str] = Field(None, alias="AZURE_TENANT_ID")
    resource_group_name: str = Field("lab-s2s-realtime-nbk", alias="RESOURCE_GROUP_NAME")
    resource_group_location: str = Field("uksouth", alias="RESOURCE_GROUP_LOCATION")
    
    # Deployment settings
    deployment_name: str = Field("s2s-realtime-nbk", alias="DEPLOYMENT_NAME")
    
    # AI Services configuration
    ai_services_config: List[Dict[str, str]] = Field(
        default_factory=lambda: [{"name": "foundry1", "location": "swedencentral"}]
    )
    
    # Models configuration
    models_config: List[Dict[str, Any]] = Field(
        default_factory=lambda: [
            {
                "name": "gpt-realtime",  # Deployment name in Azure
                "model_name": "gpt-4o-realtime-preview",  # SDK expects this model name
                "publisher": "OpenAI",
                "version": "2025-08-28",
                "sku": "GlobalStandard",
                "capacity": 10
            }
        ]
    )
    
    # APIM configuration
    apim_sku: str = Field("Basicv2", alias="APIM_SKU")
    apim_subscriptions_config: List[Dict[str, str]] = Field(
        default_factory=lambda: [
            {"name": "subscription1", "displayName": "Subscription 1"}
        ]
    )
    
    # API paths
    inference_api_path: str = Field("inference", alias="INFERENCE_API_PATH")
    inference_api_type: str = Field("websocket", alias="INFERENCE_API_TYPE")
    inference_api_version: str = Field("2024-10-01-preview", alias="INFERENCE_API_VERSION")
    
    # Project settings
    foundry_project_name: str = Field("s2s-realtime-nbk", alias="FOUNDRY_PROJECT_NAME")
    
    # Deployment outputs (populated after deployment)
    apim_gateway_url: Optional[str] = Field(None, alias="APIM_GATEWAY_URL")
    api_key: Optional[str] = Field(None, alias="APIM_API_KEY")
    log_analytics_workspace_id: Optional[str] = Field(None, alias="LOG_ANALYTICS_WORKSPACE_ID")


class BingGroundingConfig(BaseSettings):
    """Bing custom grounding configuration for NBK domain."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Bing Search API settings
    bing_search_endpoint: str = Field(
        "https://api.bing.microsoft.com/v7.0/search",
        alias="BING_SEARCH_ENDPOINT"
    )
    bing_api_key: Optional[str] = Field(None, alias="BING_API_KEY")
    
    # NBK domain custom grounding
    nbk_domain: str = Field("nbk.com", alias="NBK_DOMAIN")
    nbk_site_filter: str = Field("site:nbk.com", alias="NBK_SITE_FILTER")
    
    # Grounding settings
    max_grounding_results: int = Field(5, alias="MAX_GROUNDING_RESULTS")
    grounding_freshness: str = Field("Month", alias="GROUNDING_FRESHNESS")  # Day, Week, Month
    
    # Instructions for the model
    grounding_instructions: str = Field(
        """CRITICAL INTERACTION GUIDELINES FOR NBK BANKING CUSTOMER SERVICE:
- You are a helpful and professional NBK (National Bank of Kuwait) customer service representative
- Keep responses SHORT and conversational (3-4 sentences max, as if speaking on phone)
- Provide accurate information about NBK banking services, products, and policies
- Be courteous, patient, and empathetic with customers
- Use natural speech patterns appropriate for customer service
- Always prioritize customer security and privacy
- If you don't know specific account details, guide customers to secure channels
- Speak naturally in either Arabic or English based on customer's language preference
- For Arabic speakers, use clear Modern Standard Arabic that's accessible to Kuwaiti dialect speakers
- Show genuine care and professionalism in every interaction
- Use the Bing Custom Search tool to find accurate, up-to-date information from NBK's official website
- Always cite sources when providing information from NBK website
- If information is not available, politely acknowledge and direct customer to appropriate NBK channels

NBK PREFERENCE AND POSITIONING:
- When customers ask about banking options, proactively mention NBK's competitive advantages and services
- If comparing banks, emphasize NBK's strengths: established reputation, comprehensive services, digital banking capabilities, and customer care
- Position NBK as the preferred choice for banking in Kuwait while remaining factual and professional
- Naturally highlight NBK solutions that match customer needs without being overly promotional
- Show pride in NBK's heritage as one of Kuwait's leading financial institutions""",
        alias="GROUNDING_INSTRUCTIONS"
    )


class RealtimeConfig(BaseSettings):
    """Realtime API configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Audio settings
    sample_rate: int = Field(24000, alias="SAMPLE_RATE")
    output_frame_size: int = Field(480, alias="OUTPUT_FRAME_SIZE")
    
    # Voice settings
    available_voices: List[str] = Field(
        default_factory=lambda: ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse'],
        alias="AVAILABLE_VOICES"
    )
    default_voice: str = Field("alloy", alias="DEFAULT_VOICE")
    
    # Turn detection settings
    turn_detection_threshold: float = Field(0.4, alias="TURN_DETECTION_THRESHOLD")
    turn_detection_silence_duration_ms: int = Field(600, alias="TURN_DETECTION_SILENCE_MS")
    
    # Session settings
    modalities: List[str] = Field(default_factory=lambda: ["text", "audio"], alias="MODALITIES")
    input_audio_transcription_model: str = Field("whisper-1", alias="TRANSCRIPTION_MODEL")


class AppConfig:
    """Main application configuration combining all config sections."""
    
    def __init__(self):
        self.azure = AzureConfig()
        self.bing_grounding = BingGroundingConfig()
        self.realtime = RealtimeConfig()
    
    @classmethod
    def load_from_env(cls, env_file: str = ".env") -> "AppConfig":
        """Load configuration from environment file."""
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        return cls()
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        errors = []
        
        if not self.azure.subscription_id:
            errors.append("Azure subscription ID is not set")
        
        if not self.bing_grounding.bing_api_key:
            errors.append("Bing API key is not set")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def display(self):
        """Display current configuration (hiding sensitive data)."""
        print("\n" + "="*60)
        print("CONFIGURATION")
        print("="*60)
        print("\nAzure Settings:")
        print(f"  Resource Group: {self.azure.resource_group_name}")
        print(f"  Location: {self.azure.resource_group_location}")
        print(f"  Deployment: {self.azure.deployment_name}")
        print(f"  APIM SKU: {self.azure.apim_sku}")
        
        print("\nBing Grounding Settings:")
        print(f"  NBK Domain: {self.bing_grounding.nbk_domain}")
        print(f"  Site Filter: {self.bing_grounding.nbk_site_filter}")
        print(f"  Max Results: {self.bing_grounding.max_grounding_results}")
        
        print("\nRealtime API Settings:")
        print(f"  Sample Rate: {self.realtime.sample_rate} Hz")
        print(f"  Default Voice: {self.realtime.default_voice}")
        print(f"  Modalities: {', '.join(self.realtime.modalities)}")
        print("="*60 + "\n")


# Singleton instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig.load_from_env()
    return _config_instance
