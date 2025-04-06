def is_patch_valid(text):
    return text.startswith("diff --git") and "@@" in text and "--- " in text

def apply_patch_safely(patch_name):
    from agents.repair_commit_with_log import repair_patch_with_gpt

    for ext in [".patch", ".diff"]:
        path = f"patches/{patch_name}{ext}"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                patch_text = f.read()

            if not is_patch_valid(patch_text):
                print(f"⚠️ Патч {patch_name} невалидный — запускаю GPT-восстановление")
                repaired = repair_patch_with_gpt(patch_text)
                repaired_path = f"patches/{patch_name}_repaired.patch"
                with open(repaired_path, "w", encoding="utf-8") as f:
                    f.write(repaired)
                path = repaired_path

            result = os.system(f"git apply {path}")
            return result == 0, path

    return False, None
