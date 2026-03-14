# Installation de LibreLector

## Via le paquet .deb (recommandé)
```bash
# Télécharger la dernière release
wget https://github.com/nouhailler/LibreLector/releases/latest/download/librelector_0.2.0_amd64.deb

# Installer
sudo dpkg -i librelector_0.2.0_amd64.deb

# Corriger les dépendances manquantes si besoin
sudo apt install -f
```

## Première utilisation — voix française Piper
```bash
mkdir -p ~/.local/share/LibreLector/voices
cd ~/.local/share/LibreLector/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json

# Configurer
mkdir -p ~/.local/share/LibreLector
cat > ~/.local/share/LibreLector/settings.json << 'JSON'
{
  "tts_engine": "piper",
  "piper_model": "/home/TON_USER/.local/share/LibreLector/voices/fr_FR-siwis-medium.onnx",
  "language": "fr"
}
JSON
```

## Lancer
```bash
librelector
```
