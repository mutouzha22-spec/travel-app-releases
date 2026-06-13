import sys
import shutil
import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
APP_DIR = BASE_DIR.parent / "travel_app"
APK_SRC = APP_DIR / "build/app/outputs/flutter-apk/app-release.apk"


def release(version, description):
    history_dir = BASE_DIR / "history"
    history_dir.mkdir(exist_ok=True)

    version_file = BASE_DIR / "version.json"
    with open(version_file, encoding="utf-8") as f:
        data = json.load(f)
    old_version = data["version"]

    old_apk = BASE_DIR / "app.apk"
    if old_apk.exists():
        shutil.copy2(old_apk, history_dir / f"app-{old_version}.apk")
        print(f"已备份旧版本 → history/app-{old_version}.apk")

    if not APK_SRC.exists():
        print(f"错误：找不到新 APK，请先编译")
        sys.exit(1)
    shutil.copy2(APK_SRC, BASE_DIR / "app.apk")
    print(f"已更新 app.apk")

    data["version"] = version
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已更新 version.json → {version}")

    date = datetime.now().strftime("%Y-%m-%d")
    entry = f"## v{version} ({date})\n{description}\n"
    changelog = BASE_DIR / "CHANGELOG.md"
    existing = changelog.read_text(encoding="utf-8") if changelog.exists() else "# 更新日志\n\n"
    header, _, rest = existing.partition("\n\n")
    changelog.write_text(f"{header}\n\n{entry}\n{rest}", encoding="utf-8")
    print(f"已写入 CHANGELOG.md")

    dart_file = APP_DIR / "lib/services/update_service.dart"
    content = dart_file.read_text(encoding="utf-8")
    content = re.sub(
        r"const String _currentVersion = '[^']*';",
        f"const String _currentVersion = '{version}';",
        content
    )
    dart_file.write_text(content, encoding="utf-8")
    print(f"已更新代码版本号 → {version}")

    print(f"\n完成！请在 GitHub Desktop 提交并推送。")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python release.py <版本号> <更新说明>")
        sys.exit(1)
    release(sys.argv[1], sys.argv[2])
