import os
import time

print("[STEP 1] Script started. About to import vray...")

try:
    import vray
    print("[STEP 2] Successfully imported 'vray' module.")
except ImportError as e:
    print(f"[ERROR] Failed to import 'vray' module. Error: {e}")
    print("Please ensure the V-Ray AppSDK is correctly installed and visible to Python.")
    exit(1)

# ----------------- 关键步骤 -----------------
# 再次设置环境变量，确保在脚本内部也生效
# 这是为了确保即使外部忘记设置，这里也能覆盖
plugin_path = "/root/workspace/ml-hypersim/code/python/tools/plugins"
os.environ['VRAY_PLUGINS_PATH'] = plugin_path
print(f"[STEP 3] Set VRAY_PLUGINS_PATH environment variable to: {os.environ['VRAY_PLUGINS_PATH']}")

# ----------------- 初始化渲染器 -----------------
# 这是我们怀疑的出错点
print("[STEP 4] About to initialize vray.VRayRenderer(False)...")
try:
    # 使用 False 参数来禁用 GUI
    renderer = vray.VRayRenderer(False)
    print("[SUCCESS] Successfully initialized vray.VRayRenderer(False) without GUI.")
    
    print("[STEP 5] V-Ray Renderer object created. Closing it.")
    renderer.close()
    time.sleep(0.5)
    print("[STEP 6] Script finished successfully.")
    
except RuntimeError as e:
    print(f"\n[ERROR] A RuntimeError occurred during V-Ray initialization: {e}")
    if "Cannot connect to license server" in str(e):
        print("This is a license server issue. Please ensure the license server is running and accessible.")
    elif "display" in str(e).lower():
        print("This is a GUI/display issue. It seems vray.VRayRenderer(False) is not correctly preventing GUI initialization.")
    else:
        print("An unexpected V-Ray runtime error occurred.")
    exit(1)
except Exception as e:
    print(f"\n[ERROR] An unexpected error occurred: {e}")
    exit(1)
    