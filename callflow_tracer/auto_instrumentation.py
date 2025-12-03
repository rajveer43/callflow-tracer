"""
Auto-instrumentation for I/O and Database operations

Provides automatic tracing for httpx, requests, aiohttp, redis, and boto3.
"""

import time
import functools
import inspect
from typing import Any, Callable, Dict, Optional, Union
import urllib.parse
from contextlib import contextmanager

# Import tracing functionality
from .tracer import CallTracer, get_current_graph
from . import trace_scope


class AutoInstrumentor:
    """Base class for auto-instrumentation."""
    
    def __init__(self, tracer: Optional[CallTracer] = None):
        self.tracer = tracer
        self.original_methods: Dict[str, Callable] = {}
        self.instrumentation_enabled = False
    
    def enable(self) -> None:
        """Enable instrumentation."""
        if self.instrumentation_enabled:
            return
        self.instrumentation_enabled = True
        self._patch_methods()
    
    def disable(self) -> None:
        """Disable instrumentation."""
        if not self.instrumentation_enabled:
            return
        self.instrumentation_enabled = False
        self._unpatch_methods()
    
    def _patch_methods(self) -> None:
        """Override in subclasses to patch specific methods."""
        pass
    
    def _unpatch_methods(self) -> None:
        """Restore original methods."""
        for key, original_method in self.original_methods.items():
            module_name, method_name = key.rsplit('.', 1)
            module = __import__(module_name, fromlist=[method_name])
            setattr(module, method_name, original_method)
        self.original_methods.clear()
    
    def _store_original(self, module: Any, method_name: str) -> None:
        """Store original method before patching."""
        key = f"{module.__name__}.{method_name}"
        if key not in self.original_methods:
            self.original_methods[key] = getattr(module, method_name)


