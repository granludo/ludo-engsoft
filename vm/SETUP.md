# Course VM Setup

The course uses a standardized **Ubuntu Server 24.04 LTS** VM to ensure everyone works in the same environment. The VM is **terminal-only** (no GUI). You edit code on your host machine (Cursor, VS Code) via a shared folder, and execute everything in the VM terminal.

**If you got an OVA image from the course → jump to [Using the VM](#using-the-vm).** The "Building the VM" section is reference material; instructors do that once and distribute the OVA.

---

## Using the VM

### 1. Import the OVA into VirtualBox

[VirtualBox](https://www.virtualbox.org/) is free and works on Mac, Windows, Linux. Install it first.

- VirtualBox → **File → Import Appliance** → select the `.ova` file → next → finish.
- Boot the VM. Login: `student` / `student` (change the password on first boot: `passwd`).

### 2. SSH from your host terminal (recommended)

The VirtualBox console window is awkward (no copy-paste, tiny font). Use SSH instead — same VM, your real terminal:

```bash
ssh -p 2222 student@localhost
```

The OVA ships with `host-2222 → guest-22` port forwarding pre-configured.

### 3. Mount a shared folder for host-side editing

This is how you edit code on your host (in Cursor / VS Code) and run it in the VM.

**On the host:** VirtualBox → VM Settings → **Shared Folders** → add a host folder (e.g., `~/course-workspace`), name it **`workspace`**, check **Auto-mount** and **Make Permanent**.

**Inside the VM:** the folder appears at `/workspace`. If not:

```bash
sudo mount -t vboxsf workspace /workspace
# Or persistently:
echo 'workspace /workspace vboxsf defaults,uid=1000,gid=1000 0 0' | sudo tee -a /etc/fstab
```

Then open `~/course-workspace` on your host in Cursor / VS Code. **Edit on the host, run in the VM.**

### 4. Snapshot a clean baseline

Before doing real work, take a VirtualBox snapshot named **`week-01-clean`**. If something goes wrong later in the term, restore to this snapshot.

VirtualBox → **Snapshots** → Take Snapshot → name it.

---

## What's pre-installed (BSC tool baseline)

The OVA you receive has:

**System:**
- Ubuntu Server 24.04 LTS, headless (no GUI).
- `python3` + `python3-venv` + `python3-dev`, `git`, `curl`, `wget`, `jq`, `tree`, `htop`, `build-essential`.

**Python tooling:**
- [`uv`](https://docs.astral.sh/uv/) — fast Python env + package manager. This is the course default.
- [`llm`](https://llm.datasette.io/) (Simon Willison) — CLI for fast LLM tests and scripting; also used in agent work later in the course.
- [`gh`](https://cli.github.com/) — GitHub CLI for repo creation and pushing deliverables.
- [`opencode`](https://opencode.ai/) — agentic coding CLI used in Weeks 3+.

**Python packages** (pre-installed under user site-packages):
- `transformers`, `tokenizers` — Hugging Face stack for Week 1 exercises.
- `torch` (CPU build) — needed by `transformers`; the VM has no GPU.
- `openai`, `anthropic` — API client libraries.
- `pydantic`, `requests` — general utilities.

**Pre-cached models** (so first runs are fast):
- `gpt2` and `bert-base-uncased` tokenizers + GPT-2 124M model weights.

---

## Building the VM (instructors only — reference)

You don't do this; we do it once and distribute the OVA. Reference for whoever maintains the image.

### Base installation

1. Download Ubuntu Server 24.04 LTS ISO from [ubuntu.com](https://ubuntu.com/download/server).
2. New VM in VirtualBox:
   - Name: `bsc-agents-2026`
   - Type: Linux / Ubuntu (64-bit)
   - RAM: **4096 MB** (minimum 2048).
   - Disk: **40 GB** dynamically allocated (model weights + libraries).
   - Network: **NAT with port forwarding**: host `2222` → guest `22` (SSH).
3. Install Ubuntu Server from ISO. **Minimal installation, no desktop.** User: `student` / `student`. Enable **OpenSSH server** during install.
4. Install VirtualBox Guest Additions (for shared folders):
   ```bash
   sudo apt-get update && sudo apt-get install -y build-essential dkms linux-headers-$(uname -r)
   # Insert Guest Additions CD via VirtualBox menu, then:
   sudo mount /dev/cdrom /mnt
   sudo /mnt/VBoxLinuxAdditions.run
   sudo usermod -aG vboxsf student
   ```

### Install the BSC tool baseline

```bash
# System
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
  python3 python3-pip python3-venv python3-dev \
  git curl wget jq tree htop build-essential

# uv (Astral)
curl -LsSf https://astral.sh/uv/install.sh | sh

# gh (GitHub CLI)
(type -p wget >/dev/null && sudo mkdir -p -m 755 /etc/apt/keyrings && \
 wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
 sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg >/dev/null && \
 echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
 sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null && \
 sudo apt-get update && sudo apt-get install -y gh)

# opencode (agentic coding CLI)
curl -fsSL https://opencode.ai/install | bash

# Python stack
pip3 install --user \
  llm \
  transformers tokenizers \
  torch --index-url https://download.pytorch.org/whl/cpu \
  openai anthropic \
  pydantic requests

# PATH (user installs)
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc

# Git defaults
git config --global init.defaultBranch main
git config --global core.editor nano

# Pre-cache tokenizers + GPT-2 weights
python3 -c "
from transformers import pipeline, AutoTokenizer
pipeline('text-generation', model='gpt2')
AutoTokenizer.from_pretrained('gpt2')
AutoTokenizer.from_pretrained('bert-base-uncased')
print('models cached')
"
```

### Shared folder + SSH

```bash
sudo mkdir -p /workspace
sudo chown student:student /workspace
# Auto-mount (assuming the shared folder is named "workspace" in VBox settings)
echo 'workspace /workspace vboxsf defaults,uid=1000,gid=1000 0 0' | sudo tee -a /etc/fstab
```

SSH is on by default. The OVA inherits the port-forwarding rule from VBox settings.

### Export the OVA

VirtualBox → **File → Export Appliance** → OVA format. Expected size ~5–6 GB after pre-caching.

**Test on Mac + Windows + Linux** before distributing. Distribute via the LMS or a download link.

---

## Software added in later weeks

The OVA starts with the Week 1 baseline. Students install additional tools as needed in later weeks (RAG / vector DBs / MCP / Docker — week-specific READMEs spell it out).

---

## Troubleshooting

### VM won't start — "VT-x is not available"
Enable virtualization in your BIOS (Intel VT-x or AMD-V). On Windows, may need to disable Hyper-V:
```
bcdedit /set hypervisorlaunchtype off
```
(then reboot)

### Shared folder not visible in the VM
```bash
lsmod | grep vboxsf       # Guest Additions installed?
mount | grep vboxsf       # currently mounted?
sudo mount -t vboxsf workspace /workspace    # manual mount
groups student            # should include "vboxsf"
```

### No internet in the VM
- VirtualBox → Settings → Network → Attached to: **NAT**.
- Inside the VM: `ping 8.8.8.8`. If DNS fails:
  ```bash
  echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
  ```

### SSH connection refused
- Check the service: `sudo systemctl status ssh`.
- Check port forwarding in VirtualBox: Settings → Network → Advanced → Port Forwarding. Rule: Host `2222` → Guest `22`.

### "Disk full" errors
```bash
df -h
du -sh ~/.cache/huggingface     # the HF model cache, biggest culprit
pip3 cache purge
```
If truly full, the VM disk needs resizing (instructor reference).

---

## Can't run a VM at all?

If your laptop won't run VirtualBox (locked-down corporate laptop, old hardware, conflicting hypervisor), the sanctioned fallback is **WSL2 on Windows** or **native Ubuntu on Linux**. Same commands, same exercises. Mac users without VirtualBox: native macOS Python via `uv` also works for everything except the shared-folder workflow — you simply edit and run on the same machine.
