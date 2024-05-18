<p align="center">
    <img src="https://github.com/praetor29/personalgpt/blob/6a1fc71769a8becffb83503a1b63a2364b460828/static/media/dark.c195d63d87dd975ae38d.png" width=50% height=50%>
</p>

<p align="center">
    <i>The path to near-perfect digital cloning. Fully open source.</i>
    <br>
    <br>
  </p>
  
<p align="center">
<img alt="Python" src="https://img.shields.io/badge/Python-3.12.3-3776ab?logo=python"> <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-1.30.1-white?logo=openai">
<img alt="Pycord" src="https://img.shields.io/badge/discord.py-2.3.2-5865f2?logo=discord">
</p>

<p align="center">
  <img src="https://discordapp.com/api/guilds/1128413164623634434/widget.png?style=banner2" alt="Discord Banner 2"/>
</p>

## About
PersonalGPT is a cutting-edge project that leverages state-of-the-art AI to create an immersive digital clone. It offers a unique and interactive experience across various mediums, harnessing advanced multimodal image recognition and text generation capabilities.

### Core Features:
- **GPT-4o Support:** OpenAI's most advanced, multimodal flagship model that’s cheaper and faster than GPT-4 Turbo. It supports native vision with images, offering top-tier performance and efficiency.
- **Configurable Memory:** Features a robust `aiocache` queue, applying a **First In, First Out** (FIFO) strategy for consistent and lossless data management.
- **Fully Asynchronous Processing:** Efficiently handles high volumes of concurrent messages, maintaining seamless performance.
- **Customizable Parameters:** Provides comprehensive customization through the [Discord Developer Portal](https://discord.com/developers/applications) and an intuitive configuration file.

> [!NOTE]
> The `active-dev` branch is focused on active feature development.

## 🧪 Getting Started (Beta)
To get started with PersonalGPT, follow these steps:

1. **Download the repository**
    - Clone using Git:
    ```bash
    git clone https://github.com/praetor29/personalgpt.git
    ```
    - Or download the [latest archive.](https://github.com/praetor29/personalgpt/archive/refs/heads/main.zip)
    
2. **Modify configuration files**  
    Update `config.yaml` and `prompts.yaml` with your settings.

3. **Add API tokens**  
    Add your [OpenAI token](https://platform.openai.com/api-keys) and [Discord App token](https://discord.com/developers/docs/quick-start/getting-started) to `.env.example`, then rename the file to `.env`.

4. **Install Python**  
    Ensure you have [Python 3.12.3](https://www.python.org/downloads/release/python-3123/) installed on your system.

   > [!TIP]
   > Using a virtual environment like [Miniconda](https://docs.anaconda.com/free/miniconda/index.html) makes managing dependencies easier and less messy. 

5. **Install required packages**  
    Run the following command to install the necessary Python packages:
    ```bash
    # navigate to the project directory
    cd personalgpt
    # install all requirements
    pip install -r requirements.txt
    ```

6. **Run the application**
   
   This runs PersonalGPT in the *foreground*.
    - Launch script:
    ```bash
    # navigate to project directory
    cd personalgpt
    # make launch script executable (first time)
    chmod +x ./personalgpt.sh
    # run launch script
    ./personalgpt.sh
    ```
    - Directly:
    ```bash
    python -m src
    ```

7. **Run in the background (Linux)**  
    To run PersonalGPT in the *background*, use [nohup](https://en.wikipedia.org/wiki/Nohup):
    ```bash
    nohup <launch script or python command> &
    ```

---

## Contributions
### ⚡ Development
```
praetor29
```
### ✨ Beta Testing
```
yumeshu, jinzou, goldiereal, vamp1044, ambasinghhh
```

## 🔗 Useful Links
- [Project Webpage](https://praetor29.github.io/personalgpt) (not updated to v3.0)
- [Join our Discord](https://discord.gg/9EA2mrG3ZT)

## 🌐 Core Technologies
PersonalGPT utilizes several open-source libraries and technologies:
- **[discord.py](https://github.com/Rapptz/discord.py)**: A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.
- **[openai-python](https://github.com/openai/openai-python)**: Official OpenAI library for AI interaction. SDK v1 compliant.
- **[aiocache](https://github.com/aio-libs/aiocache)**: Asyncio cache supporting multiple backends (memory, redis and memcached).

> [!NOTE]
> Support for OpenAI's [fine-tuning](https://platform.openai.com/docs/guides/fine-tuning), ElevenLabs Voice Cloning/Discord [voice support](https://github.com/praetor29/personalgpt/tree/5991d9f0708637a1057bb556e3950d59b657d494/src/voice) were dropped in v3.0. Voice support may be re-implemented in a later release.

## ⚖️ License
This project is licensed under the [GNU General Public License v3.0](https://github.com/praetor29/personalgpt/blob/main/LICENSE).