class HTTPInstrumentor(AutoInstrumentor):
    """Auto-instrumentation for HTTP clients (requests, httpx, aiohttp)."""
    
    def _patch_methods(self) -> None:
        """Patch HTTP client methods."""
        # Patch requests
        try:
            import requests
            self._patch_requests(requests)
        except ImportError:
            pass
        
        # Patch httpx
        try:
            import httpx
            self._patch_httpx(httpx)
        except ImportError:
            pass
        
        # Patch aiohttp
        try:
            import aiohttp
            self._patch_aiohttp(aiohttp)
        except ImportError:
            pass
    
    def _patch_requests(self, requests) -> None:
        """Patch requests library."""
        # Patch Session.request
        if hasattr(requests.Session, 'request'):
            self._store_original(requests.Session, 'request')
            original_request = requests.Session.request
            
            @functools.wraps(original_request)
            def traced_request(self, method, url, **kwargs):
                start_time = time.time()
                try:
                    response = original_request(self, method, url, **kwargs)
                    duration = time.time() - start_time
                    
                    # Record the HTTP call
                    self._record_http_call(
                        method=method.upper(),
                        url=url,
                        status_code=response.status_code,
                        duration=duration,
                        success=response.status_code < 400,
                        library="requests"
                    )
                    
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_http_call(
                        method=method.upper(),
                        url=url,
                        status_code=None,
                        duration=duration,
                        success=False,
                        library="requests",
                        error=str(e)
                    )
                    raise
            
            requests.Session.request = traced_request
        
        # Patch requests.get/post/put/delete etc.
        for method_name in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if hasattr(requests, method_name):
                self._store_original(requests, method_name)
                original_method = getattr(requests, method_name)
                
                @functools.wraps(original_method)
                def traced_method(*args, **kwargs):
                    # Extract URL from args/kwargs
                    url = args[0] if args else kwargs.get('url', '')
                    start_time = time.time()
                    try:
                        response = original_method(*args, **kwargs)
                        duration = time.time() - start_time
                        
                        self._record_http_call(
                            method=method_name.upper(),
                            url=url,
                            status_code=response.status_code,
                            duration=duration,
                            success=response.status_code < 400,
                            library="requests"
                        )
                        
                        return response
                    except Exception as e:
                        duration = time.time() - start_time
                        self._record_http_call(
                            method=method_name.upper(),
                            url=url,
                            status_code=None,
                            duration=duration,
                            success=False,
                            library="requests",
                            error=str(e)
                        )
                        raise
                
                setattr(requests, method_name, traced_method)
    
    def _patch_httpx(self, httpx) -> None:
        """Patch httpx library."""
        # Patch Client.request
        if hasattr(httpx.Client, 'request'):
            self._store_original(httpx.Client, 'request')
            original_request = httpx.Client.request
            
            @functools.wraps(original_request)
            def traced_request(self, method, url, **kwargs):
                start_time = time.time()
                try:
                    response = original_request(self, method, url, **kwargs)
                    duration = time.time() - start_time
                    
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=response.status_code,
                        duration=duration,
                        success=response.status_code < 400,
                        library="httpx"
                    )
                    
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=None,
                        duration=duration,
                        success=False,
                        library="httpx",
                        error=str(e)
                    )
                    raise
            
            httpx.Client.request = traced_request
        
        # Patch async methods
        if hasattr(httpx.AsyncClient, 'request'):
            self._store_original(httpx.AsyncClient, 'request')
            original_request = httpx.AsyncClient.request
            
            @functools.wraps(original_request)
            async def traced_async_request(self, method, url, **kwargs):
                start_time = time.time()
                try:
                    response = await original_request(self, method, url, **kwargs)
                    duration = time.time() - start_time
                    
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=response.status_code,
                        duration=duration,
                        success=response.status_code < 400,
                        library="httpx"
                    )
                    
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=None,
                        duration=duration,
                        success=False,
                        library="httpx",
                        error=str(e)
                    )
                    raise
            
            httpx.AsyncClient.request = traced_async_request
    
    def _patch_aiohttp(self, aiohttp) -> None:
        """Patch aiohttp library."""
        # Patch ClientSession.request
        if hasattr(aiohttp.ClientSession, 'request'):
            self._store_original(aiohttp.ClientSession, 'request')
            original_request = aiohttp.ClientSession.request
            
            @functools.wraps(original_request)
            async def traced_request(self, method, url, **kwargs):
                start_time = time.time()
                try:
                    response = await original_request(self, method, url, **kwargs)
                    duration = time.time() - start_time
                    
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=response.status,
                        duration=duration,
                        success=response.status < 400,
                        library="aiohttp"
                    )
                    
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_http_call(
                        method=method.upper(),
                        url=str(url),
                        status_code=None,
                        duration=duration,
                        success=False,
                        library="aiohttp",
                        error=str(e)
                    )
                    raise
            
            aiohttp.ClientSession.request = traced_request
    
    def _record_http_call(self, method: str, url: str, status_code: Optional[int],
                         duration: float, success: bool, library: str,
                         error: Optional[str] = None) -> None:
        """Record an HTTP call in the trace."""
        graph = get_current_graph()
        if not graph:
            return
        
        # Parse URL to get domain
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc or url
        
        # Create function name for the HTTP call
        function_name = f"{library}.{method.lower()}"
        
        # Add call with metadata
        caller_name = "auto_instrumentation"
        if graph.tracer and graph.tracer.call_stack:
            caller_name = graph.tracer.call_stack[-1] if graph.tracer.call_stack else caller_name
        
        metadata = {
            "method": method,
            "url": url,
            "domain": domain,
            "status_code": status_code,
            "success": success,
            "library": library,
            "duration": duration,
            "error": error
        }
        
        graph.add_call(caller_name, function_name, duration, metadata)


