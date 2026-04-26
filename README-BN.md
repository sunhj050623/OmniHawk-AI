<div align="center">

# 🦅 OmniHawk AI
### টিম ও এজেন্টের জন্য গ্লোবাল AI ইন্টেলিজেন্স রাডার

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

## ✨ সারসংক্ষেপ
OmniHawk AI এক প্ল্যাটফর্মে AI paper ট্র্যাকিং, মডেল রিলিজ, AI ফাইন্যান্স, ইন্ডাস্ট্রি রিপোর্ট, নীতি ও নিরাপত্তা আপডেট, এবং ওপেন-সোর্স ডেভেলপার সিগন্যাল একত্র করে।

মূল ফ্লো: fetch -> dedupe -> analyze -> subscribe -> push.

## 🔭 ছয়টি স্বতন্ত্র পেজ
1. AI Paper Radar
2. AI Frontier Radar
3. AI Finance
4. AI Industry Reports
5. AI Policy & Safety
6. AI OSS & Dev Signals

প্রতিটি পেজের আলাদা সেটিংস, ফিল্টার ও সাবস্ক্রিপশন রয়েছে।

## 🚀 কুইক স্টার্ট
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

## 📡 নোটিফিকেশন চ্যানেল
`feishu`, `wework`, `wechat`, `telegram`, `dingtalk`, `ntfy`, `bark`, `slack`, `email`

## 🤖 MCP + CLI
- MCP: এজেন্ট ইন্টিগ্রেশনের জন্য স্ট্যান্ডার্ড ইন্টারফেস।
- CLI: লোকাল অটোমেশন ও স্ক্রিপ্ট রান (`omnihawk-ai-cli`)।

## 📄 লাইসেন্স
এই প্রোজেক্টটি [MIT License](LICENSE) লাইসেন্সের অধীনে।

## 🙏 রেফারেন্স
[TrendRadar](https://github.com/sansan0/TrendRadar) থেকে অনুপ্রাণিত।
