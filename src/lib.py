import os
import sys
import json
from enum import Enum


class MiddlewareType(Enum):
    NATIVE = 0,
    DAPR = 1


def get_middleware_type() -> MiddlewareType:
    return MiddlewareType.DAPR


def get_script_path() -> str:
    """Return the absolute path to the directory the invoked Python script
    is located in."""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_cache_data():
    return json.loads(os.getenv('VELOCITAS_CACHE_DATA'))


def get_services():
    return json.load(open(f"{get_script_path()}/services.json", encoding="utf-8"))


def replace_variables(input: str, vars: dict[str]) -> str:
    for key, value in vars.items():
        input = input.replace('${{ '+key+' }}', str(value))
    return input


def wrap_in_dapr(app_id: str, app_port: int, program_args: list[str], env: dict[str]) -> list[str]:
    env['DAPR_GRPC_PORT'] = str(891)
    env['DAPR_HTTP_PORT'] = str(123)
    dapr_args = [
        'dapr',
        'run',
        '--app-id', app_id,
        '--app-protocol', 'grpc',
        '--app-port', str(app_port),
        '--components-path', f'{get_script_path()}/.dapr/components',
        '--config', f'{get_script_path()}/.dapr/config.yaml'
        ]

    dapr_args.reverse()
    for dapr_arg in dapr_args:
        program_args.insert(0, dapr_arg)