class RedisInstrumentor(AutoInstrumentor):
    """Auto-instrumentation for Redis operations."""
    
    def _patch_methods(self) -> None:
        """Patch Redis methods."""
        try:
            import redis
            self._patch_redis(redis)
        except ImportError:
            pass
        
        try:
            import redis.asyncio as aioredis
            self._patch_aioredis(aioredis)
        except ImportError:
            pass
    
    def _patch_redis(self, redis) -> None:
        """Patch redis-py library."""
        if hasattr(redis.Redis, 'execute_command'):
            self._store_original(redis.Redis, 'execute_command')
            original_execute = redis.Redis.execute_command
            
            @functools.wraps(original_execute)
            def traced_execute(self, *args, **kwargs):
                start_time = time.time()
                command = args[0] if args else 'unknown'
                try:
                    result = original_execute(self, *args, **kwargs)
                    duration = time.time() - start_time
                    
                    self._record_redis_call(
                        command=command,
                        args=args[1:] if len(args) > 1 else [],
                        duration=duration,
                        success=True,
                        library="redis"
                    )
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_redis_call(
                        command=command,
                        args=args[1:] if len(args) > 1 else [],
                        duration=duration,
                        success=False,
                        library="redis",
                        error=str(e)
                    )
                    raise
            
            redis.Redis.execute_command = traced_execute
    
    def _patch_aioredis(self, aioredis) -> None:
        """Patch aioredis library."""
        if hasattr(aioredis.Redis, 'execute_command'):
            self._store_original(aioredis.Redis, 'execute_command')
            original_execute = aioredis.Redis.execute_command
            
            @functools.wraps(original_execute)
            async def traced_execute(self, *args, **kwargs):
                start_time = time.time()
                command = args[0] if args else 'unknown'
                try:
                    result = await original_execute(self, *args, **kwargs)
                    duration = time.time() - start_time
                    
                    self._record_redis_call(
                        command=command,
                        args=args[1:] if len(args) > 1 else [],
                        duration=duration,
                        success=True,
                        library="aioredis"
                    )
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_redis_call(
                        command=command,
                        args=args[1:] if len(args) > 1 else [],
                        duration=duration,
                        success=False,
                        library="aioredis",
                        error=str(e)
                    )
                    raise
            
            aioredis.Redis.execute_command = traced_execute
    
    def _record_redis_call(self, command: str, args: list, duration: float,
                          success: bool, library: str, error: Optional[str] = None) -> None:
        """Record a Redis call in the trace."""
        graph = get_current_graph()
        if not graph:
            return
        
        function_name = f"{library}.{command}"
        
        caller_name = "auto_instrumentation"
        if graph.tracer and graph.tracer.call_stack:
            caller_name = graph.tracer.call_stack[-1] if graph.tracer.call_stack else caller_name
        
        metadata = {
            "command": command,
            "args": args[:3],  # Limit args to avoid sensitive data
            "success": success,
            "library": library,
            "duration": duration,
            "error": error
        }
        
        graph.add_call(caller_name, function_name, duration, metadata)


class Boto3Instrumentor(AutoInstrumentor):
    """Auto-instrumentation for AWS Boto3 operations."""
    
    def _patch_methods(self) -> None:
        """Patch Boto3 methods."""
        try:
            import boto3
            self._patch_boto3(boto3)
        except ImportError:
            pass
    
    def _patch_boto3(self, boto3) -> None:
        """Patch boto3 library."""
        # Patch the BaseClient's _make_request method
        from botocore.client import BaseClient
        
        if hasattr(BaseClient, '_make_request'):
            self._store_original(BaseClient, '_make_request')
            original_make_request = BaseClient._make_request
            
            @functools.wraps(original_make_request)
            def traced_make_request(self, operation_model, request_dict, request_context):
                start_time = time.time()
                service_name = getattr(self, 'service_name', 'unknown')
                operation_name = operation_model.name
                
                try:
                    response = original_make_request(
                        self, operation_model, request_dict, request_context
                    )
                    duration = time.time() - start_time
                    
                    self._record_boto3_call(
                        service=service_name,
                        operation=operation_name,
                        duration=duration,
                        success=True,
                        library="boto3"
                    )
                    
                    return response
                except Exception as e:
                    duration = time.time() - start_time
                    self._record_boto3_call(
                        service=service_name,
                        operation=operation_name,
                        duration=duration,
                        success=False,
                        library="boto3",
                        error=str(e)
                    )
                    raise
            
            BaseClient._make_request = traced_make_request
    
    def _record_boto3_call(self, service: str, operation: str, duration: float,
                           success: bool, library: str, error: Optional[str] = None) -> None:
        """Record a Boto3 call in the trace."""
        graph = get_current_graph()
        if not graph:
            return
        
        function_name = f"{library}.{service}.{operation.lower()}"
        
        caller_name = "auto_instrumentation"
        if graph.tracer and graph.tracer.call_stack:
            caller_name = graph.tracer.call_stack[-1] if graph.tracer.call_stack else caller_name
        
        metadata = {
            "service": service,
            "operation": operation,
            "success": success,
            "library": library,
            "duration": duration,
            "error": error
        }
        
        graph.add_call(caller_name, function_name, duration, metadata)


