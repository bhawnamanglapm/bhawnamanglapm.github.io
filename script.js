(function(){
  document.documentElement.classList.add('js');

  // Order Case Studies categories by most-recently-worked-on date first.
  // Add data-updated="YYYY-MM-DD" to a .jcard when its content is filled
  // in/edited — the category holding it moves up automatically on next load.
  // Categories with no dated cards yet keep their original J1..J11 order,
  // placed after every dated category.
  (function(){
    var tracks = document.querySelectorAll('.jtrack');
    tracks.forEach(function(track){
      var groups = Array.prototype.slice.call(track.querySelectorAll('.jcat-group'));
      groups.forEach(function(g){
        var dates = Array.prototype.slice.call(g.querySelectorAll('.jcard[data-updated]'))
          .map(function(c){ return c.getAttribute('data-updated'); });
        g.dataset.sortDate = dates.length ? dates.sort().slice(-1)[0] : '';
      });
      groups.sort(function(a, b){
        var da = a.dataset.sortDate, db = b.dataset.sortDate;
        if(da && db) return da === db ? 0 : (da < db ? 1 : -1);
        if(da && !db) return -1;
        if(!da && db) return 1;
        return 0;
      });
      groups.forEach(function(g){ track.appendChild(g); });

      // Non-.jcat-group children (e.g. the "Show more" link to an expanded
      // roadmap page) aren't touched by the sort above, which otherwise
      // leaves them stranded at the top since appendChild moves the sorted
      // groups to the end — keep them pinned after the sorted groups instead.
      var trailing = track.querySelectorAll(':scope > a.track-showmore');
      trailing.forEach(function(el){ track.appendChild(el); });

      // Show a "last worked on" badge for categories with dated cards.
      groups.forEach(function(g){
        if(!g.dataset.sortDate) return;
        var head = g.querySelector('.jcat-head');
        if(!head || head.querySelector('.jcat-updated')) return;
        var d = new Date(g.dataset.sortDate + 'T00:00:00');
        var label = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        var badge = document.createElement('span');
        badge.className = 'jcat-updated';
        badge.textContent = 'Last worked on ' + label;
        head.appendChild(badge);
      });
    });
  })();

  // Case study full-screen detail view
  var caseOverlay = document.getElementById('caseOverlay');
  var caseBack = document.getElementById('caseBack');
  var caseDetailIllus = document.getElementById('caseDetailIllus');
  var caseDetailCategory = document.getElementById('caseDetailCategory');
  var caseDetailTitle = document.getElementById('caseDetailTitle');
  var caseDetailMeta = document.getElementById('caseDetailMeta');
  var caseDetailBody = document.getElementById('caseDetailBody');
  var jcards = document.querySelectorAll('.jcard[data-case]');
  var lastFocusedCard = null;
  var lastOriginSection = 'practice';
  var mainEl = document.getElementById('main-content');
  var navEl = document.querySelector('nav');
  var footerEl = document.querySelector('footer');

  function findCardBySlug(slug){
    for(var i = 0; i < jcards.length; i++){
      if(jcards[i].getAttribute('data-case') === slug){
        // Never open a card that's hidden (work-in-progress, not ready to publish)
        // even via a stale cross-reference link or a directly-typed URL hash.
        if(jcards[i].closest('.hide-wip')) return null;
        return jcards[i];
      }
    }
    return null;
  }

  function openCase(card, pushHistory){
    if(!card || !caseOverlay) return;
    var illus = card.querySelector('.jcard-illus');
    var title = card.querySelector('.jtitle');
    var meta = card.querySelector('.jmeta');
    var body = card.querySelector('.jbody');
    var catTitle = card.closest('.jcat-group');
    catTitle = catTitle ? catTitle.querySelector('.jcat-title') : null;

    caseDetailIllus.innerHTML = illus ? illus.innerHTML : '';
    caseDetailIllus.setAttribute('style', illus ? illus.getAttribute('style') : '');
    caseDetailCategory.textContent = catTitle ? catTitle.textContent : '';
    caseDetailTitle.textContent = title ? title.textContent : '';
    caseDetailMeta.textContent = meta ? meta.textContent : '';
    caseDetailBody.innerHTML = body ? body.innerHTML : '';

    caseOverlay.hidden = false;
    document.documentElement.classList.add('case-open');
    caseOverlay.scrollTop = 0;
    lastFocusedCard = card;
    var originSection = card.closest('section');
    lastOriginSection = originSection ? originSection.id : 'practice';
    caseBack.focus();
    if(mainEl) mainEl.inert = true;
    if(navEl) navEl.inert = true;
    if(footerEl) footerEl.inert = true;

    if(pushHistory !== false){
      var slug = card.getAttribute('data-case');
      history.pushState({ caseSlug: slug }, '', '#case-' + slug);
    }
  }

  function closeCase(pushHistory){
    if(!caseOverlay || caseOverlay.hidden) return;
    caseOverlay.hidden = true;
    document.documentElement.classList.remove('case-open');
    if(mainEl) mainEl.inert = false;
    if(navEl) navEl.inert = false;
    if(footerEl) footerEl.inert = false;
    if(lastFocusedCard){
      var btn = lastFocusedCard.querySelector('.jhead');
      if(btn) btn.focus();
    }
    if(pushHistory !== false){
      history.pushState(null, '', '#' + lastOriginSection);
    }
  }

  jcards.forEach(function(card){
    var btn = card.querySelector('.jhead');
    if(btn){
      btn.addEventListener('click', function(){ openCase(card); });
    }
  });

  // In-content cross-references between case studies, e.g.
  // <a data-open-case="some-slug">, work whether clicked from the page
  // or from inside an already-open overlay (a plain #case-slug href only
  // fires history's popstate on back/forward, not on the initial click).
  document.addEventListener('click', function(e){
    var link = e.target.closest ? e.target.closest('[data-open-case]') : null;
    if(!link) return;
    var target = findCardBySlug(link.getAttribute('data-open-case'));
    if(target){
      e.preventDefault();
      openCase(target);
    }
  });

  if(caseBack){
    caseBack.addEventListener('click', function(){ closeCase(); });
  }

  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && caseOverlay && !caseOverlay.hidden){ closeCase(); }
  });

  window.addEventListener('popstate', function(){
    var hash = window.location.hash;
    if(hash.indexOf('#case-') === 0){
      var slug = hash.slice(6);
      var card = findCardBySlug(slug);
      if(card) openCase(card, false);
    } else {
      closeCase(false);
    }
  });

  // Support direct-linking / reload on a #case-<slug> URL
  (function(){
    var hash = window.location.hash;
    if(hash.indexOf('#case-') === 0){
      var slug = hash.slice(6);
      var card = findCardBySlug(slug);
      if(card) openCase(card, false);
    }
  })();

  // Mobile nav toggle
  var navToggle = document.getElementById('navToggle');
  var navLinks = document.getElementById('navLinks');
  if(navToggle && navLinks){
    navToggle.addEventListener('click', function(){
      var open = navLinks.classList.toggle('open');
      navToggle.classList.toggle('active', open);
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navLinks.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){
        navLinks.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Scroll-spy: highlight the nav link for the section currently in view
  var navAnchorEls = navLinks ? navLinks.querySelectorAll('a:not(.nav-btn)') : [];
  var spySections = Array.prototype.slice.call(navAnchorEls).map(function(a){
    var id = a.getAttribute('href').slice(1);
    return { link: a, section: document.getElementById(id) };
  }).filter(function(s){ return s.section; });
  if('IntersectionObserver' in window && spySections.length){
    var spyIo = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        var match = spySections.filter(function(s){ return s.section === entry.target; })[0];
        if(!match) return;
        if(entry.isIntersecting){
          spySections.forEach(function(s){ s.link.classList.remove('active'); });
          match.link.classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });
    spySections.forEach(function(s){ spyIo.observe(s.section); });
  }

  // Scroll-reveal animations
  var revealSelectors = '.sec-head, .jcat-group, .tl-card, .toolkit-cat, .stat-circle, .impact-card, .resume-panel, .rec-card, .elsewhere-card, .panel, .contact-form, .ptable2-wrap, .pipeline, .strength-card, .tool-item, .ai-sub, .recognition-card';
  // Elements nested inside a .jbody are hidden (display:none) until the case-overlay
  // opens, so they never intersect the viewport and would otherwise stay stuck at
  // opacity:0 forever — exclude them from scroll-reveal entirely.
  var revealEls = Array.prototype.filter.call(document.querySelectorAll(revealSelectors), function(el){
    return !el.closest('.jbody');
  });
  if('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    revealEls.forEach(function(el){ el.classList.add('reveal'); });
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add('in-view');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function(el){ io.observe(el); });
  }

  // Count-up animation for impact numbers
  var countEls = document.querySelectorAll('.stat-num, .impact-card .num:not(.todo)');
  if('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches && countEls.length){
    var numRe = /\d+(\.\d+)?/g;
    var countIo = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(!entry.isIntersecting) return;
        countIo.unobserve(entry.target);
        var el = entry.target;
        var template = el.textContent;
        var targets = (template.match(numRe) || []).map(Number);
        if(!targets.length) return;
        var duration = 1200;
        var start = null;
        function frame(ts){
          if(start === null) start = ts;
          var progress = Math.min((ts - start) / duration, 1);
          var eased = 1 - Math.pow(1 - progress, 3);
          var i = 0;
          el.textContent = template.replace(numRe, function(match){
            var target = targets[i++];
            var current = target * eased;
            return Number.isInteger(target) ? Math.round(current).toString() : current.toFixed(1);
          });
          if(progress < 1){
            requestAnimationFrame(frame);
          } else {
            el.textContent = template;
          }
        }
        requestAnimationFrame(frame);
      });
    }, { threshold: 0.4 });
    countEls.forEach(function(el){ countIo.observe(el); });
  }

  // Contact form -> Web3Forms (sends real email, no backend of our own)
  var form = document.getElementById('contactForm');
  var status = document.getElementById('formStatus');
  if(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var submitBtn = form.querySelector('button[type="submit"]');
      if(submitBtn){ submitBtn.disabled = true; }
      if(status){ status.classList.remove('error'); status.classList.add('show'); status.textContent = 'Sending…'; }

      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(Object.fromEntries(new FormData(form)))
      })
        .then(function(res){ return res.json(); })
        .then(function(data){
          if(data.success){
            if(status){ status.textContent = "Sent — I'll get back to you soon."; }
            form.reset();
          } else {
            if(status){ status.classList.add('error'); status.textContent = "Something went wrong — email me directly instead."; }
          }
        })
        .catch(function(){
          if(status){ status.classList.add('error'); status.textContent = "Couldn't send — email me directly instead."; }
        })
        .finally(function(){
          if(submitBtn){ submitBtn.disabled = false; }
        });
    });
  }
})();
