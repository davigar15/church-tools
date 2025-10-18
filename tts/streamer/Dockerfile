FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends icecast2 liquidsoap netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Fix Icecast to listen on all interfaces
RUN sed -i 's|<hostname>localhost</hostname>|<hostname>0.0.0.0</hostname>|' /etc/icecast2/icecast.xml \
 && sed -i 's|<!-- <bind-address>127.0.0.1</bind-address> -->|<bind-address>0.0.0.0</bind-address>|' /etc/icecast2/icecast.xml \
 && sed -i 's|<authentication>|<authentication><admin-user>admin</admin-user><admin-password>hackme</admin-password>|' /etc/icecast2/icecast.xml

# --- Entrypoint that generates Liquidsoap config and starts services ---
COPY --chmod=755 <<'EOF' /entrypoint.sh
#!/bin/bash
set -e

AUDIO_DIR="/app/audio"
TMP_SCRIPT="/tmp/generated.liq"
BACKGROUND="$AUDIO_DIR/background/background.mp3"

echo "# Auto-generated Liquidsoap configuration" > "$TMP_SCRIPT"
echo 'settings.init.allow_root.set(true)' >> "$TMP_SCRIPT"
echo 'set("log.stdout", true)' >> "$TMP_SCRIPT"
echo 'set("log.level", 3)' >> "$TMP_SCRIPT"
echo 'set("server.telnet", true)' >> "$TMP_SCRIPT"
echo 'set("server.telnet.port", 1234)' >> "$TMP_SCRIPT"
echo 'set("server.telnet.bind_addr", "0.0.0.0")' >> "$TMP_SCRIPT"

# ✅ define the background source BEFORE the loop
if [ -f "$BACKGROUND" ]; then
  echo "background = single(\"$BACKGROUND\")" >> "$TMP_SCRIPT"
else
  echo "Background file not found at $BACKGROUND"
  exit 1
fi

for file in "$AUDIO_DIR"/*.mp3; do
  [ -e "$file" ] || continue
  name=$(basename "$file" .mp3)
  echo "Creating stream for: $name ($file)"

  echo "track_$name = request.queue(id=\"track_$name\")" >> "$TMP_SCRIPT"
  echo "source_$name = fallback(track_sensitive=false, [track_$name, background])" >> "$TMP_SCRIPT"
  # echo "source_$name = fallback([track_$name, background])" >> "$TMP_SCRIPT"
  echo "output.icecast(%mp3, mount=\"/$name\", host=\"localhost\", port=8000, password=\"hackme\", mksafe(source_$name))" >> "$TMP_SCRIPT"
done

service icecast2 start
exec liquidsoap "$TMP_SCRIPT"
EOF

# --- Helper script to play all matching MP3s safely ---
COPY --chmod=755 <<'EOF' /usr/local/bin/play_all

#!/bin/bash
AUDIO_DIR="/app/audio"
HOST="localhost"
PORT="1234"

for file in "$AUDIO_DIR"/*.mp3; do
  [ -e "$file" ] || continue
  name=$(basename "$file" .mp3)
  cmd="track_${name}.push /app/audio/${name}.mp3"
  echo "Pushing track: $name"
  printf "%s\nquit\n" "$cmd" | nc "$HOST" "$PORT" >/dev/null 2>&1 && \
    echo "✅ Pushed $name" || echo "⚠️ Failed to push $name"
done
EOF

WORKDIR /app
VOLUME ["/app/audio"]

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
