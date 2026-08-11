(function(){
  document.addEventListener('DOMContentLoaded', function(){
    var WORKER_URL = 'https://bhawna-portfolio-chatbot.bhawnamangla98.workers.dev';

    var OFFLINE_MESSAGE = "I'm not able to chat right now — feel free to email Bhawna directly at bhawna202019@gmail.com or connect on LinkedIn.";

    // ---------- Build widget markup ----------
    var root = document.createElement('div');
    root.className = 'chatbot-root';
    root.innerHTML =
      '<button class="chatbot-toggle" type="button" aria-label="Open chat about Bhawna" aria-expanded="false">' +
        '<svg class="chatbot-toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/></svg>' +
        '<svg class="chatbot-toggle-icon chatbot-toggle-icon--close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>' +
      '</button>' +
      '<div class="chatbot-panel" role="dialog" aria-label="Chat about Bhawna Mangla" hidden>' +
        '<div class="chatbot-head">' +
          '<div>' +
            '<div class="chatbot-title">Ask about Bhawna</div>' +
            '<div class="chatbot-subtitle">AI assistant, trained on this portfolio</div>' +
          '</div>' +
          '<button class="chatbot-close" type="button" aria-label="Close chat">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6L6 18M6 6l12 12"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="chatbot-messages" role="log" aria-live="polite"></div>' +
        '<form class="chatbot-input-row">' +
          '<input class="chatbot-input" type="text" placeholder="Ask a question…" maxlength="500" aria-label="Your question" autocomplete="off">' +
          '<button class="chatbot-send" type="submit" aria-label="Send">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>' +
          '</button>' +
        '</form>' +
      '</div>';
    document.body.appendChild(root);

    var toggleBtn = root.querySelector('.chatbot-toggle');
    var panel = root.querySelector('.chatbot-panel');
    var closeBtn = root.querySelector('.chatbot-close');
    var messagesEl = root.querySelector('.chatbot-messages');
    var form = root.querySelector('.chatbot-input-row');
    var input = root.querySelector('.chatbot-input');
    var sendBtn = root.querySelector('.chatbot-send');

    var history = []; // { role: 'user'|'assistant', content: string }
    var opened = false;
    var greeted = false;

    function addBubble(role, text){
      var bubble = document.createElement('div');
      bubble.className = 'chatbot-bubble chatbot-bubble--' + role;
      bubble.textContent = text;
      messagesEl.appendChild(bubble);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return bubble;
    }

    function addTyping(){
      var bubble = document.createElement('div');
      bubble.className = 'chatbot-bubble chatbot-bubble--assistant chatbot-typing';
      bubble.innerHTML = '<span></span><span></span><span></span>';
      messagesEl.appendChild(bubble);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return bubble;
    }

    function setBusy(busy){
      input.disabled = busy;
      sendBtn.disabled = busy;
    }

    function openPanel(){
      panel.hidden = false;
      root.classList.add('chatbot-open');
      toggleBtn.setAttribute('aria-expanded', 'true');
      opened = true;
      if(!greeted){
        greeted = true;
        addBubble('assistant', "Hi! I'm an AI assistant trained on Bhawna's portfolio. Ask me about her experience, case studies, or skills — try “What did she build at Bajaj Finserv?”");
      }
      input.focus();
    }

    function closePanel(){
      panel.hidden = true;
      root.classList.remove('chatbot-open');
      toggleBtn.setAttribute('aria-expanded', 'false');
      opened = false;
    }

    toggleBtn.addEventListener('click', function(){
      if(opened) closePanel(); else openPanel();
    });
    closeBtn.addEventListener('click', closePanel);
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape' && opened) closePanel();
    });

    form.addEventListener('submit', function(e){
      e.preventDefault();
      var text = input.value.trim();
      if(!text) return;

      addBubble('user', text);
      history.push({ role: 'user', content: text });
      input.value = '';
      setBusy(true);
      var typingBubble = addTyping();

      if(!WORKER_URL){
        setTimeout(function(){
          typingBubble.remove();
          addBubble('assistant', OFFLINE_MESSAGE);
          setBusy(false);
          input.focus();
        }, 400);
        return;
      }

      fetch(WORKER_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: history.slice(0, -1) })
      })
        .then(function(res){
          return res.json().then(function(data){
            return { ok: res.ok, status: res.status, data: data };
          });
        })
        .then(function(result){
          typingBubble.remove();
          if(result.ok && result.data && result.data.reply){
            addBubble('assistant', result.data.reply);
            history.push({ role: 'assistant', content: result.data.reply });
          } else {
            // TEMP DEBUG: surfacing the real error instead of the friendly
            // fallback while we track down the deploy issue. Revert to
            // OFFLINE_MESSAGE once the chatbot is confirmed working.
            var detail = result.data && (result.data.error || result.data.detail);
            addBubble('assistant', 'Debug — HTTP ' + result.status + (detail ? ': ' + detail : ' (no error detail in response body)'));
          }
        })
        .catch(function(err){
          typingBubble.remove();
          // TEMP DEBUG: same as above, revert once fixed.
          addBubble('assistant', 'Debug — request failed before a response came back: ' + (err && err.message ? err.message : String(err)));
        })
        .finally(function(){
          setBusy(false);
          input.focus();
        });
    });
  });
})();
