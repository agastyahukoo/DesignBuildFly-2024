Below is a **check-list you can hand to a teammate who has never touched a Pi or Jitsi before**.
Follow it line-by-line and you will be watching both drone cameras on the ground-station screen in < 30 min.

---

## 0 . What you need on the bench

| Item                                                              | Notes                                                                                                                                      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Raspberry Pi 5** (4 GB+), USB-C PSU, micro-SD (32 GB)           | Pi 5 needs the new 27 W supply or a clean 5 V 3 A bench source.                                                                            |
| **2 × cameras**                                                   | Any two USB UVC webcams *or* two Pi CSI/UCSE cams (e.g. Cam Module 3).                                                                     |
| **4 G/LTE dongle or Wi-Fi**                                       | For a desk test Wi-Fi is fine.                                                                                                             |
| **Laptop/desktop** (ground station)                               | Windows 10+/macOS/Linux with Chrome/Edge/Firefox.                                                                                          |
| **Jitsi server**                                                  | • Fast track: sign up for **8×8 JaaS** free tier.<br>• DIY: run `docker-compose` with the official `jitsi/jitsi-meet` stack on a cloud VM. |
| The **single-file HTML** prototype you got in the previous answer | Put it somewhere you can double-click.                                                                                                     |

---

## 1 . Prepare the Jitsi back end (once)

### A. If you use **8×8 JaaS (recommended for demos)**

1. Sign up at [jaas.8x8.vc](https://jaas.8x8.vc) → “Create app”.
2. Copy the **App ID** and **Secret**.
3. In “Security” turn on **JWT only** and **Lobby off**.

### B. If you self-host (Docker way)

1. On any Ubuntu 22.04/24.04 VPS with a public IPv4 run:

   ```bash
   git clone https://github.com/jitsi/docker-jitsi-meet && cd docker-jitsi-meet
   cp env.example .env
   # edit .env → set PUBLIC_URL, ENABLE_AUTH=1, ENABLE_GUESTS=0
   docker compose up -d
   ```
2. Add DNS `A` record `meet.example.com` → your VPS IP and point a TLS proxy such as **Caddy** or **Traefik** at `docker-jitsi-meet/web`.

> **Why JWT?** It skips any login or pre-join screens so your app looks 100 % custom.

---

## 2 . Mint a test JWT (30-sec CLI)

On any machine with Node 18+:

```bash
npm install -g jsonwebtoken-cli
jwt sign --alg HS256 --secret '<YOUR_SECRET>' \
'{"iss":"<YOUR_APP_ID>","aud":"jitsi","room":"drone-demo","exp":'$((`date +%s`+3600))'}'
```

*Copy the resulting long string* — that is the **token** you will paste into the ground-station GUI.
(Repeat the same command on the Pi so the drone also has a token; they can be identical.)

---

## 3 . Flash & update the Pi

1. Download **Raspberry Pi OS 64-bit (Bookworm, April 2025)** → flash with **Raspberry Pi Imager**.
2. First boot:

   ```bash
   sudo raspi-config   # → Interface Options → Camera → Enable
   sudo raspi-config   # → Performance → GPU Memory → 256
   ```
3. Update & install Chromium:

   ```bash
   sudo apt update && sudo apt full-upgrade -y
   sudo apt install -y chromium-browser
   ```
4. Plug in both cameras (`ls /dev/video*` should show `video0` and `video1`).

---

## 4 . Launch the streams from the Pi (one line per cam)

Open an **SSH** shell (or the Pi’s own terminal) and run:

```bash
chromium-browser --no-sandbox --autoplay-policy=no-user-gesture-required \
"https://meet.example.com/drone-demo?jwt=<PASTE_TOKEN>#config.prejoinPageEnabled=false&config.startWithAudioMuted=true&config.startSilent=true" &
```

* Repeat once more, adding `--user-data-dir=/tmp/alt` so a second Chromium instance grabs the second camera.

Chromium auto-publishes the default webcam; if both instances start you now have **two remote tracks** in the Jitsi room.

---

## 5 . Start the ground-station viewer

1. Copy the earlier **`drone-viewer.html`** to your laptop.

2. Double-click it (or open with Chrome).

3. Fill in:

   | Field         | Value                                 |
   | ------------- | ------------------------------------- |
   | **Domain**    | `meet.example.com` (or your JaaS URL) |
   | **Room**      | `drone-demo`                          |
   | **JWT Token** | the long string from step 2           |

4. Press **Connect** → the login panel fades, the black dashboard appears, and after 2-3 s both video panes light up.

---

## 6 . What you should see

* Left pane = first camera.
* Right pane = second camera.
* No toolbars, chat buttons, or Jitsi branding anywhere.

If either feed is blank check:

* The Pi terminal: WebRTC ICE failures print in red.
* Laptop network: your browser must reach `wss://<domain>/xmpp-websocket` (port 443).
* **CTRL + SHIFT + I** in the viewer → Console shows `TRACK_ADDED` events for each camera.

---

## 7 . Moving from desk to drone

| Replace…                 | With…                                                                                    |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| Wi-Fi                    | Your **USB 4 G modem** (`ppp0` or `wwan0`). Latency will rise to \~200 ms.               |
| Two USB cams             | Two CSI/UCSE ribbon cams; Chromium will list them as `/base` and `/extra`.               |
| Manual token             | A tiny Python script that fetches a fresh JWT via your backend API before each flight.   |
| Double click viewer.html | Package it into **Electron** using `electron-builder --dir` and distribute an installer. |

---

### End-to-end test complete 🎉

You now have a repeatable recipe: flash Pi → install Chromium → run two browser instances into a JWT-protected Jitsi room → open the single-file viewer on the ground station.
From here you can embed the same HTML into Electron, add telemetry overlays, or swap Chromium for an `ffmpeg → Jitsi Ingress` pipeline without changing anything in the viewer UI.
