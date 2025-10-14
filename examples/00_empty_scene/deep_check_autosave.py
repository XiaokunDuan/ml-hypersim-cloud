import argparse
import os
import time
import vray

def deep_check_vrscene_autosave(vrscene_file):
    """
    Loads a .vrscene file using the V-Ray AppSDK and inspects plugin
    properties in memory to find problematic auto_save settings.
    """
    if not os.path.exists(vrscene_file):
        print(f"[FATAL] Scene file not found: {vrscene_file}")
        return

    print(f"\n--- Deep Checking Scene File: {vrscene_file} ---")

    renderer = None
    try:
        # Initialize renderer in headless mode
        renderer = vray.VRayRenderer(False)
        
        # Load the scene file into memory
        print("[INFO] Loading scene into V-Ray AppSDK...")
        renderer.load(vrscene_file)
        # Give it a moment to process
        time.sleep(1) 
        print("[INFO] Scene loaded.")

        problem_found = False

        # List of plugin classes that are known to have auto_save functionality
        plugin_classes_to_check = [
            "SettingsLightCache",
            "SettingsIrradianceMap",
            "SettingsCaustics",
            # Add other potential classes here if needed
        ]

        for class_name in plugin_classes_to_check:
            print(f"\n[CHECKING] Plugins of type: {class_name}")
            try:
                plugin_class = getattr(renderer.classes, class_name)
                instances = plugin_class.getInstances()
                
                if not instances:
                    print("    -> No instances found.")
                    continue

                for inst in instances:
                    # Check if the instance has 'auto_save' and 'auto_save_file' attributes
                    if hasattr(inst, 'auto_save') and hasattr(inst, 'auto_save_file'):
                        is_autosave_enabled = inst.auto_save
                        autosave_file_path = inst.auto_save_file
                        
                        print(f"    -> Found instance: {inst.getName()}")
                        print(f"       - auto_save is set to: {is_autosave_enabled}")
                        print(f"       - auto_save_file is set to: '{autosave_file_path}'")

                        # The condition that causes the error
                        if is_autosave_enabled and not autosave_file_path:
                            print(f"    [!!! PROBLEM FOUND !!!]")
                            print(f"    -> Instance '{inst.getName()}' of type '{class_name}' has auto_save enabled with an empty file path.")
                            problem_found = True
                    else:
                        print(f"    -> Instance '{inst.getName()}' does not have full auto_save properties.")

            except AttributeError:
                print(f"    -> Class '{class_name}' not found in this V-Ray version.")
            except Exception as e:
                print(f"    -> An error occurred while checking {class_name}: {e}")

        if not problem_found:
            print("\n[INFO] No problematic auto_save settings were found during deep check.")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during the process: {e}")
    finally:
        if renderer:
            print("[INFO] Closing renderer.")
            renderer.close()
            time.sleep(0.5)

    print("\n--- Deep Check Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deep diagnose .vrscene files for auto_save issues.")
    parser.add_argument("--file", required=True, help="The .vrscene file to check.")
    args = parser.parse_args()
    
    deep_check_vrscene_autosave(args.file)

    