<div align="center">

# 🦅 OmniHawk AI
### टीमों और एजेंट्स के लिए वैश्विक AI इंटेलिजेंस रडार

</div>

## Language Versions (Top 10)
- [Chinese (Simplified)](README.md)
- [English](README-EN.md)
- [Hindi](README-HI.md)
- [Spanish](README-ES.md)
- [Arabic](README-AR.md)
- [French](README-FR.md)
- [Portuguese](README-PT.md)
- [Bengali](README-BN.md)
- [Japanese](README-JA.md)
- [Korean](README-KO.md)

## ✨ सारांश
OmniHawk AI एक ही प्लेटफ़ॉर्म पर AI पेपर ट्रैकिंग, मॉडल रिलीज़, AI वित्तीय जानकारी, इंडस्ट्री रिपोर्ट, नीति और सुरक्षा अपडेट, और ओपन-सोर्स डेवलपर सिग्नल उपलब्ध कराता है।

मुख्य कार्यप्रवाह: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 छह स्वतंत्र पेज
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

हर पेज की सेटिंग, फ़िल्टर और सब्सक्रिप्शन स्वतंत्र हैं।

## 🚀 क्विक स्टार्ट
```bash
uv sync --locked
omnihawk-ai
python -m omnihawk_ai.web.panel_server --port 8080 --output-dir output
omnihawk-ai-mcp --transport http --host 0.0.0.0 --port 3333
```

## 🐳 Docker
```bash
docker compose -f docker/docker-compose.yml up -d --build
docker compose -f docker/docker-compose.yml logs -f
docker compose -f docker/docker-compose.yml down
```

## 📡 नोटिफिकेशन चैनल
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: एजेंट इंटीग्रेशन के लिए मानक इंटरफ़ेस।
- CLI: लोकल ऑटोमेशन और स्क्रिप्ट रन (`omnihawk-ai-cli`)।

## 📄 लाइसेंस
यह प्रोजेक्ट [MIT License](LICENSE) के अंतर्गत है।

## 🙏 संदर्भ
[TrendRadar](https://github.com/sansan0/TrendRadar) से प्रेरित।
