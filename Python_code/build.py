# build.py
import subprocess
import shutil
import os


def run_command(cmd):
    """Выполняет команду и выводит результат"""
    print(f"Выполняется: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Ошибка: {result.stderr}")
        return False
    print(result.stdout)
    return True


def clean():
    """Очистка старых сборок"""
    print("\n[1/4] Очистка старых сборок...")

    folders = ['build', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"  Удалена папка {folder}")

    for file in os.listdir('.'):
        if file.endswith('.spec'):
            os.remove(file)
            print(f"  Удалён {file}")

    print("  Готово!")


def build_main():
    """Сборка main.py"""
    print("\n[2/4] Сборка main.py...")

    cmd = (
        'pyinstaller --onefile '
        '--windowed '
        '--name Miksher '
        '--icon "data/иконка.ico" '
        'main.py'
    )
    return run_command(cmd)


def build_settings():
    """Сборка settings_main.py"""
    print("\n[3/4] Сборка settings_main.py...")

    cmd = (
        'pyinstaller --onefile '
        '--windowed '
        '--name Settings '
        '--icon "data/иконка.ico" '
        'settings_main.py'
    )
    return run_command(cmd)


def finish():
    """Завершение"""
    print("\n[4/4] Готово!")
    print("\n" + "=" * 50)
    print("  Сборка завершена успешно!")
    print("  .exe файлы находятся в папке 'dist'")


if __name__ == "__main__":
    print("=" * 50)
    print("  Build Miksher")
    print("=" * 50)

    clean()

    if not build_main():
        print("Ошибка при сборке main.py!")
        exit(1)

    if not build_settings():
        print("Ошибка при сборке settings_main.py!")
        exit(1)

    finish()