"""
AI Knowledge Graph — EXE 打包脚本
使用 PyInstaller 将 FastAPI 后端 + Vite 前端 + 种子数据 打包为单个 exe

命名规范:
  akg-v{version}-{commit_short}-{YYYYMMDD}-{HHmm}.exe
  例: akg-v0.1.0-dbdf735-20260313-1543.exe

用法:
  cd ai-knowledge-graph
  python scripts/build_exe.py
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# ── Paths ──
ROOT = Path(__file__).parent.parent.resolve()
API_DIR = ROOT / "apps" / "api"
WEB_DIR = ROOT / "packages" / "web"
WEB_DIST = WEB_DIR / "dist"
SEED_JSON = ROOT / "data" / "seed" / "programming" / "seed_graph.json"
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"


def get_git_info() -> tuple[str, str]:
    """Get short commit hash and timestamp"""
    try:
        commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%h"], cwd=str(ROOT), text=True
        ).strip()
        return commit, datetime.now().strftime("%Y%m%d-%H%M")
    except Exception:
        return "unknown", datetime.now().strftime("%Y%m%d-%H%M")


def get_version() -> str:
    """Read version from package.json"""
    import json
    pkg = ROOT / "package.json"
    with open(pkg, encoding="utf-8") as f:
        return json.load(f).get("version", "0.1.0")


def build_frontend():
    """Build the Vite frontend"""
    print("\n📦 Building frontend...")
    if WEB_DIST.exists():
        print("   Using existing dist/ (run 'pnpm build' to rebuild)")
    else:
        subprocess.check_call(["pnpm", "build"], cwd=str(ROOT), shell=True)
    assert WEB_DIST.exists(), f"Frontend dist not found at {WEB_DIST}"
    assert (WEB_DIST / "index.html").exists(), "index.html missing in dist"
    print(f"   ✅ Frontend dist ready: {WEB_DIST}")


def build_exe():
    """Run PyInstaller to create the exe"""
    commit, timestamp = get_git_info()
    version = get_version()
    exe_name = f"akg-v{version}-{commit}-{timestamp}"

    print(f"\n🔨 Building exe: {exe_name}.exe")

    # Clean previous builds
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)

    # Prepare staging directory for added data
    staging = BUILD_DIR / "staging"
    staging.mkdir(parents=True, exist_ok=True)

    # Copy frontend dist → staging/web_dist
    web_staging = staging / "web_dist"
    shutil.copytree(WEB_DIST, web_staging)
    print(f"   📁 Staged frontend: {web_staging}")

    # Copy seed data → staging/seed_data
    seed_staging = staging / "seed_data"
    seed_staging.mkdir(parents=True)
    shutil.copy2(SEED_JSON, seed_staging / "seed_graph.json")
    print(f"   📁 Staged seed data: {seed_staging}")

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", exe_name,
        "--onefile",
        "--console",  # Keep console for server logs
        "--noconfirm",
        # Add data
        "--add-data", f"{web_staging};web_dist",
        "--add-data", f"{seed_staging};seed_data",
        # Hidden imports that PyInstaller misses
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--hidden-import", "httptools",
        "--hidden-import", "dotenv",
        "--hidden-import", "pydantic_settings",
        "--hidden-import", "multipart",  # for form uploads if needed
        "--hidden-import", "email_validator",
        # Paths
        "--paths", str(API_DIR),
        # Working dirs
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR / "work"),
        "--specpath", str(BUILD_DIR),
        # Entry point
        str(API_DIR / "main.py"),
    ]

    print(f"   Running PyInstaller...")
    subprocess.check_call(cmd, cwd=str(ROOT))

    exe_path = DIST_DIR / f"{exe_name}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Build successful!")
        print(f"   📦 {exe_path}")
        print(f"   📏 Size: {size_mb:.1f} MB")
        print(f"   🏷️  Version: v{version}")
        print(f"   🔗 Commit: {commit}")
        print(f"   📅 Time: {timestamp}")
    else:
        print(f"\n❌ Build failed — exe not found at {exe_path}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("  AI Knowledge Graph — EXE Builder")
    print("=" * 50)

    # Verify we're in the right directory
    assert (ROOT / "package.json").exists(), f"Not in project root: {ROOT}"
    assert SEED_JSON.exists(), f"Seed data not found: {SEED_JSON}"

    build_frontend()
    build_exe()


if __name__ == "__main__":
    main()