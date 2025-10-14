import argparse
import os
import re

def check_vrscene_paths(vrscene_file):
    """
    Checks for missing texture files and problematic auto_save settings.
    """
    if not os.path.exists(vrscene_file):
        print(f"\n[FATAL] Scene file not found: {vrscene_file}")
        return

    print(f"\n--- Checking Scene File: {vrscene_file} ---")
    
    with open(vrscene_file, 'r') as f:
        content = f.read()

    # --- 检查纹理文件 ---
    print("\n[1] Checking for missing texture files...")
    # 正则表达式匹配类似 file="<path>" 的模式
    texture_paths = re.findall(r'file\s*=\s*"([^"]+)"', content)
    
    missing_files_found = False
    if not texture_paths:
        print("    -> No texture file references found.")
    else:
        for path in set(texture_paths): # 使用 set 去重
            # V-Ray 可能会使用正斜杠或反斜杠，我们统一处理
            normalized_path = path.replace('\\', '/')
            
            # 检查绝对路径和相对路径
            if not os.path.exists(normalized_path):
                # 如果是相对路径，尝试拼接当前工作目录
                relative_check_path = os.path.join(os.path.dirname(vrscene_file), normalized_path)
                if not os.path.exists(relative_check_path):
                    print(f'    [WARNING] Missing texture file: {path}')
                    missing_files_found = True

    if not missing_files_found and texture_paths:
        print("    -> All texture files seem to exist.")

    # --- 检查自动保存问题 ---
    print("\n[2] Checking for problematic auto_save settings...")
    
    problematic_autosave_found = False
    # 使用正则表达式查找整个插件块
    plugin_blocks = re.finditer(r'(\w+)\s+\w+@\w+\s*{([^}]+)}', content, re.DOTALL)

    for match in plugin_blocks:
        plugin_type = match.group(1)
        plugin_content = match.group(2)
        
        # 如果插件内容里有 auto_save = 1;
        if 'auto_save = 1;' in plugin_content:
            # 检查是否有 auto_save_file 定义，并且值不为空
            file_match = re.search(r'auto_save_file\s*=\s*"([^"]+)"', plugin_content)
            
            # 如果没找到 auto_save_file 或者找到了但是路径为空
            if not file_match or not file_match.group(1):
                problematic_autosave_found = True
                print(f"    [WARNING] Problematic auto_save found in plugin of type '{plugin_type}':")
                print("    -------------------- PLUGIN BLOCK --------------------")
                # 打印整个插件块以便调试
                print(match.group(0).strip())
                print("    ----------------------------------------------------")
                print("    -> This plugin has auto_save enabled but the file path is missing or empty.")

    if not problematic_autosave_found:
        print("    -> No problematic auto_save settings were found.")
        
    print("\n--- Check Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnose .vrscene files.")
    parser.add_argument("--file", required=True, help="The .vrscene file to check.")
    args = parser.parse_args()
    
    check_vrscene_paths(args.file)


    