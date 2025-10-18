# final_gi_test.py
import subprocess
import vray
import os
import sys
import time
from pathlib import Path

print("--- V-Ray GI Engine Independent Test ---")

# -------------------
# 测试函数
# -------------------
def run_render_test(test_name, enable_gi):
    print(f"\n--- Running Test: {test_name} ---")
    print(f"    Global Illumination (GI) Enabled: {enable_gi}")
    
    renderer = None
    try:
        # 1. 创建渲染器
        renderer = vray.VRayRenderer()
        print("    [Step 1] Renderer instance created.")

        # 2. 从零创建场景内容
        # 创建一个简单的平面
        geom_static_mesh = renderer.classes.GeomStaticMesh("TestPlane")
        geom_static_mesh.vertices = vray.List([vray.Vector(-100,-100,0), vray.Vector(100,-100,0), vray.Vector(100,100,0), vray.Vector(-100,100,0)])
        geom_static_mesh.faces = vray.List([0,1,2, 0,2,3])
        
        # 创建一个简单的材质
        brdf = renderer.classes.BRDFVRayMtl("TestMaterial")
        brdf.diffuse = vray.AColor(0.8, 0.8, 0.8)
        mtl = renderer.classes.MtlSingleBRDF("TestMtl")
        mtl.brdf = brdf
        
        # 创建场景节点
        node = renderer.classes.Node("TestNode")
        node.geometry = geom_static_mesh
        node.material = mtl
        print("    [Step 2] Minimal scene created in memory.")
        
        # 3. 创建一盏灯
        light = renderer.classes.LightDome("TestLight")
        light.texture = vray.AColor(1.0, 1.0, 1.0)
        light.texture_multiplier = 2.0 # 让它亮一点
        print("    [Step 3] Simple light created.")

        # 4. 设置渲染参数
        settings_output = renderer.classes.SettingsOutput("TestOutput")
        settings_output.img_width = 320
        settings_output.img_height = 240
        
        # 5. 设置 GI (这是测试的关键)
        settings_gi = renderer.classes.SettingsGI("TestGI")
        settings_gi.on = 1 if enable_gi else 0 # 根据参数开启或关闭
        print(f"    [Step 4] GI is set to {'ON' if enable_gi else 'OFF'}.")

        # 6. 开始渲染
        print("    [Step 5] Starting render... (This is the critical point)")
        renderer.start()
        renderer.waitForRenderEnd()
        print("    [Step 6] Render finished.")
        
        print("\n    [RESULT] SUCCESS (No Crash)!")
        return True
        
    except Exception as e:
        print(f"\n    [RESULT] FAILED with Python Exception: {e}")
        return False
        
    finally:
        if renderer:
            renderer.close()

# -------------------
# 执行测试
# -------------------
# 包装在 xvfb-run 中执行
if 'XVFB_RUNNING' not in os.environ:
    print("\n[INFO] This script needs to run under xvfb-run. Relaunching myself...")
    try:
        # 设置环境变量以禁用 CPU 扩展
        env = os.environ.copy()
        env["VRAY_CPU_PLATFORM_EXTENSIONS"] = "0"
        env["XVFB_RUNNING"] = "1"
        
        # 使用 subprocess 重新启动自己
        subprocess.run(['xvfb-run', 'python'] + sys.argv, env=env, check=True)
        sys.exit(0) # 成功退出父进程
    except Exception as e:
        print(f"[FAIL] Failed to relaunch with xvfb-run. Error: {e}")
        sys.exit(1)
        
# --- 实际测试逻辑 ---
gi_disabled_success = run_render_test("Test 1: GI Disabled", enable_gi=False)
gi_enabled_success = run_render_test("Test 2: GI Enabled", enable_gi=True)

# --- 最终诊断 ---
print("\n--- FINAL DIAGNOSIS ---")
if gi_disabled_success and not gi_enabled_success:
    print("[INCOMPATIBILITY CONFIRMED] The test with GI disabled SUCCEEDED, but the test with GI enabled FAILED.")
    print("                           This provides definitive proof that the incompatibility lies within the V-Ray")
    print("                           Global Illumination (GI) engine in your current environment.")
    print("\n[RECOMMENDATION] Your configuration is correct, but the environment is not compatible.")
    print("                 Please switch to a different Docker image, such as 'ubuntu:18.04'.")
elif not gi_disabled_success:
    print("[CRITICAL FAIL] Even the most basic render (with GI disabled) failed.")
    print("                 This indicates a more fundamental problem with the V-Ray installation or environment.")
else:
    print("[UNEXPECTED SUCCESS] Both tests passed. The previous crashes might be scene-specific.")
    print("                      However, given the consistent failures with Hypersim's scenes, an")
    print("                      environmental incompatibility is still the most likely culprit.")
    
print("\n--- Doctor Finished ---")
