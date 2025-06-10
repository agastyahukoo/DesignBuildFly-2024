### Quick-Start Checklist

Follow these 15 bite-size steps and you’ll have two Pi cameras streaming into the new **Drone Ground Station Pro** page in about 25 minutes—even if you’ve never touched Jitsi or a Raspberry Pi before.

---

#### 1 · What to have on the desk

* **Raspberry Pi 5** (4 GB +), 27 W USB-C power, 32 GB micro-SD
* **Two cameras** — USB webcams *or* Pi CSI/UCSE ribbon cams
* **Network** — Wi-Fi is fine for tabletop tests; 4 G dongle later
* **Laptop/desktop** with Chrome/Edge/Firefox (ground station)
* Internet account with **8×8 JaaS** (fastest Jitsi option)

---

### A · Prepare the back-end (once)

| Step | Command / click                                   |
| ---- | ------------------------------------------------- |
| 1    | Sign up at **jaas.8x8.vc** → **Create App**       |
| 2    | Copy **App ID** and **App Secret**                |
| 3    | In “Security” turn **Lobby OFF** and **JWT ONLY** |

> *Why JaaS?* No servers to install, HTTPS and TURN already there.

---

### B · Mint one test JWT (60 s)

On **any** machine with Node 18 +:

```bash
npm i -g jsonwebtoken-cli
jwt sign --alg HS256 --secret 'APP_SECRET' \
'{"iss":"APP_ID","aud":"jitsi","room":"drone-demo","exp":'$((`date +%s`+86400))'}'
```

Copy the long string that appears—that is your **token**.
(You can reuse the very same token on the Pi and on the laptop.)

---

### C · Flash and prep the Pi 5 (10 min)

```bash
# 1. Install OS
# – Flash “Raspberry Pi OS 64-bit (Bookworm)” with Raspberry Pi Imager
# – Boot once, go through the wizard

# 2. Enable cameras & give GPU 256 MB
sudo raspi-config          # Interface Options → Camera → Enable
sudo raspi-config          # Performance → GPU Memory → 256

# 3. Update and install Chromium
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y chromium-browser
```

Plug both cameras → `ls /dev/video*` should show `video0` and `video1`.

---

### D · Start streaming from the Pi (2 min)

Open an SSH terminal (or the Pi desktop) and run **once per camera**:

```bash
chromium-browser --no-sandbox \
  --autoplay-policy=no-user-gesture-required \
  "https://8x8.vc/drone-demo?jwt=TOKEN#config.prejoinPageEnabled=false&config.startWithAudioMuted=true" &
```

* For the **second** instance add `--user-data-dir=/tmp/cam2`.
* Each Chromium tab automatically publishes one webcam to Jitsi.

---

### E · Set up the ground-station page (2 min)

1. Copy the big **Drone Ground Station Pro** HTML you pasted above into a file called `viewer.html`.
2. Double-click `viewer.html` on the laptop—page opens instantly (no server needed).

---

### F · Connect (30 s)

| Field on the Home screen | What to type                      |
| ------------------------ | --------------------------------- |
| **Domain**               | `8x8.vc`                          |
| **Room**                 | `drone-demo`                      |
| **JWT Token**            | *(paste the token you generated)* |

Click **Connect** → the login card fades, a black dashboard appears, then both camera feeds pop in.
No Jitsi watermark, no toolbar, just your own UI.

---

### G · That’s it—fly!

* **ESC / ⛶** buttons toggle full-screen per feed.
* Gear icon lets you pick resolution/bit-rate and turn on auto-reconnect.
* Press <kbd>Ctrl</kbd> + <kbd>\`</kbd> to open the live debug overlay.

If you later switch to a 4 G dongle, nothing changes—Chromium will ICE-reconnect over the mobile link automatically.

Happy streaming!
