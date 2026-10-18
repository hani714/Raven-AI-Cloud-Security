import json
import logging
from typing import List, Optional, Dict, Any

from .base import BaseLambdaEnumerator
from .models import LambdaLayer

logger = logging.getLogger(__name__)


class LayerEnumerator(BaseLambdaEnumerator):
    async def list_all_layers(self) -> List[str]:
        """Get list of all Lambda layer names"""
        try:
            async with self.aiosession.client('lambda') as lambda_client:
                layers = await self._paginate_results(
                    lambda_client,
                    'list_layers',
                    'Layers',
                    'list_layers'
                )
            return [layer['LayerName'] for layer in layers]
        except Exception as e:
            self._handle_error("list_layers", e)
            return []
    
    async def list_layer_versions(self, layer_name: str) -> List[Dict[str, Any]]:
        """List versions for a specific layer"""
        async with self.aiosession.client('lambda') as lambda_client:
            return await self._paginate_results(
                lambda_client,
                'list_layer_versions',
                'LayerVersions',
                'list_layer_versions',
                LayerName=layer_name
            )
    
    async def get_layer_version(self, layer_name: str, version_number: int) -> Dict[str, Any]:
        """Get specific layer version details"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_layer_version",
                lambda_client,
                "get_layer_version",
                f"{layer_name}:{version_number}",
                LayerName=layer_name,
                VersionNumber=version_number
            )
        return response or {}
    
    async def get_layer_version_policy(self, layer_name: str, version_number: int) -> Dict[str, Any]:
        """Get layer version resource policy"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_layer_version_policy",
                lambda_client,
                "get_layer_version_policy",
                f"{layer_name}:{version_number}",
                LayerName=layer_name,
                VersionNumber=version_number
            )
        
        if response and 'Policy' in response:
            try:
                return json.loads(response['Policy'])
            except json.JSONDecodeError:
                return {"raw_policy": response['Policy']}
        return {}
    
    async def enumerate_layer(self, scan_id: str, layer_name: str, get_all_versions: bool = False,
                              max_versions: int = 5) -> Optional[LambdaLayer]:
        try:
            # Get layer versions
            versions = await self.list_layer_versions(layer_name)
            
            if not versions:
                logger.warning(f"No versions found for layer {layer_name}")
                return None
            
            # Sort versions by version number (descending to get latest first)
            versions.sort(key=lambda x: x.get('Version', 0), reverse=True)
            
            # Get details for the latest version
            latest_version = versions[0]
            version_number = latest_version.get('Version')
            
            if not version_number:
                logger.warning(f"Could not determine version number for layer {layer_name}")
                return None
            
            # Get detailed version information
            version_details = await self.get_layer_version(layer_name, version_number)
            
            if not version_details:
                logger.warning(f"Could not get details for layer {layer_name}:{version_number}")
                return None
            
            # Get layer version policy
            try:
                policy = await self.get_layer_version_policy(layer_name, version_number)
            except Exception as e:
                logger.debug(f"Could not get policy for layer {layer_name}:{version_number}: {str(e)}")
                policy = {}
            
            # Create LambdaLayer object
            lambda_layer = LambdaLayer(
                scan_id=scan_id,
                layer_name=layer_name,
                layer_arn=version_details.get('LayerArn', ''),
                version=version_details.get('Version'),
                description=version_details.get('Description'),
                created_date=version_details.get('CreatedDate'),
                content=version_details.get('Content', {}),
                compatible_runtimes=version_details.get('CompatibleRuntimes', []),
                compatible_architectures=version_details.get('CompatibleArchitectures', []),
                license_info=version_details.get('LicenseInfo'),
                policy=policy
            )
            
            return lambda_layer
            
        except Exception as e:
            self._handle_error("enumerate_layer", e, layer_name)
            return None
    
    async def enumerate_all_layers(self, scan_id: str, get_all_versions: bool = False,
                                   max_versions_per_layer: int = 5) -> List[LambdaLayer]:
        layers = []
        layer_names = await self.list_all_layers()
        
        logger.info(f"Found {len(layer_names)} Lambda layers to enumerate")
        
        for layer_name in layer_names:
            try:
                layer = await self.enumerate_layer(scan_id, layer_name, get_all_versions, max_versions_per_layer)
                if layer:
                    layers.append(layer)
                    logger.debug(f"Successfully enumerated layer: {layer_name}")
                else:
                    logger.warning(f"Failed to enumerate layer: {layer_name}")
                    
            except Exception as e:
                logger.error(f"Error enumerating layer {layer_name}: {str(e)}")
                continue
        
        logger.info(f"Successfully enumerated {len(layers)} Lambda layers")
        return layers
    
    async def enumerate_all_layer_versions(self, scan_id: str, layer_name: str,
                                           max_versions: int = 10) -> List[LambdaLayer]:
        layer_versions = []
        
        try:
            # Get all versions
            versions = await self.list_layer_versions(layer_name)
            
            if not versions:
                logger.warning(f"No versions found for layer {layer_name}")
                return []
            
            # Sort versions by version number (descending)
            versions.sort(key=lambda x: x.get('Version', 0), reverse=True)
            
            # Limit versions if specified
            if max_versions > 0:
                versions = versions[:max_versions]
            
            for version_info in versions:
                version_number = version_info.get('Version')
                
                if not version_number:
                    continue
                
                try:
                    # Get detailed version information
                    version_details = await self.get_layer_version(layer_name, version_number)
                    
                    if not version_details:
                        continue
                    
                    # Get layer version policy
                    try:
                        policy = await self.get_layer_version_policy(layer_name, version_number)
                    except Exception:
                        policy = {}
                    
                    # Create LambdaLayer object for this version
                    lambda_layer = LambdaLayer(
                        scan_id=scan_id,
                        layer_name=layer_name,
                        layer_arn=version_details.get('LayerArn', ''),
                        version=version_details.get('Version'),
                        description=version_details.get('Description'),
                        created_date=version_details.get('CreatedDate'),
                        content=version_details.get('Content', {}),
                        compatible_runtimes=version_details.get('CompatibleRuntimes', []),
                        compatible_architectures=version_details.get('CompatibleArchitectures', []),
                        license_info=version_details.get('LicenseInfo'),
                        policy=policy
                    )
                    
                    layer_versions.append(lambda_layer)
                    
                except Exception as e:
                    logger.warning(f"Could not get details for layer {layer_name}:{version_number}: {str(e)}")
                    continue
            
            logger.info(f"Successfully enumerated {len(layer_versions)} versions for layer {layer_name}")
            
        except Exception as e:
            self._handle_error("enumerate_all_layer_versions", e, layer_name)
        
        return layer_versions
    
    async def get_layer_basic_info(self, layer_name: str) -> Optional[Dict[str, Any]]:
        try:
            versions = await self.list_layer_versions(layer_name)
            
            if not versions:
                return None
            
            # Return info for the latest version
            latest_version = max(versions, key=lambda x: x.get('Version', 0))
            return latest_version
            
        except Exception as e:
            logger.warning(f"Could not get basic info for layer {layer_name}: {str(e)}")
            return None
    
    async def find_layers_by_runtime(self, scan_id: str, runtime: str) -> List[str]:
        compatible_layers = []
        
        try:
            layer_names = await self.list_all_layers()
            
            for layer_name in layer_names:
                try:
                    layer = await self.enumerate_layer(scan_id, layer_name)
                    if layer and runtime in layer.compatible_runtimes:
                        compatible_layers.append(layer_name)
                        
                except Exception as e:
                    logger.debug(f"Could not check compatibility for layer {layer_name}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(compatible_layers)} layers compatible with runtime {runtime}")
            
        except Exception as e:
            logger.error(f"Error finding layers by runtime {runtime}: {str(e)}")
        
        return compatible_layers