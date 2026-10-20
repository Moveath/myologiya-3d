"""Start the already installed local bridge; no model/prefs writes."""
import importlib.util
import sys
import bpy

path = 'C:/Users/Пользователь/Desktop/blender-codex-mcp-main/addon.py'
spec = importlib.util.spec_from_file_location('batch7_existing_bridge', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.register()
bpy.types.blendermcp_server = module.BlenderMCPServer(host='127.0.0.1', port=9876)
bpy.types.blendermcp_server.start()
