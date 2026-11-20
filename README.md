# Mayaboti Agent Harness — Editable Source for Koyeb & BotKeep

এই ফোল্ডারটি (`mayaboti-koyeb/`) ওপেন-সোর্স `MIT License` এজেন্ট হারনেস কোডকে **Mayaboti** ব্র্যান্ডে রূপান্তর করে [`src/`](./src) ডিরেক্টরিতে সেটআপ করা হয়েছে—তুমি চাইলে নিজের মতো যেকোনো ফাইল এডিট করতে পারবে।

---

## কোন ফোল্ডারে কী এডিট করবে?
- **`src/mayaboti/agent/`** — এজেন্ট লুপ, সিস্টেম প্রম্পট, মেমোরি ও টুল ব্যবহার।
- **`src/mayaboti/agent/tools/`** — বিল্ট-ইন টুলস (ফাইল, শেল, ওয়েব সার্চ ইত্যাদি) বা নিজের নতুন টুল যোগ করা।
- **`src/mayaboti/channels/`** — Telegram, WebSocket/WebUI ও অন্যান্য মেসেজিং চ্যানেল।
- **`src/mayaboti/skills/`** — বিল্ট-ইন এজেন্ট স্কিলসমূহ (`mayaboti-document` সহ)।
- **`src/webui/`** — ব্রাউজার WebUI (React/Vite); এডিট করলে `Dockerfile`-এর মাল্টি-স্টেজ বিল্ড অটোমেটিক বিল্ড করে নেবে।

> **BotKeep-এ এডিট করা কোড সরাসরি চালাতে:** `requirements.txt`-এ `-e ./src` দেওয়া আছে, তাই `src/mayaboti/`-এ কিছু এডিট করলে পুনরায় ইনস্টল ছাড়াই রিস্টার্টে কাজ করবে।

---

## গুরুত্বপূর্ণ সতর্কতা
- তোমার বর্তমান **Mayaboti AI** (`@Ariferex_bot`) বটের Telegram টোকেন এখানে **ব্যবহার করবে না**—`@BotFather` থেকে আলাদা একটি **নতুন Bot Token** তৈরি করে নাও (নাহলে দুটি সার্ভিসের মধ্যে Telegram Polling Conflict হবে)।
- `TELEGRAM_ALLOW_FROM`-এ অবশ্যই তোমার নিজের numeric Telegram User ID দেবে, যাতে অন্য কেউ এজেন্টের শেল/ফাইল টুল চালাতে না পারে।

---

## ১. Koyeb-এ ডিপ্লয় করার নিয়ম
1. `mayaboti-koyeb/` ফোল্ডারটি একটি নতুন GitHub রিপোজিটরিতে পুশ করো (অথবা Koyeb-এ Work Directory হিসেবে `mayaboti-koyeb` সিলেক্ট করো)।
2. Build Method: **Dockerfile** (ফাইলের `Dockerfile`-এ ২-স্টেজ বিল্ডে WebUI সহ সব বিল্ড হবে)।
3. Port: **`8080`** (`channels.websocket` সরাসরি `0.0.0.0:$PORT`-এ WebUI সার্ভ করে)।
4. **Environment Variables** সেট করো:
   - `GROQ_API_KEY`: তোমার Groq API কী
   - `OPENROUTER_API_KEY`: তোমার OpenRouter API কী
   - `MAYABOTI_PROVIDER`: `groq`
   - `MAYABOTI_MODEL`: `qwen/qwen3.8-27b` (অথবা `openrouter/free`)
   - `TELEGRAM_BOT_TOKEN`: `@BotFather` থেকে নেওয়া **নতুন** বট টোকেন
   - `TELEGRAM_ALLOW_FROM`: তোমার Telegram numeric User ID
   - `MAYABOTI_WEB_TOKEN`: নিজের পছন্দের শক্তিশালী WebUI পাসওয়ার্ড/টোকেন
5. **২৪/৭ অনলাইন রাখতে:** UptimeRobot দিয়ে প্রতি ১০–১৫ মিনিটে তোমার Koyeb অ্যাপ URL পিং করো।

---

## ২. BotKeep (Python 2GB RAM) সার্ভারে চালানোর নিয়ম
1. `mayaboti-koyeb/` ফোল্ডারের সব ফাইল (`requirements.txt`, `start.py`, `src/`) BotKeep সার্ভারে আপলোড করো।
2. Environment Variables (অথবা `.env` ফাইলে `.env.example` দেখে) উপরের কীগুলো সেট করো।
3. Startup Command সেট করো:
   ```bash
   python start.py
   ```
   *(Server port হিসেবে BotKeep-এর দেওয়া পোর্ট `PORT` ভেরিয়েবলে বসালেই WebUI সেই পোর্টে চালু হবে।)*