class AutoInstrumentationManager:
    """Manages all auto-instrumentation."""
    
    def __init__(self):
        self.instrumentors = {
            'http': HTTPInstrumentor(),
            'redis': RedisInstrumentor(),
            'boto3': Boto3Instrumentor()
        }
        self.enabled = False
    
    def enable_all(self) -> None:
        """Enable all auto-instrumentation."""
        for instrumentor in self.instrumentors.values():
            instrumentor.enable()
        self.enabled = True
    
    def disable_all(self) -> None:
        """Disable all auto-instrumentation."""
        for instrumentor in self.instrumentors.values():
            instrumentor.disable()
        self.enabled = False
    
    def enable_http(self) -> None:
        """Enable HTTP instrumentation."""
        self.instrumentors['http'].enable()
    
    def enable_redis(self) -> None:
        """Enable Redis instrumentation."""
        self.instrumentors['redis'].enable()
    
    def enable_boto3(self) -> None:
        """Enable Boto3 instrumentation."""
        self.instrumentors['boto3'].enable()
    
    def disable_http(self) -> None:
        """Disable HTTP instrumentation."""
        self.instrumentors['http'].disable()
    
    def disable_redis(self) -> None:
        """Disable Redis instrumentation."""
        self.instrumentors['redis'].disable()
    
    def disable_boto3(self) -> None:
        """Disable Boto3 instrumentation."""
        self.instrumentors['boto3'].disable()


# Global manager instance
_global_manager = None


def get_auto_instrumentation_manager() -> AutoInstrumentationManager:
    """Get the global auto-instrumentation manager."""
    global _global_manager
    if _global_manager is None:
        _global_manager = AutoInstrumentationManager()
    return _global_manager


@contextmanager
def auto_instrumentation(enabled: bool = True):
    """Context manager for auto-instrumentation."""
    manager = get_auto_instrumentation_manager()
    original_state = manager.enabled
    
    if enabled:
        manager.enable_all()
    
    try:
        yield manager
    finally:
        if not original_state:
            manager.disable_all()


def enable_auto_instrumentation(libraries: Optional[list] = None) -> None:
    """Enable auto-instrumentation for specified libraries."""
    manager = get_auto_instrumentation_manager()
    
    if libraries is None:
        manager.enable_all()
    else:
        for lib in libraries:
            if lib == 'http':
                manager.enable_http()
            elif lib == 'redis':
                manager.enable_redis()
            elif lib == 'boto3':
                manager.enable_boto3()


def disable_auto_instrumentation(libraries: Optional[list] = None) -> None:
    """Disable auto-instrumentation for specified libraries."""
    manager = get_auto_instrumentation_manager()
    
    if libraries is None:
        manager.disable_all()
    else:
        for lib in libraries:
            if lib == 'http':
                manager.disable_http()
            elif lib == 'redis':
                manager.disable_redis()
            elif lib == 'boto3':
                manager.disable_boto3()
