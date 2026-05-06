# 🚀 Niscahya Chatbot API - Frontend Integration Guide

Panduan lengkap untuk mengintegrasikan chatbot Niscahya ke website utama Anda.

## 📁 File Structure

```
frontend/
├── niscahya-chatbot.js    # API Client Library
├── demo.html             # Demo Implementation
└── README.md             # This file
```

## 🔧 Quick Setup

### 1. Include API Client

```html
<!-- Include di <head> atau sebelum </body> -->
<script src="niscahya-chatbot.js"></script>
```

### 2. Initialize Chatbot

```javascript
// Initialize dengan URL API
const chatbot = new NiscahyaChatbot('http://localhost:8000');

// Atau dengan custom session ID
const chatbot = new NiscahyaChatbot('http://localhost:8000', 'user_session_123');
```

### 3. Send Message

```javascript
// Basic chat
const response = await chatbot.sendMessage('Halo, apa produk PJUTS tersedia?');

if (response.success) {
    console.log('Bot:', response.answer);
    console.log('Intent:', response.intent);
    console.log('Product:', response.product);
} else {
    console.error('Error:', response.error);
}
```

## 📚 API Methods

### `sendMessage(message)`

Kirim pesan ke chatbot.

```javascript
const response = await chatbot.sendMessage('Saya butuh lampu taman');

Response format:
{
    success: true,
    answer: "✨ **Rekomendasi PJUTS...**",
    intent: "product_recommendation",
    product: { name: "PJUTS 40W", watt: "40W", battery: "20Ah" },
    sessionId: "session_123"
}
```

### `createLead(leadData)`

Buat lead/contact baru.

```javascript
const leadData = {
    name: "John Doe",
    whatsapp: "+6281234567890",
    project_needs: "Butuh PJUTS untuk area parkir"
};

const response = await chatbot.createLead(leadData);
```

### `getHistory(limit)`

Ambil riwayat chat.

```javascript
const history = await chatbot.getHistory(10);
// Returns array of chat messages
```

### `clearHistory()`

Hapus riwayat chat untuk session ini.

```javascript
await chatbot.clearHistory();
```

### `uploadDocuments(files)`

Upload dokumen knowledge base (untuk admin).

```javascript
const fileInput = document.getElementById('fileInput');
const response = await chatbot.uploadDocuments(fileInput.files);
```

### `getStatus()`

Check status API.

```javascript
const status = await chatbot.getStatus();
// Returns API info if online
```

## 🎨 HTML Integration Example

### Basic Chat Widget

```html
<div id="niscahya-chat-widget">
    <div id="chat-messages"></div>
    <input type="text" id="message-input" placeholder="Tanya tentang PJUTS...">
    <button onclick="sendMessage()">Kirim</button>
</div>

<script src="niscahya-chatbot.js"></script>
<script>
const chatbot = new NiscahyaChatbot('http://localhost:8000');

async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    input.value = '';

    // Get bot response
    const response = await chatbot.sendMessage(message);
    addMessage(response.answer, 'bot');
}

function addMessage(text, type) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = text;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}
</script>
```

### Floating Chat Button

```html
<!-- Floating chat button -->
<div id="chat-button" onclick="toggleChat()">
    💬 Chat
</div>

<!-- Chat modal -->
<div id="chat-modal" style="display: none;">
    <div id="chat-messages"></div>
    <input type="text" id="message-input" onkeypress="handleKeyPress(event)">
    <button onclick="sendMessage()">Kirim</button>
    <button onclick="toggleChat()">✕</button>
</div>

<script>
let chatbot = null;

function toggleChat() {
    const modal = document.getElementById('chat-modal');
    modal.style.display = modal.style.display === 'none' ? 'block' : 'none';

    if (!chatbot) {
        chatbot = new NiscahyaChatbot('http://localhost:8000');
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = '';

    const response = await chatbot.sendMessage(message);
    addMessage(response.answer, 'bot');
}

function addMessage(text, type) {
    const messages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = text.replace(/\n/g, '<br>');
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}
</script>

<style>
#chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #007bff;
    color: white;
    padding: 12px 20px;
    border-radius: 25px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

#chat-modal {
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    display: flex;
    flex-direction: column;
    z-index: 1000;
}

#chat-messages {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    border-bottom: 1px solid #eee;
}

.message {
    margin-bottom: 10px;
    padding: 8px 12px;
    border-radius: 15px;
    max-width: 80%;
}

.message.user {
    background: #007bff;
    color: white;
    margin-left: auto;
}

.message.bot {
    background: #f1f1f1;
    margin-right: auto;
}

#message-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 20px;
    margin: 10px;
}

button {
    padding: 8px 15px;
    margin: 10px;
    border: none;
    border-radius: 20px;
    cursor: pointer;
}
</style>
```

