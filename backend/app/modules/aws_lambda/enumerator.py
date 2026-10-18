"""
Lambda Enumerator
Main enumerator that orchestrates Lambda function and layer enumeration
"""

import asyncio
import logging
from datetime import datetime
from typing import List

from .base import BaseLambdaEnumerator
from .exceptions import LambdaEnumerationError
from .functions import FunctionEnumerator
from .layers import LayerEnumerator
from .models import LambdaEnumerationResult, LambdaFunction, LambdaLayer


logger = logging.getLogger(__name__)


class LambdaEnumerator(BaseLambdaEnumerator):
    """Main Lambda enumerator that orchestrates comprehensive enumeration."""

    def __init__(self, session=None, max_workers: int = 5):
        super().__init__(session)
        self.max_workers = max_workers
        self.function_enumerator = FunctionEnumerator(session)
        self.layer_enumerator = LayerEnumerator(session)
        logger.info(f"Initialized Lambda enumerator with {max_workers} workers")

    async def enumerate_functions_only(
        self,
        scan_id: str,
        get_detailed_config: bool = True,
        concurrent: bool = True,
    ) -> List[LambdaFunction]:
        function_names = await self.function_enumerator.list_all_functions()
        if not function_names:
            logger.info("No Lambda functions found")
            return []

        logger.info(f"Starting {'concurrent' if concurrent else 'sequential'} enumeration of {len(function_names)} functions")
        
        if not concurrent:
            return await self.function_enumerator.enumerate_all_functions(scan_id, get_detailed_config)
        
        # Concurrent enumeration using asyncio.gather
        tasks = [
            self.function_enumerator.enumerate_function(scan_id, name, get_detailed_config)
            for name in function_names
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        functions = []
        for function_name, result in zip(function_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error enumerating function {function_name}: {result}")
            elif result:
                functions.append(result)
                logger.debug(f"Successfully enumerated function: {function_name}")
            else:
                logger.warning(f"Failed to enumerate function: {function_name}")
        
        logger.info(f"Completed concurrent enumeration of {len(functions)} functions")
        return functions

    async def enumerate_layers_only(
        self,
        scan_id: str,
        get_all_versions: bool = False,
        max_versions_per_layer: int = 5,
        concurrent: bool = True,
    ) -> List[LambdaLayer]:
        layer_names = await self.layer_enumerator.list_all_layers()
        if not layer_names:
            logger.info("No Lambda layers found")
            return []

        logger.info(f"Starting {'concurrent' if concurrent else 'sequential'} enumeration of {len(layer_names)} layers")
        
        if not concurrent:
            return await self.layer_enumerator.enumerate_all_layers(scan_id, get_all_versions, max_versions_per_layer)
        
        # Concurrent enumeration using asyncio.gather
        tasks = [
            self.layer_enumerator.enumerate_layer(scan_id, name, get_all_versions, max_versions_per_layer)
            for name in layer_names
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        layers = []
        for layer_name, result in zip(layer_names, results):
            if isinstance(result, Exception):
                logger.error(f"Error enumerating layer {layer_name}: {result}")
            elif result:
                layers.append(result)
                logger.debug(f"Successfully enumerated layer: {layer_name}")
            else:
                logger.warning(f"Failed to enumerate layer: {layer_name}")
        
        logger.info(f"Completed concurrent enumeration of {len(layers)} layers")
        return layers

    async def enumerate_all(
        self,
        scan_id: str,
        enumerate_functions: bool = True,
        enumerate_layers: bool = True,
        get_detailed_function_config: bool = True,
        get_all_layer_versions: bool = False,
        max_versions_per_layer: int = 5,
        concurrent: bool = True,
    ) -> LambdaEnumerationResult:
        start_time = datetime.now()
        logger.info("Starting comprehensive Lambda enumeration")

        functions: List[LambdaFunction] = []
        layers: List[LambdaLayer] = []
        errors = []

        try:
            if not await self.test_connectivity():
                raise LambdaEnumerationError("Lambda API connectivity test failed")

            if enumerate_functions:
                logger.info("Enumerating Lambda functions...")
                try:
                    functions = await self.enumerate_functions_only(
                        scan_id=scan_id,
                        get_detailed_config=get_detailed_function_config,
                        concurrent=concurrent,
                    )
                    logger.info(f"Successfully enumerated {len(functions)} functions")
                except Exception as exc:
                    error_msg = f"Error enumerating functions: {exc}"
                    logger.error(error_msg)
                    errors.append(
                        {
                            "operation": "enumerate_functions",
                            "error": error_msg,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            if enumerate_layers:
                logger.info("Enumerating Lambda layers...")
                try:
                    layers = await self.enumerate_layers_only(
                        scan_id=scan_id,
                        get_all_versions=get_all_layer_versions,
                        max_versions_per_layer=max_versions_per_layer,
                        concurrent=concurrent,
                    )
                    logger.info(f"Successfully enumerated {len(layers)} layers")
                except Exception as exc:
                    error_msg = f"Error enumerating layers: {exc}"
                    logger.error(error_msg)
                    errors.append(
                        {
                            "operation": "enumerate_layers",
                            "error": error_msg,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            result = LambdaEnumerationResult(
                functions=functions,
                layers=layers,
                region=self.region,
                enumeration_time=start_time.isoformat(),
                errors=errors,
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Lambda enumeration completed in {duration:.2f} seconds")
            logger.info(f"Total functions: {len(functions)}, Total layers: {len(layers)}")

            if errors:
                logger.warning(f"Enumeration completed with {len(errors)} errors")

            return result

        except Exception as exc:
            logger.error(f"Fatal error during Lambda enumeration: {exc}")
            raise LambdaEnumerationError(
                f"Lambda enumeration failed: {exc}",
                operation="enumerate_all",
                original_error=exc,
            )
