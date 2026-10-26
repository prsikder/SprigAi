(function () {
  "use strict";

  const chatMessages = document.getElementById("chatMessages");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const typingRow = document.getElementById("typingRow");
  const welcomeBlock = document.getElementById("welcomeBlock");
  const suggestions = document.querySelectorAll(".sprig-chat-suggestion");

  if (!chatMessages || !chatForm || !chatInput) return;

  const sendUrl = chatForm.dataset.sendUrl;
  const csrfToken = chatForm.querySelector("[name=csrfmiddlewaretoken]").value;

  const SUGGESTIONS = [
    "What crops grow best in Bangladesh monsoon season?",
    "How do I treat common rice leaf blight?",
    "When should I apply fertilizer to wheat?",
    "What soil type is best for mango trees?",
  ];

  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function scrollToBottom(smooth) {
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: smooth ? "smooth" : "auto",
    });
  }

  function hideWelcome() {
    if (welcomeBlock) {
      welcomeBlock.style.display = "none";
    }
  }

  function createMessageRow(text, sender, animate) {
    const row = document.createElement("div");
    row.className = "sprig-chat-row " + (sender === "user" ? "user" : "bot");
    if (animate) row.style.animationDelay = "0s";

    const avatar = document.createElement("div");
    avatar.className = "sprig-chat-row-avatar";
    avatar.innerHTML = sender === "user"
      ? '<i class="bi bi-person-fill"></i>'
      : '<i class="bi bi-flower1"></i>';

    const wrap = document.createElement("div");
    wrap.className = "sprig-chat-bubble-wrap";

    const bubble = document.createElement("div");
    bubble.className = "sprig-chat-bubble";

    const time = document.createElement("span");
    time.className = "sprig-chat-time";
    time.textContent = formatTime(new Date());

    wrap.appendChild(bubble);
    wrap.appendChild(time);
    row.appendChild(avatar);
    row.appendChild(wrap);

    return { row, bubble };
  }

  function appendUserMessage(text) {
    hideWelcome();
    const { row, bubble } = createMessageRow(text, "user", true);
    bubble.textContent = text;
    chatMessages.appendChild(row);
    scrollToBottom(true);
  }

  function showTyping() {
    if (typingRow) {
      typingRow.classList.remove("d-none");
      scrollToBottom(true);
    }
  }

  function hideTyping() {
    if (typingRow) typingRow.classList.add("d-none");
  }

  function typeBotMessage(text, instant) {
    hideWelcome();
    hideTyping();

    const { row, bubble } = createMessageRow(text, "bot", true);
    chatMessages.appendChild(row);
    scrollToBottom(true);

    if (instant || text.length > 600) {
      bubble.textContent = text;
      scrollToBottom(true);
      return Promise.resolve();
    }

    return new Promise(function (resolve) {
      let i = 0;
      const speed = Math.max(8, Math.min(18, 1200 / text.length));

      function tick() {
        if (i < text.length) {
          bubble.textContent += text.charAt(i);
          i += 1;
          if (i % 8 === 0) scrollToBottom(true);
          setTimeout(tick, speed);
        } else {
          scrollToBottom(true);
          resolve();
        }
      }
      tick();
    });
  }

  function setInputEnabled(enabled) {
    chatInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    sendBtn.classList.toggle("sending", !enabled);
  }

  function autoResizeInput() {
    chatInput.style.height = "auto";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + "px";
  }

  async function sendMessage(text) {
    const message = text.trim();
    if (!message) return;

    appendUserMessage(message);
    chatInput.value = "";
    autoResizeInput();
    setInputEnabled(false);
    showTyping();

    try {
      const resp = await fetch(sendUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ message: message }),
      });

      const data = await resp.json();
      hideTyping();

      if (data.reply) {
        await typeBotMessage(data.reply, !data.provider_ok);
      } else {
        await typeBotMessage("Sorry, something went wrong. Please try again.", true);
      }
    } catch (err) {
      hideTyping();
      await typeBotMessage("Network error — please check your connection and try again.", true);
    } finally {
      setInputEnabled(true);
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage(chatInput.value);
  });

  chatInput.addEventListener("input", autoResizeInput);

  chatInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.requestSubmit();
    }
  });

  suggestions.forEach(function (btn) {
    btn.addEventListener("click", function () {
      sendMessage(btn.dataset.prompt || btn.textContent);
    });
  });

  scrollToBottom(false);
  chatInput.focus();
})();