## 🔧 Advanced Configuration

### Custom API URL

```javascript
// Production URL
const chatbot = new NiscahyaChatbot('https://api.niscahya.com');

// Development URL
const chatbot = new NiscahyaChatbot('http://localhost:8000');
```

### Session Management

```javascript
// Use user ID as session
const userId = getCurrentUserId();
const chatbot = new NiscahyaChatbot('http://localhost:8000', `user_${userId}`);

// Or generate unique session per page visit
const sessionId = 'page_' + Date.now();
const chatbot = new NiscahyaChatbot('http://localhost:8000', sessionId);
```

### Error Handling

```javascript
try {
    const response = await chatbot.sendMessage(message);

    if (response.success) {
        displayMessage(response.answer, 'bot');
    } else {
        displayError(response.error);
    }
} catch (error) {
    displayError('Network error. Please check your connection.');
}
```

### Auto Lead Capture

```javascript
// Detect product recommendation intent
const response = await chatbot.sendMessage(message);

if (response.intent === 'product_recommendation') {
    // Show lead capture form
    showLeadForm();

    // Auto-create lead when user provides contact
    const leadData = getLeadFormData();
    await chatbot.createLead(leadData);
}
```

## 📊 Response Formatting

API response sudah diformat dengan baik untuk frontend:

### Product Recommendation
```
✨ **Rekomendasi PJUTS untuk Kebutuhan Anda**

🏆 **Rekomendasi #1: PJUTS 40W**
🎯 *Match Score: 100%*

📋 **Spesifikasi Produk:**
• ⚡ Daya: 40 Watt
• 🔋 Baterai: 20 Ah LiFePO4
• 📍 Cocok untuk: taman, jalan, area
• 💡 Durasi Penerangan: 6-8 jam

💡 **Mengapa cocok:** cocok untuk area taman, jalan, efisien untuk area terbatas

══════════════════════════════════════════════════
📞 **Hubungi Kami untuk Detail Lebih Lanjut**
• Diskusi spesifikasi lengkap
• Penawaran harga khusus
• Jadwal pemasangan
• Garansi & maintenance

💬 WhatsApp: [Nomor WhatsApp Anda]
```

### FAQ Response
```
💡 **Jawaban FAQ**

Harga PJUTS tergantung kapasitas watt dan spesifikasi. PJUTS 40W mulai dari Rp 3-4 juta...

❓ **Ada pertanyaan lain?**
Hubungi tim kami untuk info lebih detail!
```

## 🚀 Production Deployment

### 1. Update API URL
```javascript
// Change this line in your website
const chatbot = new NiscahyaChatbot('https://your-api-domain.com');
```

### 2. CORS Configuration
Pastikan API server mengizinkan domain website Anda:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourwebsite.com", "https://www.yourwebsite.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. SSL/HTTPS
Pastikan API menggunakan HTTPS di production.

### 4. Error Monitoring
```javascript
// Add error tracking
window.addEventListener('error', function(e) {
    // Send error to monitoring service
    console.error('Chatbot error:', e.error);
});
```

## 🐛 Troubleshooting

### API Not Connected
```javascript
// Check API status
const status = await chatbot.getStatus();
console.log('API Status:', status);
```

### CORS Error
- Pastikan `allow_origins` di API server includes domain website Anda
- Atau gunakan proxy jika perlu

### Session Issues
```javascript
// Clear session
await chatbot.clearHistory();
const newChatbot = new NiscahyaChatbot(API_URL);
```

## 📞 Support

Jika ada pertanyaan atau butuh bantuan integrasi:

1. Check API documentation: `http://localhost:8000/docs`
2. Test dengan demo: `demo.html`
3. Lihat browser console untuk error details
4. Contact development team

---

**🎉 Happy Integrating! Website Anda sekarang bisa chat dengan customer menggunakan AI chatbot Niscahya!**