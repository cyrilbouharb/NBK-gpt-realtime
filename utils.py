"""
Utility functions for Azure operations and deployment management.
"""
import json
import subprocess
import sys
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass
class CommandResult:
    """Result from running a command."""
    success: bool
    output: str
    json_data: Optional[Dict[str, Any]] = None
    exit_code: int = 0


class AzureUtils:
    """Utilities for interacting with Azure."""
    
    @staticmethod
    def run_command(
        command: str,
        success_message: Optional[str] = None,
        error_message: Optional[str] = None,
        parse_json: bool = True,
        show_spinner: bool = True
    ) -> CommandResult:
        """
        Run a command and return the result.
        
        Args:
            command: Command to execute
            success_message: Message to display on success
            error_message: Message to display on error
            parse_json: Whether to parse output as JSON
            show_spinner: Whether to show a spinner during execution
        """
        try:
            if show_spinner:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                    transient=True
                ) as progress:
                    task = progress.add_task("Executing command...", total=None)
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True
                )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            json_data = None
            if parse_json and success and output.strip():
                try:
                    json_data = json.loads(output)
                except json.JSONDecodeError:
                    pass
            
            if success and success_message:
                console.print(f"✅ {success_message}", style="green")
            elif not success and error_message:
                console.print(f"❌ {error_message}", style="red")
                if output:
                    console.print(f"Error details: {output}", style="red dim")
            
            return CommandResult(
                success=success,
                output=output,
                json_data=json_data,
                exit_code=result.returncode
            )
            
        except Exception as e:
            console.print(f"❌ Exception while running command: {str(e)}", style="red")
            return CommandResult(
                success=False,
                output=str(e),
                exit_code=-1
            )
    
    @staticmethod
    def get_azure_account_info() -> Optional[Dict[str, str]]:
        """Get current Azure account information."""
        result = AzureUtils.run_command(
            "az account show",
            success_message="Retrieved Azure account information",
            error_message="Failed to get Azure account"
        )
        
        if result.success and result.json_data:
            return {
                "user": result.json_data.get("user", {}).get("name"),
                "tenant_id": result.json_data.get("tenantId"),
                "subscription_id": result.json_data.get("id"),
                "subscription_name": result.json_data.get("name")
            }
        return None
    
    @staticmethod
    def create_resource_group(name: str, location: str) -> bool:
        """Create an Azure resource group if it doesn't exist."""
        # Check if it exists
        check_result = AzureUtils.run_command(
            f"az group show --name {name}",
            parse_json=True,
            show_spinner=False
        )
        
        if check_result.success:
            console.print(f"ℹ️  Resource group '{name}' already exists", style="blue")
            return True
        
        # Create it
        result = AzureUtils.run_command(
            f"az group create --name {name} --location {location}",
            success_message=f"Created resource group '{name}' in {location}",
            error_message=f"Failed to create resource group '{name}'"
        )
        return result.success
    
    @staticmethod
    def deploy_bicep(
        deployment_name: str,
        resource_group: str,
        template_file: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Deploy a Bicep template to Azure.
        
        Args:
            deployment_name: Name of the deployment
            resource_group: Resource group name
            template_file: Path to the Bicep template
            parameters: Parameters for the deployment
        """
        # Create parameters file
        params_file = "params.json"
        bicep_parameters = {
            "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {
                key: {"value": value} for key, value in parameters.items()
            }
        }
        
        with open(params_file, 'w') as f:
            json.dump(bicep_parameters, f, indent=2)
        
        console.print(f"\n🚀 Starting deployment '{deployment_name}'...", style="bold blue")
        
        # Run deployment
        result = AzureUtils.run_command(
            f"az deployment group create --name {deployment_name} "
            f"--resource-group {resource_group} "
            f"--template-file {template_file} "
            f"--parameters {params_file}",
            success_message=f"Deployment '{deployment_name}' succeeded",
            error_message=f"Deployment '{deployment_name}' failed"
        )
        
        return result.success
    
    @staticmethod
    def get_deployment_outputs(deployment_name: str, resource_group: str) -> Optional[Dict[str, Any]]:
        """Get outputs from a deployment."""
        result = AzureUtils.run_command(
            f"az deployment group show --name {deployment_name} -g {resource_group}",
            parse_json=True,
            show_spinner=False
        )
        
        if result.success and result.json_data:
            outputs = result.json_data.get("properties", {}).get("outputs", {})
            return {key: value.get("value") for key, value in outputs.items()}
        
        return None
    
    @staticmethod
    def get_deployment_output(outputs: Dict[str, Any], key: str, description: Optional[str] = None) -> Any:
        """Get a specific output from deployment outputs."""
        value = outputs.get(key)
        if description and value:
            console.print(f"  {description}: {value}", style="cyan")
        return value


class BingGroundingUtils:
    """Utilities for Bing custom grounding."""
    
    @staticmethod
    def search_bing(
        query: str,
        api_key: str,
        site_filter: Optional[str] = None,
        freshness: str = "Month",
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Bing with optional site filtering.
        
        Args:
            query: Search query
            api_key: Bing API key
            site_filter: Optional site filter (e.g., 'site:nbk.com')
            freshness: Freshness filter (Day, Week, Month)
            count: Number of results to return
        """
        import requests
        
        search_query = f"{query} {site_filter}" if site_filter else query
        
        headers = {
            "Ocp-Apim-Subscription-Key": api_key
        }
        
        params = {
            "q": search_query,
            "count": count,
            "freshness": freshness,
            "textDecorations": True,
            "textFormat": "HTML"
        }
        
        try:
            response = requests.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            web_pages = data.get("webPages", {}).get("value", [])
            
            results = []
            for page in web_pages:
                results.append({
                    "title": page.get("name", ""),
                    "url": page.get("url", ""),
                    "snippet": page.get("snippet", ""),
                    "date_published": page.get("datePublished", "")
                })
            
            return results
            
        except Exception as e:
            console.print(f"❌ Error searching Bing: {str(e)}", style="red")
            return []
    
    @staticmethod
    def format_grounding_context(search_results: List[Dict[str, Any]]) -> str:
        """Format search results as grounding context for the model."""
        if not search_results:
            return "No relevant information found from NBK sources."
        
        context_parts = ["Here is relevant information from NBK sources:\n"]
        
        for idx, result in enumerate(search_results, 1):
            context_parts.append(f"\n{idx}. {result['title']}")
            context_parts.append(f"   Source: {result['url']}")
            context_parts.append(f"   {result['snippet']}\n")
        
        return "\n".join(context_parts)


def print_header(title: str):
    """Print a styled header."""
    console.print(Panel(title, style="bold magenta", expand=False))


def print_info(message: str):
    """Print an info message."""
    console.print(f"ℹ️  {message}", style="blue")


def print_success(message: str):
    """Print a success message."""
    console.print(f"✅ {message}", style="green")


def print_error(message: str):
    """Print an error message."""
    console.print(f"❌ {message}", style="red")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"⚠️  {message}", style="yellow")
