# vray_compatibility_test.py
import os
import sys
import subprocess
from pathlib import Path

print("--- V-Ray Core Engine Compatibility Test ---")

# --- 配置 ---
try:
    sys.path.insert(0, str(Path.cwd().parents[2] / 'code/python'))
    import _system_config as cfg
    VRAY_BIN = cfg.vray_bin
except ImportError:
    print("[FAIL] Could not load _system_config.py to find vray_bin.")
    sys.exit(1)
    
SCENE_FILE = Path("../00_empty_scene/empty.vrscene").resolve()

if not SCENE_FILE.exists():
    print(f"[FAIL] Test scene '{SCENE_FILE}' not found!")
    sys.exit(1)

# 定义不同的测试配置
test_cases = {
    "1_minimal_render": [
        VRAY_BIN,
        f"-sceneFile={SCENE_FILE}",
        "-display=0",
        "-frames=0"
    ],
    "2_with_gi_irradiance_map": [
        VRAY_BIN,
        f"-sceneFile={SCENE_FILE}",
        "-display=0",
        "-frames=0",
        # 强制开启 GI
        '-parameterOverride="SettingsGI::on=1"',
        '-parameterOverride="SettingsGI::primary_engine=0"', # Irradiance map
    ],
    "3_with_gi_light_cache": [
        VRAY_BIN,
        f"-sceneFile={SCENE_FILE}",
        "-display=0",
        "-frames=0",
        # 强制开启 GI
        '-parameterOverride="SettingsGI::on=1"',
        '-parameterOverride="SettingsGI::primary_engine=3"', # Light cache
    ],
}

# --- 执行测试 ---
for name, command in test_cases.items():
    print(f"\n--- Running Test: {name} ---")
    
    # 总是使用 xvfb-run
    full_command = ['xvfb-run'] + command
    
    # 禁用 CPU 扩展，这是目前最可能的解决方案
    env = os.environ.copy()
    env["VRAY_CPU_PLATFORM_EXTENSIONS"] = "0"
    
    print(f"Command: {' '.join(full_command)}")
    
    try:
        # 使用 subprocess 来更好地控制和捕获输出
        result = subprocess.run(full_command, capture_output=True, text=True, env=env, timeout=60)
        
        print(f"Return Code: {result.returncode}")
        
        if "Segmentation fault" in result.stderr or "core dumped" in result.stderr or result.returncode in [139, -11]:
             print("[RESULT] CRASH DETECTED (Segmentation Fault)!")
        elif result.returncode == 0:
            print("[RESULT] SUCCESS (No Crash).")
        else:
            print(f"[RESULT] FAILED with an error (but not a crash).")
            print("--- STDERR ---")
            print(result.stderr or "None")
            print("--------------")
            
    except subprocess.TimeoutExpired:
        print("[RESULT] FAILED (Process timed out).")
    except Exception as e:
        print(f"[RESULT] FAILED (An unexpected Python error occurred: {e})")
        
print("\n--- Test Suite Finished ---")
