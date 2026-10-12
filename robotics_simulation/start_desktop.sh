export WEBKIT_DISABLE_COMPOSITING_MODE=0
epiphany http://localhost:8080 &
APP_BIN="epiphany-browser"
sudo pkill -9 -f "${APP_BIN}"
export WEBKIT_FORCE_COMPOSITING_MODE=1
export WEBKIT_DISABLE_COMPOSITING_MODE=0
TARGET_URL="http://localhost:8080"
${APP_BIN} "${TARGET_URL}"