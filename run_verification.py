import subprocess
import time
import os

def run_verification():
    """
    Launches the application in a virtual display, captures its output,
    takes a screenshot, and then terminates the application.
    """
    display = ":99"
    xvfb_cmd = f"Xvfb {display} -screen 0 1280x1024x24"
    screenshot_path = "/home/jules/verification/verification.png"
    log_path = "/home/jules/verification/app.log"

    # Use the correct pyenv Python executable
    python_executable = "/home/jules/.pyenv/shims/python"

    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

    # Start the virtual display
    xvfb_proc = subprocess.Popen(xvfb_cmd.split())

    try:
        env = os.environ.copy()
        env["DISPLAY"] = display
        env["MINISIS_ENV"] = "test"

        with open(log_path, "w") as log_file:
            app_proc = subprocess.Popen(
                [python_executable, "main.py"],
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )

            time.sleep(5)

            subprocess.run(["scrot", screenshot_path, "-d", "1"], env=env)

            app_proc.terminate()
            try:
                app_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_proc.kill()

    finally:
        xvfb_proc.terminate()
        try:
            xvfb_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            xvfb_proc.kill()

if __name__ == "__main__":
    run_verification()
