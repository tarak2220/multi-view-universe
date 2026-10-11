
from pathlib import Path
import threading
import webbrowser

from flask import Flask, abort, jsonify, render_template, send_from_directory

# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "multi view universe"
WELCOME_IMAGE = BASE_DIR / "Multi View Universe Exhibit.png"

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# --------------------------------------------------
# DISPLAY STATE
# --------------------------------------------------

state_lock = threading.Lock()
current_view = 0  # 0 = Welcome, 1-6 = Exhibit images

GPIO_AVAILABLE = False
GPIO_ERROR = None
GPIO = None

PORT = 5001

# Raspberry Pi BCM pins
# Welcome: GPIO 5
# View 1:  GPIO 6
# View 2:  GPIO 13
# View 3:  GPIO 16
# View 4:  GPIO 19
# View 5:  GPIO 20
# View 6:  GPIO 21
# Restart: GPIO 26

BUTTON_PINS = {
    5: 0,
    6: 1,
    13: 2,
    16: 3,
    19: 4,
    20: 5,
    21: 6,
    26: 0
}


# --------------------------------------------------
# VIEW MANAGEMENT
# --------------------------------------------------

def set_view(view_number):
    """Set the currently displayed image."""

    global current_view

    if view_number not in range(0, 7):
        return False

    with state_lock:
        current_view = view_number

    print(f"Selected view: {view_number}")
    return True


def on_button_pressed(channel):
    """Handle a physical Raspberry Pi button press."""

    view_number = BUTTON_PINS.get(channel, 0)
    set_view(view_number)

    print(
        f"Physical button pressed on BCM {channel}; "
        f"selected view {view_number}"
    )


# --------------------------------------------------
# RASPBERRY PI GPIO SETUP
# --------------------------------------------------

def setup_gpio():
    """Enable physical buttons on Raspberry Pi."""

    global GPIO_AVAILABLE, GPIO_ERROR, GPIO

    try:
        import RPi.GPIO as GPIO_module

        GPIO = GPIO_module

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for pin in BUTTON_PINS:
            GPIO.setup(
                pin,
                GPIO.IN,
                pull_up_down=GPIO.PUD_UP
            )

            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=on_button_pressed,
                bouncetime=250
            )

        GPIO_AVAILABLE = True
        GPIO_ERROR = None

        print("Raspberry Pi physical buttons enabled.")

    except Exception as exc:
        GPIO_AVAILABLE = False
        GPIO_ERROR = str(exc)

        print(
            "GPIO buttons unavailable. "
            "Website controls remain available."
        )
        print(f"GPIO message: {exc}")


def cleanup_gpio():
    """Clean up GPIO when the application stops."""

    if GPIO is not None:
        try:
            GPIO.cleanup()
            print("GPIO resources cleaned up.")
        except Exception as exc:
            print(f"GPIO cleanup warning: {exc}")


# --------------------------------------------------
# WEBSITE ROUTES
# --------------------------------------------------

@app.route("/")
def index():
    """Display the main website."""

    return render_template("index.html")


@app.route("/welcome")
def welcome_image():
    """Serve the welcome image."""

    if not WELCOME_IMAGE.is_file():
        abort(
            404,
            description=(
                "Welcome image not found. Expected file: "
                f"{WELCOME_IMAGE.name}"
            )
        )

    return send_from_directory(
        str(BASE_DIR),
        WELCOME_IMAGE.name
    )


@app.route("/image/<int:number>")
def exhibit_image(number):
    """Serve exhibit images 1.jpg through 6.jpg."""

    if number not in range(1, 7):
        abort(404, description="Invalid exhibit image number.")

    filename = f"{number}.jpg"
    image_path = IMAGE_DIR / filename

    if not image_path.is_file():
        abort(
            404,
            description=f"Exhibit image not found: {filename}"
        )

    return send_from_directory(
        str(IMAGE_DIR),
        filename
    )


# --------------------------------------------------
# API: CURRENT VIEW
# --------------------------------------------------

@app.route("/api/current-view")
def api_current_view():
    """Return the currently selected view."""

    with state_lock:
        view = current_view

    return jsonify({
        "view": view,
        "gpio_available": GPIO_AVAILABLE,
        "gpio_error": GPIO_ERROR
    })


# --------------------------------------------------
# API: SELECT A VIEW FROM THE WEBSITE
# --------------------------------------------------

@app.route("/api/select/<int:number>", methods=["POST"])
def api_select_view(number):
    """Allow website buttons to select a view."""

    if number not in range(0, 7):
        abort(
            400,
            description="View must be 0 (Welcome) or 1 through 6."
        )

    set_view(number)

    return jsonify({
        "ok": True,
        "view": number
    })


# --------------------------------------------------
# OPEN THE WEBSITE
# --------------------------------------------------

def open_browser():
    """Open the local website in the default browser."""

    webbrowser.open(f"http://127.0.0.1:{PORT}")


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    setup_gpio()

    # Open the browser shortly after starting Flask.
    threading.Timer(1.0, open_browser).start()

    print("\n========================================")
    print("       MULTI VIEW UNIVERSE")
    print("========================================")
    print(f"Website: http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop the server.")
    print("========================================\n")

    try:
        app.run(
            host="0.0.0.0",
            port=PORT,
            debug=False,
            threaded=True,
            use_reloader=False
        )

    except KeyboardInterrupt:
        print("\nStopping Multi View Universe...")

    finally:
        cleanup_gpio()
