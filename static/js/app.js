/* ============================================================
   Startup Stress-Test TN — Main Application JavaScript
   ============================================================ */

const App = {
  currentPage: 'accueil',
  questionnaireStep: 1,
  questionnaireAnswers: {},
  simulationData: null,
  diagnosticData: null,
  charts: {},

  // ==================== INITIALIZATION ====================
  init() {
    this.setupNavigation();
    this.setupSimulatorSliders();
    this.setupPresetScenarios();
    this.setupMobileMenu();
    this.animateCounters();
    this.loadQuestionnaire(1);
    this.loadMarketData();
    // Run initial simulation with default values
    setTimeout(() => this.runSimulation(), 500);
  },

  // ==================== NAVIGATION ====================
  setupNavigation() {
    document.querySelectorAll('#mainNav button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.navigateTo(btn.dataset.page);
      });
    });
  },

  navigateTo(page) {
    // Hide all sections
    document.querySelectorAll('.page-section').forEach(s => s.classList.remove('active'));
    // Show target
    const target = document.getElementById('page-' + page);
    if (target) {
      target.classList.add('active');
      target.style.animation = 'none';
      target.offsetHeight; // reflow
      target.style.animation = '';
    }
    // Update nav
    document.querySelectorAll('#mainNav button').forEach(b => b.classList.remove('active'));
    const navBtn = document.querySelector(`#mainNav button[data-page="${page}"]`);
    if (navBtn) navBtn.classList.add('active');
    this.currentPage = page;
    // Close mobile menu
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebarOverlay').classList.remove('active');
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (page === 'rapport') this.generateRapport();
  },

  // ==================== MOBILE MENU ====================
  setupMobileMenu() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (toggle) {
      toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('active');
      });
    }
    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
      });
    }
  },

  // ==================== ANIMATED COUNTERS ====================
  animateCounters() {
    const counters = document.querySelectorAll('.counter');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.target);
          this._countUp(el, 0, target, 1500);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(c => observer.observe(c));
  },

  _countUp(el, start, end, duration) {
    const range = end - start;
    const increment = end > 100 ? Math.ceil(range / (duration / 16)) : 1;
    const stepTime = Math.max(16, Math.floor(duration / (range / increment)));
    let current = start;
    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        current = end;
        clearInterval(timer);
      }
      el.textContent = current.toLocaleString('fr-FR');
      if (el.closest('.stat-item') && end === 98) {
        el.textContent = current + '%';
      } else if (end >= 1000) {
        el.textContent = current.toLocaleString('fr-FR') + '+';
      } else if (end > 10 && end < 100) {
        el.textContent = current + '+';
      }
    }, stepTime);
  },

  // ==================== MARKET DATA ====================
  async loadMarketData() {
    try {
      const res = await fetch('/api/market-data');
      const json = await res.json();
      if (!json.success) return;
      const data = json.data;
      
      // Sector cards
      const scroll = document.getElementById('marketScroll');
      if (scroll && data.secteurs) {
        let html = '';
        Object.entries(data.secteurs).forEach(([key, s]) => {
          const croissance = s.taux_croissance_annuel;
          const trend = croissance > 15 ? '📈' : croissance > 5 ? '➡️' : '📉';
          html += `<div class="market-card">
            <div class="market-card-name">${s.nom}</div>
            <div class="market-card-stat"><span>Panier moyen</span><strong>${s.panier_moyen} DT</strong></div>
            <div class="market-card-stat"><span>Taille marché</span><strong>${s.taille_marche_mdt}M DT</strong></div>
            <div class="market-card-stat"><span>Croissance</span><strong style="color:${croissance > 10 ? 'var(--success)' : croissance > 0 ? 'var(--warning)' : 'var(--danger)'}">${trend} +${croissance}%/an</strong></div>
            <div class="market-card-stat"><span>Concurrence</span><strong>${s.concurrence}</strong></div>
          </div>`;
        });
        scroll.innerHTML = html;
      }
      
      // Macro indicators
      const macro = document.getElementById('marketMacro');
      if (macro && data.indicateurs_macro) {
        const m = data.indicateurs_macro;
        macro.innerHTML = `
          <div class="macro-item"><i class="fas fa-wifi"></i><span>Pénétration Internet</span><strong>${m.penetration_internet_pct}%</strong></div>
          <div class="macro-item"><i class="fas fa-mobile-alt"></i><span>Pénétration Smartphone</span><strong>${m.penetration_smartphone_pct}%</strong></div>
          <div class="macro-item"><i class="fas fa-rocket"></i><span>Startups labelisées</span><strong>${m.nombre_startups_labelisees}</strong></div>
          <div class="macro-item"><i class="fas fa-chart-line"></i><span>Taux d'inflation</span><strong>${m.taux_inflation_pct}%</strong></div>
          <div class="macro-item"><i class="fas fa-users"></i><span>Taux de chômage</span><strong>${m.taux_chomage_pct}%</strong></div>
          <div class="macro-item"><i class="fas fa-store"></i><span>E-commerce croissance</span><strong>+${m.croissance_ecommerce_pct || '—'}%</strong></div>
        `;
      }
    } catch (e) { console.error('market data error', e); }
  },

  // ==================== QUESTIONNAIRE ====================
  async loadQuestionnaire(step) {
    const container = document.getElementById('questionContainer');
    container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Chargement des questions…</p></div>';

    try {
      const res = await fetch('/api/questionnaire', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ step, answers: this.questionnaireAnswers })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      this.questionnaireStep = step;
      this._renderProgressSteps(step, data.total_steps);
      document.getElementById('progressBar').style.width = data.progression + '%';
      this._renderQuestions(data);
    } catch (err) {
      container.innerHTML = `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  _renderProgressSteps(current, total) {
    const wrap = document.getElementById('progressSteps');
    let html = '';
    for (let i = 1; i <= total; i++) {
      const cls = i < current ? 'done' : i === current ? 'active' : '';
      html += `<div class="step-dot ${cls}">${i < current ? '<i class="fas fa-check" style="font-size:12px"></i>' : i}</div>`;
    }
    wrap.innerHTML = html;
  },

  _renderQuestions(data) {
    const container = document.getElementById('questionContainer');
    let html = `<div class="question-card animate-slide-up">
      <h3>${data.titre}</h3>
      <p class="helper-text">Étape ${data.step} sur ${data.total_steps}</p>`;

    data.questions.forEach(q => {
      html += `<div class="form-group" id="qgroup-${q.id}">
        <label><i class="fas fa-angle-right"></i> ${q.texte}</label>`;

      if (q.hint) {
        html += `<small style="color:var(--secondary);font-size:12px;display:block;margin-bottom:6px"><i class="fas fa-info-circle"></i> ${q.hint}</small>`;
      }

      if (q.type === 'select') {
        const val = this.questionnaireAnswers[q.id] || '';
        // Check if this select triggers conditional questions in same step
        const hasSameStepConditional = data.allQuestions && data.allQuestions.some(oq => oq.condition?.field === q.id);
        const reloadOnChange = hasSameStepConditional ? `App.loadQuestionnaire(${data.step})` : '';
        html += `<select class="form-control" data-qid="${q.id}" onchange="App._onAnswer('${q.id}', this.value)${reloadOnChange ? '; ' + reloadOnChange : ''}">
          <option value="">Choisir…</option>`;
        q.options.forEach(opt => {
          html += `<option value="${opt.value}" ${val === opt.value ? 'selected' : ''}>${opt.label}</option>`;
        });
        html += '</select>';
        // If "autre" is selected, show a text field
        if (val === 'autre' || val === 'autre_revenu' || val === 'autre_region') {
          const autreVal = this.questionnaireAnswers[q.id + '_autre'] || '';
          html += `<input type="text" class="form-control" style="margin-top:8px" placeholder="Précisez…" value="${autreVal}" oninput="App._onAnswer('${q.id}_autre', this.value)">`;
        }
      } else if (q.type === 'multiselect') {
        const vals = this.questionnaireAnswers[q.id] || [];
        html += '<div class="checkbox-group">';
        q.options.forEach(opt => {
          const checked = vals.includes(opt.value);
          html += `<label class="checkbox-option ${checked ? 'selected' : ''}">
            <input type="checkbox" value="${opt.value}" ${checked ? 'checked' : ''} 
              onchange="App._onMultiAnswer('${q.id}', '${opt.value}', this.checked, this)">
            ${opt.label}</label>`;
        });
        html += '</div>';
        // If "autre" is in selected values, show text input
        if (vals.includes('autre') || vals.includes('autre_revenu')) {
          const autreVal = this.questionnaireAnswers[q.id + '_autre'] || '';
          html += `<input type="text" class="form-control" style="margin-top:8px" placeholder="Précisez votre autre option…" value="${autreVal}" oninput="App._onAnswer('${q.id}_autre', this.value)">`;
        }
      } else if (q.type === 'number') {
        const val = this.questionnaireAnswers[q.id] || '';
        html += `<input type="number" class="form-control" data-qid="${q.id}" 
          value="${val}" placeholder="${q.placeholder || ''}" 
          oninput="App._onAnswer('${q.id}', this.value)">`;
      } else {
        const val = this.questionnaireAnswers[q.id] || '';
        html += `<input type="text" class="form-control" data-qid="${q.id}" 
          value="${val}" placeholder="${q.placeholder || ''}" 
          oninput="App._onAnswer('${q.id}', this.value)">`;
      }

      // Inline conditional: montant_recherche shown when besoin_financement is answered in same step
      if (q.id === 'besoin_financement') {
        const bfVal = this.questionnaireAnswers['besoin_financement'];
        if (bfVal && bfVal !== 'non') {
          const montantVal = this.questionnaireAnswers['montant_recherche'] || '';
          html += `<div class="form-group" style="margin-top:16px;padding:16px;background:rgba(255,107,107,0.05);border:1px dashed var(--primary);border-radius:var(--radius-sm)">
            <label><i class="fas fa-money-bill-wave" style="color:var(--primary)"></i> Montant à lever (en DT)</label>
            <input type="number" class="form-control" id="montant_recherche_inline" placeholder="Ex: 80000"
              value="${montantVal}" oninput="App._onAnswer('montant_recherche', this.value)">
          </div>`;
        }
      }

      html += '</div>';
    });

    html += '<div class="question-actions">';
    if (data.step > 1) {
      html += `<button class="btn btn-ghost" onclick="App.loadQuestionnaire(${data.step - 1})"><i class="fas fa-arrow-left"></i> Précédent</button>`;
    } else {
      html += '<div></div>';
    }
    if (data.is_last) {
      html += `<button class="btn btn-primary" onclick="App._finishQuestionnaire()"><i class="fas fa-check"></i> Terminer</button>`;
    } else {
      html += `<button class="btn btn-primary" onclick="App.loadQuestionnaire(${data.step_suivant})">Suivant <i class="fas fa-arrow-right"></i></button>`;
    }
    html += '</div></div>';

    container.innerHTML = html;
  },

  _onAnswer(id, value) {
    this.questionnaireAnswers[id] = value;
  },

  _onMultiAnswer(id, value, checked, el) {
    if (!this.questionnaireAnswers[id]) this.questionnaireAnswers[id] = [];
    if (checked) {
      if (!this.questionnaireAnswers[id].includes(value)) {
        this.questionnaireAnswers[id].push(value);
      }
      el.closest('.checkbox-option').classList.add('selected');
    } else {
      this.questionnaireAnswers[id] = this.questionnaireAnswers[id].filter(v => v !== value);
      el.closest('.checkbox-option').classList.remove('selected');
    }
  },

  _finishQuestionnaire() {
    // Pre-fill simulator with questionnaire answers
    if (this.questionnaireAnswers.panier_moyen_estime) {
      const panierVal = parseFloat(this.questionnaireAnswers.panier_moyen_estime);
      if (!isNaN(panierVal) && panierVal > 0) {
        const sPanier = document.getElementById('sim_panier');
        const nPanier = document.getElementById('num_panier');
        const dPanier = document.getElementById('val_panier');
        if (sPanier) sPanier.value = panierVal;
        if (nPanier) nPanier.value = panierVal;
        if (dPanier) dPanier.textContent = panierVal;
      }
    }

    if (this.questionnaireAnswers.objectif_clients_an1) {
      const objClients = parseFloat(this.questionnaireAnswers.objectif_clients_an1);
      if (!isNaN(objClients) && objClients > 0 && objClients < 5000) {
        const monthlyCmd = Math.round(objClients / 12);
        const sCmd = document.getElementById('sim_commandes');
        const nCmd = document.getElementById('num_commandes');
        const dCmd = document.getElementById('val_commandes');
        if (sCmd) sCmd.value = monthlyCmd;
        if (nCmd) nCmd.value = monthlyCmd;
        if (dCmd) dCmd.textContent = monthlyCmd;
      }
    }

    // Refresh simulation
    this.runSimulation();

    // Show success message
    const container = document.getElementById('questionContainer');
    container.innerHTML = `<div class="question-card animate-scale-in" style="text-align:center;padding:60px 40px">
      <div style="width:80px;height:80px;border-radius:50%;background:var(--gradient-secondary);display:flex;align-items:center;justify-content:center;margin:0 auto 24px;font-size:36px;color:white">
        <i class="fas fa-check"></i>
      </div>
      <h3 style="font-size:24px;margin-bottom:12px">Questionnaire terminé !</h3>
      <p style="color:var(--text-light);margin-bottom:32px;max-width:400px;margin-left:auto;margin-right:auto">
        Vos réponses ont été enregistrées. Explorez maintenant les autres outils pour approfondir votre analyse.
      </p>
      <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
        <button class="btn btn-primary" onclick="App.navigateTo('simulateur')"><i class="fas fa-chart-line"></i> Simulateur (pré-rempli)</button>
        <button class="btn btn-secondary" onclick="App.navigateTo('diagnostic')"><i class="fas fa-stethoscope"></i> Diagnostic</button>
        <button class="btn btn-ghost" onclick="App.navigateTo('business-plan')"><i class="fas fa-file-lines"></i> Business Plan</button>
      </div>
    </div>`;
  },

  // ==================== SIMULATOR ====================
  setupSimulatorSliders() {
    const sliderPairs = [
      { slider: 'sim_panier', num: 'num_panier', display: 'val_panier' },
      { slider: 'sim_cout_produits', num: 'num_cout_produits', display: 'val_cout_produits' },
      { slider: 'sim_cout_transport', num: 'num_cout_transport', display: 'val_cout_transport' },
      { slider: 'sim_livraison', num: 'num_livraison', display: 'val_livraison' },
      { slider: 'sim_autres', num: 'num_autres', display: 'val_autres' },
      { slider: 'sim_charges', num: 'num_charges', display: 'val_charges' },
      { slider: 'sim_commandes', num: 'num_commandes', display: 'val_commandes' }
    ];

    sliderPairs.forEach(pair => {
      const slider = document.getElementById(pair.slider);
      const num = document.getElementById(pair.num);
      const display = document.getElementById(pair.display);
      if (!slider || !num) return;

      const update = (val) => {
        slider.value = val;
        num.value = val;
        if (display) display.textContent = val;
        this._debouncedSimulate();
      };

      slider.addEventListener('input', () => update(slider.value));
      num.addEventListener('input', () => update(num.value));
    });

    // Shock sliders
    const shocks = [
      { id: 'sim_choc_a', display: 'val_choc_a' },
      { id: 'sim_choc_b', display: 'val_choc_b' },
      { id: 'sim_choc_c', display: 'val_choc_c' },
      { id: 'sim_choc_d', display: 'val_choc_d' }
    ];

    shocks.forEach(s => {
      const el = document.getElementById(s.id);
      if (!el) return;
      el.addEventListener('input', () => {
        document.getElementById(s.display).textContent = el.value + '%';
        this._debouncedSimulate();
      });
    });

    // Combined toggle
    const toggle = document.getElementById('simCombined');
    if (toggle) toggle.addEventListener('change', () => this.runSimulation());
  },

  _simulateTimeout: null,
  _debouncedSimulate() {
    clearTimeout(this._simulateTimeout);
    this._simulateTimeout = setTimeout(() => this.runSimulation(), 150);
  },

  setupPresetScenarios() {
    const sel = document.getElementById('presetScenario');
    if (!sel) return;
    sel.addEventListener('change', () => {
      if (sel.value === 'okkis') {
        this._setSimValues({ panier: 89, cout_produits: 70, cout_transport: 8, autres: 2, charges: 9000, commandes: 1000, choc_a: 25, choc_b: 8, choc_c: 0, choc_d: 0 });
      } else {
        this._setSimValues({ panier: 89, cout_produits: 45, cout_transport: 8, autres: 5, charges: 3000, commandes: 200, choc_a: 30, choc_b: 20, choc_c: 10, choc_d: 10 });
      }
    });
  },

  _setSimValues(v) {
    const setVal = (slider, num, display, val, suffix) => {
      const s = document.getElementById(slider);
      const n = document.getElementById(num);
      const d = document.getElementById(display);
      if (s) s.value = val;
      if (n) n.value = val;
      if (d) d.textContent = val + (suffix || '');
    };
    setVal('sim_panier', 'num_panier', 'val_panier', v.panier);
    setVal('sim_cout_produits', 'num_cout_produits', 'val_cout_produits', v.cout_produits);
    setVal('sim_cout_transport', 'num_cout_transport', 'val_cout_transport', v.cout_transport);
    setVal('sim_autres', 'num_autres', 'val_autres', v.autres);
    setVal('sim_charges', 'num_charges', 'val_charges', v.charges);
    setVal('sim_commandes', 'num_commandes', 'val_commandes', v.commandes);
    setVal('sim_choc_a', null, 'val_choc_a', v.choc_a, '%');
    setVal('sim_choc_b', null, 'val_choc_b', v.choc_b, '%');
    setVal('sim_choc_c', null, 'val_choc_c', v.choc_c, '%');
    setVal('sim_choc_d', null, 'val_choc_d', v.choc_d, '%');
    this.runSimulation();
  },

  async runSimulation() {
    const params = {
      panier_moyen: parseFloat(document.getElementById('sim_panier')?.value || 89),
      cout_produits: parseFloat(document.getElementById('sim_cout_produits')?.value || 45),
      cout_transport: parseFloat(document.getElementById('sim_cout_transport')?.value || 8),
      autres_couts: parseFloat(document.getElementById('sim_autres')?.value || 5),
      charges_fixes: parseFloat(document.getElementById('sim_charges')?.value || 3000),
      commandes_mois: parseFloat(document.getElementById('sim_commandes')?.value || 200),
      livraison_facturee: parseFloat(document.getElementById('sim_livraison')?.value || 0),
      choc_transport_pct: parseFloat(document.getElementById('sim_choc_a')?.value || 0),
      choc_demande_pct: parseFloat(document.getElementById('sim_choc_b')?.value || 0),
      choc_concurrent_pct: parseFloat(document.getElementById('sim_choc_c')?.value || 0),
      choc_marge_pct: parseFloat(document.getElementById('sim_choc_d')?.value || 0)
    };

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      const data = await res.json();
      if (!data.success) return;

      this.simulationData = data;
      this._updateSimResults(data);
      this._updateSimCharts(data, params);
    } catch (err) {
      console.error('Simulation error:', err);
    }
  },

  _updateSimResults(d) {
    const result = d.apres.resultat_mensuel;
    const resultEl = document.getElementById('resultAmount');
    const badgeEl = document.getElementById('resultBadge');

    // Format big number
    const formatted = (result >= 0 ? '+' : '') + Math.round(result).toLocaleString('fr-FR') + ' DT';
    resultEl.textContent = formatted;
    resultEl.className = 'amount ' + (result > 0 ? 'positive' : result < 0 ? 'negative' : 'zero');

    if (result > 0) {
      badgeEl.textContent = 'BÉNÉFICE';
      badgeEl.className = 'result-badge profit';
    } else if (result < 0) {
      badgeEl.textContent = 'DÉFICIT';
      badgeEl.className = 'result-badge deficit';
    } else {
      badgeEl.textContent = 'ÉQUILIBRE';
      badgeEl.className = 'result-badge equilibre';
    }

    // KPIs
    const setKPI = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
    setKPI('kpiMarge', d.avant.marge_unitaire.toFixed(2) + ' DT');
    setKPI('kpiMargeAfter', 'Après choc : ' + d.apres.marge_unitaire.toFixed(2) + ' DT');
    setKPI('kpiSeuil', (d.avant.seuil_rentabilite || '∞') + ' cmd');
    setKPI('kpiSeuilAfter', 'Après choc : ' + (d.apres.seuil_rentabilite || '∞') + ' cmd');
    
    const cmdRestantes = Math.round(parseFloat(document.getElementById('sim_commandes')?.value || 200) * (1 - parseFloat(document.getElementById('sim_choc_b')?.value || 0) / 100));
    setKPI('kpiRestantes', cmdRestantes);
    
    setKPI('kpiCouverture', d.apres.taux_couverture.toFixed(0) + '%');

    // Coverage bar
    const bar = document.getElementById('coverageBar');
    if (bar) {
      const pct = Math.min(100, Math.max(0, d.apres.taux_couverture));
      bar.style.width = pct + '%';
      bar.style.background = pct >= 100 ? 'var(--success)' : pct >= 70 ? 'var(--warning)' : 'var(--danger)';
    }

    // Shock decomposition
    const decomp = d.decomposition_chocs;
    const decompEl = document.getElementById('shockDecomp');
    if (decompEl) {
      decompEl.innerHTML = [
        { name: 'Choc A : Transport', val: decomp.impact_transport },
        { name: 'Choc B : Demande', val: decomp.impact_demande },
        { name: 'Choc C : Concurrence', val: decomp.impact_concurrent },
        { name: 'Choc D : Marge', val: decomp.impact_marge }
      ].map(s => `<div class="shock-row">
        <span class="shock-name">${s.name}</span>
        <span class="shock-impact" style="color:${s.val <= 0 ? 'var(--danger)' : 'var(--success)'}">
          ${s.val >= 0 ? '+' : ''}${Math.round(s.val).toLocaleString('fr-FR')} DT
        </span>
      </div>`).join('') + `<div class="shock-row" style="border-top:2px solid var(--gray-200);margin-top:4px;padding-top:12px;font-weight:700">
        <span class="shock-name">Total</span>
        <span class="shock-impact" style="color:${decomp.impact_total <= 0 ? 'var(--danger)' : 'var(--success)'}">
          ${decomp.impact_total >= 0 ? '+' : ''}${Math.round(decomp.impact_total).toLocaleString('fr-FR')} DT
        </span>
      </div>`;
    }

    // Gauge
    this._updateGauge(d);

    // Alerts
    if (d.alerte && d.alerte.length) {
      let alertHtml = '';
      d.alerte.forEach(a => {
        alertHtml += `<div class="error-banner" style="background:${a.niveau === 'critique' ? 'rgba(231,76,60,0.08)' : a.niveau === 'attention' ? 'rgba(241,196,15,0.08)' : 'rgba(46,196,182,0.08)'}; border-color:${a.niveau === 'critique' ? 'rgba(231,76,60,0.2)' : a.niveau === 'attention' ? 'rgba(241,196,15,0.2)' : 'rgba(46,196,182,0.2)'}; color:${a.niveau === 'critique' ? 'var(--danger)' : a.niveau === 'attention' ? '#c89e00' : 'var(--secondary-dark)'}">
          ${a.message}
        </div>`;
      });
      const heroEl = document.getElementById('resultHero');
      const existingAlerts = heroEl?.parentNode.querySelector('.sim-alerts');
      if (existingAlerts) existingAlerts.remove();
      const div = document.createElement('div');
      div.className = 'sim-alerts';
      div.style.padding = '0 24px 16px';
      div.innerHTML = alertHtml;
      heroEl?.parentNode.appendChild(div);
    }
  },

  _updateGauge(d) {
    const avant = d.avant.resultat_mensuel;
    const apres = d.apres.resultat_mensuel;
    let score = 50;
    if (avant > 0) {
      const ratio = apres / avant;
      score = Math.max(0, Math.min(100, Math.round(ratio * 75)));
    } else if (apres >= 0) {
      score = 60;
    } else {
      score = Math.max(0, 25 + Math.round(apres / 100));
    }
    score = Math.max(0, Math.min(100, score));

    const arc = document.getElementById('gaugeArc');
    const val = document.getElementById('gaugeValue');
    if (arc) {
      const offset = 440 - (440 * score / 100);
      arc.setAttribute('stroke-dashoffset', offset);
      arc.setAttribute('stroke', score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)');
    }
    if (val) val.textContent = score;
  },

  _updateSimCharts(d, params) {
    // Bar chart
    this._createOrUpdateChart('chartBar', 'bar', {
      labels: ['Résultat avant', 'Résultat après'],
      datasets: [{
        data: [d.avant.resultat_mensuel, d.apres.resultat_mensuel],
        backgroundColor: [
          d.avant.resultat_mensuel >= 0 ? '#2ecc71' : '#e74c3c',
          d.apres.resultat_mensuel >= 0 ? '#2EC4B6' : '#FF6B6B'
        ],
        borderRadius: 8,
        barThickness: 60
      }]
    }, {
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: false, ticks: { callback: v => v.toLocaleString('fr-FR') + ' DT' } }
      }
    });

    // Pie chart
    this._createOrUpdateChart('chartPie', 'doughnut', {
      labels: ['Produits', 'Transport', 'Autres coûts', 'Charges fixes'],
      datasets: [{
        data: [
          params.cout_produits * params.commandes_mois,
          params.cout_transport * params.commandes_mois,
          params.autres_couts * params.commandes_mois,
          params.charges_fixes
        ],
        backgroundColor: ['#FF6B6B', '#2EC4B6', '#3498db', '#f1c40f'],
        borderWidth: 0
      }]
    }, {
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, padding: 12 } } }
    });

    // Line chart (sensitivity)
    const steps = [];
    const resultsA = [], resultsB = [];
    for (let i = 0; i <= 100; i += 5) {
      steps.push(i + '%');
      const margeA = params.panier_moyen - params.cout_produits - params.cout_transport * (1 + i / 100) - params.autres_couts;
      resultsA.push(params.commandes_mois * margeA - params.charges_fixes);
      const cmdB = params.commandes_mois * (1 - i / 100);
      const margeB = params.panier_moyen - params.cout_produits - params.cout_transport - params.autres_couts;
      resultsB.push(cmdB * margeB - params.charges_fixes);
    }

    this._createOrUpdateChart('chartLine', 'line', {
      labels: steps,
      datasets: [
        {
          label: 'Choc Transport',
          data: resultsA,
          borderColor: '#FF6B6B',
          backgroundColor: 'rgba(255,107,107,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: 'Choc Demande',
          data: resultsB,
          borderColor: '#2EC4B6',
          backgroundColor: 'rgba(46,196,182,0.1)',
          fill: true,
          tension: 0.3,
          pointRadius: 0
        }
      ]
    }, {
      plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } },
      scales: {
        y: { ticks: { callback: v => v.toLocaleString('fr-FR') + ' DT' } }
      }
    });
  },

  _createOrUpdateChart(canvasId, type, data, options) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.charts[canvasId]) {
      this.charts[canvasId].data = data;
      this.charts[canvasId].update('none');
    } else {
      this.charts[canvasId] = new Chart(canvas.getContext('2d'), {
        type,
        data,
        options: {
          responsive: true,
          maintainAspectRatio: true,
          animation: { duration: 600 },
          ...options
        }
      });
    }
  },

  // ==================== DIAGNOSTIC ====================
  async runDiagnostic() {
    const answers = {
      taille_marche: this.questionnaireAnswers.type_client === 'b2c' ? 'grand' : 'moyen',
      marche_valide: this.questionnaireAnswers.stade_projet !== 'idee',
      clients_existants: ['lance', 'croissance'].includes(this.questionnaireAnswers.stade_projet),
      croissance_marche: 'moderate',
      niveau_concurrence: this.questionnaireAnswers.concurrence_directe === 'beaucoup' ? 'fort' : 
                          this.questionnaireAnswers.concurrence_directe === 'aucun' ? 'faible' : 'moyen',
      proposition_valeur_claire: !!this.questionnaireAnswers.description_projet,
      avantage_concurrentiel: !!this.questionnaireAnswers.differentiation,
      strategie_prix: 'alignee',
      canaux_distribution: true,
      niveau_innovation: 'incremental',
      prototype_mvp: ['mvp', 'lance', 'croissance'].includes(this.questionnaireAnswers.stade_projet),
      modele_scalable: this.questionnaireAnswers.modele_revenu?.includes('abonnement') ? 'saas' :
                       this.questionnaireAnswers.modele_revenu?.includes('commission') ? 'marketplace' : 'lineaire',
      automatisation: false,
      taille_equipe: this.questionnaireAnswers.taille_equipe_actuelle === 'solo' ? 1 :
                     this.questionnaireAnswers.taille_equipe_actuelle === '2_3' ? 3 :
                     this.questionnaireAnswers.taille_equipe_actuelle === '4_10' ? 7 : 15,
      fournisseurs_locaux: true,
      politique_environnementale: false
    };

    try {
      const res = await fetch('/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      this.diagnosticData = data;
      document.getElementById('diagEmpty').classList.add('hidden');
      document.getElementById('diagResults').classList.remove('hidden');
      this._renderDiagnostic(data);
    } catch (err) {
      alert('Erreur: ' + err.message);
    }
  },

  _renderDiagnostic(data) {
    // Score circle
    const scoreArc = document.getElementById('diagScoreArc');
    const scoreVal = document.getElementById('diagScoreVal');
    if (scoreArc) {
      const offset = 440 - (440 * data.note_globale / 100);
      scoreArc.setAttribute('stroke-dashoffset', offset);
      scoreArc.setAttribute('stroke', data.grade.couleur);
    }
    if (scoreVal) scoreVal.textContent = Math.round(data.note_globale);

    // Radar chart
    this._createOrUpdateChart('chartRadar', 'radar', {
      labels: Object.keys(data.scores),
      datasets: [{
        label: 'Score',
        data: Object.values(data.scores),
        backgroundColor: 'rgba(46,196,182,0.2)',
        borderColor: '#2EC4B6',
        borderWidth: 2,
        pointBackgroundColor: '#2EC4B6',
        pointRadius: 5
      }]
    }, {
      scales: {
        r: { beginAtZero: true, max: 100, ticks: { stepSize: 20, font: { size: 10 } } }
      },
      plugins: { legend: { display: false } }
    });

    // Dimension cards
    const dimCards = document.getElementById('dimCards');
    let dimHtml = '';
    Object.entries(data.scores).forEach(([dim, score]) => {
      const grade = score >= 70 ? { letter: 'A', cls: 'grade-a' } :
                    score >= 55 ? { letter: 'B', cls: 'grade-b' } :
                    score >= 40 ? { letter: 'C', cls: 'grade-c' } :
                    score >= 25 ? { letter: 'D', cls: 'grade-d' } :
                    { letter: 'F', cls: 'grade-f' };
      const color = score >= 70 ? 'var(--success)' : score >= 40 ? 'var(--warning)' : 'var(--danger)';
      
      dimHtml += `<div class="dim-card animate-slide-up">
        <div class="dim-header">
          <span class="dim-name">${dim}</span>
          <div class="dim-grade ${grade.cls}">${grade.letter}</div>
        </div>
        <div class="dim-score-bar"><div class="dim-score-fill" style="width:${score}%;background:${color}"></div></div>
        <div class="dim-explain">${score}/100 — ${score >= 70 ? 'Point fort' : score >= 40 ? 'À améliorer' : 'Point faible critique'}</div>
      </div>`;
    });
    dimCards.innerHTML = dimHtml;

    // Recommendations
    const recoList = document.getElementById('recoList');
    let recoHtml = '';
    data.recommandations.forEach(rec => {
      const iconColor = rec.priorite === 'haute' ? 'var(--danger)' : rec.priorite === 'moyenne' ? 'var(--warning)' : 'var(--secondary)';
      const iconBg = rec.priorite === 'haute' ? 'rgba(231,76,60,0.1)' : rec.priorite === 'moyenne' ? 'rgba(241,196,15,0.1)' : 'rgba(46,196,182,0.1)';
      recoHtml += `<li class="reco-item">
        <div class="reco-icon" style="background:${iconBg};color:${iconColor}"><i class="fas fa-${rec.priorite === 'haute' ? 'exclamation-triangle' : rec.priorite === 'moyenne' ? 'lightbulb' : 'check-circle'}"></i></div>
        <div class="reco-text">
          <strong>${rec.dimension}</strong>
          ${rec.conseil}
          <ul style="margin-top:8px;padding-left:16px;font-size:13px;color:var(--text-light)">
            ${rec.actions.map(a => '<li>' + a + '</li>').join('')}
          </ul>
        </div>
      </li>`;
    });
    recoList.innerHTML = recoHtml;
  },

  // ==================== PIVOT SCENARIOS ====================
  async loadPivots() {
    const params = {
      panier_moyen: parseFloat(document.getElementById('sim_panier')?.value || 89),
      cout_produits: parseFloat(document.getElementById('sim_cout_produits')?.value || 45),
      cout_transport: parseFloat(document.getElementById('sim_cout_transport')?.value || 8),
      charges_fixes: parseFloat(document.getElementById('sim_charges')?.value || 3000),
      commandes_mois: parseFloat(document.getElementById('sim_commandes')?.value || 200),
      marge_pct: 25,
      secteur: this.questionnaireAnswers.secteur || 'ecommerce'
    };

    document.getElementById('pivotEmpty').classList.add('hidden');
    document.getElementById('pivotResults').classList.remove('hidden');

    const pivotTypes = ['premium', 'volume', 'niche', 'b2b', 'abonnement'];
    const grid = document.getElementById('pivotGrid');
    grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Génération des scénarios…</p></div>';

    try {
      const results = [];
      for (const pt of pivotTypes) {
        const res = await fetch('/api/pivot-scenarios', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...params, pivot_type: pt })
        });
        const data = await res.json();
        if (data.success) results.push(data);
      }

      let html = `<div class="pivot-card">
        <div class="pivot-label current">SITUATION ACTUELLE</div>
        <h3>Votre modèle</h3>
        <table class="pivot-table">
          <tr><td>CA mensuel</td><td>${Math.round(results[0]?.scenario_actuel?.ca_mensuel || 0).toLocaleString('fr-FR')} DT</td></tr>
          <tr><td>Résultat</td><td style="color:${(results[0]?.scenario_actuel?.resultat_mensuel || 0) >= 0 ? 'var(--success)' : 'var(--danger)'}">
            ${Math.round(results[0]?.scenario_actuel?.resultat_mensuel || 0).toLocaleString('fr-FR')} DT</td></tr>
          <tr><td>Seuil</td><td>${results[0]?.scenario_actuel?.seuil_rentabilite || '—'} cmd</td></tr>
        </table>
      </div>`;

      results.forEach(r => {
        const sp = r.scenario_pivot;
        const isReco = r.comparaison.recommendation.verdict === 'recommandé';
        html += `<div class="pivot-card ${isReco ? 'recommended' : ''}">
          <div class="pivot-label option">${isReco ? '⭐ RECOMMANDÉ' : 'OPTION'}</div>
          <h3>${sp.nom}</h3>
          <p style="font-size:13px;color:var(--text-light);margin-bottom:12px">${sp.description}</p>
          <table class="pivot-table">
            <tr><td>CA mensuel</td><td>${Math.round(sp.ca_mensuel).toLocaleString('fr-FR')} DT</td></tr>
            <tr><td>Résultat</td><td style="color:${sp.resultat_mensuel >= 0 ? 'var(--success)' : 'var(--danger)'}">
              ${(sp.resultat_mensuel >= 0 ? '+' : '')}${Math.round(sp.resultat_mensuel).toLocaleString('fr-FR')} DT</td></tr>
            <tr><td>Risque</td><td><span class="risk-badge ${sp.risque === 'faible' ? 'low' : sp.risque === 'moyen' ? 'medium' : 'high'}">${sp.risque}</span></td></tr>
            <tr><td>Transition</td><td>${sp.delai_transition_mois} mois</td></tr>
          </table>
          <div class="recommended-badge">${r.comparaison.recommendation.emoji} ${r.comparaison.recommendation.verdict}</div>
        </div>`;
      });

      grid.innerHTML = html;
    } catch (err) {
      grid.innerHTML = `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  // ==================== PERSONAS ====================
  async loadPersonas() {
    document.getElementById('personasEmpty').classList.add('hidden');
    document.getElementById('personasResults').classList.remove('hidden');
    const grid = document.getElementById('personaGrid');
    grid.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Génération des personas…</p></div>';

    try {
      const res = await fetch('/api/persona-simulator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          secteur: this.questionnaireAnswers.secteur || 'ecommerce',
          type_produit: this.questionnaireAnswers.description_projet || 'Produit',
          prix_range: 'moyen'
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      const colors = ['c1', 'c2', 'c3', 'c4'];
      let html = '';
      data.personas.forEach((p, i) => {
        html += `<div class="persona-card animate-slide-up" style="animation-delay:${i * 0.1}s">
          <div class="persona-avatar ${colors[i % 4]}">${p.nom[0]}</div>
          <h3>${p.nom}, ${p.age} ans</h3>
          <div class="persona-demo">${p.demographiques.genre} · ${p.demographiques.localisation} · ${p.demographiques.situation}</div>
          <p style="font-size:13px;color:var(--text-light);margin-bottom:12px">${p.profil}</p>
          
          <div class="persona-section">
            <h4>Points de douleur</h4>
            <ul>${p.pain_points.slice(0, 3).map(pp => '<li>' + pp + '</li>').join('')}</ul>
          </div>
          
          <div class="persona-section">
            <h4>Motivations d'achat</h4>
            <ul>${p.motivations.slice(0, 3).map(m => '<li>' + m + '</li>').join('')}</ul>
          </div>
          
          <div class="persona-section">
            <h4>Disposition à payer</h4>
            <p style="font-weight:600;color:var(--dark)">Max: ${p.willingness_to_pay.max_dt} DT</p>
            <div class="wtp-bar"><div class="wtp-fill" style="width:${Math.min(100, p.willingness_to_pay.max_dt / 2)}%"></div></div>
          </div>
          
          <div class="persona-section" style="margin-top:14px;padding:12px;background:var(--gray-100);border-radius:8px">
            <h4>Scénario d'utilisation</h4>
            <p style="font-style:italic">${p.scenario_utilisation}</p>
          </div>
        </div>`;
      });

      if (data.conseil_ciblage) {
        html += `<div class="persona-card animate-slide-up" style="border-left:4px solid var(--secondary)">
          <h3 style="color:var(--secondary)"><i class="fas fa-bullseye"></i> Conseil de ciblage</h3>
          <p style="font-size:14px;margin-top:12px">${data.conseil_ciblage.strategie_prix}</p>
          <p style="font-size:13px;color:var(--text-light);margin-top:8px">${data.conseil_ciblage.conseil}</p>
          <div class="persona-section" style="margin-top:12px">
            <h4>Canaux recommandés</h4>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">
              ${data.conseil_ciblage.canaux_recommandes.map(c => `<span style="padding:4px 12px;background:rgba(46,196,182,0.1);color:var(--secondary-dark);border-radius:12px;font-size:12px;font-weight:600">${c}</span>`).join('')}
            </div>
          </div>
        </div>`;
      }

      grid.innerHTML = html;
    } catch (err) {
      grid.innerHTML = `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  // ==================== BUSINESS PLAN ====================
  async generateBP() {
    document.getElementById('bpEmpty').classList.add('hidden');
    const content = document.getElementById('bpContent');
    content.classList.remove('hidden');
    content.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Génération du Business Plan…</p></div>';

    try {
      const res = await fetch('/api/business-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          answers: this.questionnaireAnswers,
          simulation: this.simulationData || {}
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      let html = `<div style="margin-bottom:24px;padding:24px;background:linear-gradient(135deg, #ffffff 0%, #fff7f5 50%, #f0fdf9 100%);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow-sm)">
        <h2 style="color:var(--neutral-900);font-size:22px;margin-bottom:4px;font-weight:800">${data.business_plan.titre}</h2>
        <p style="color:var(--text-muted);font-size:14px">${data.business_plan.date_generation}</p>
      </div>`;

      data.business_plan.sections.forEach((section, i) => {
        html += `<div class="bp-section ${i === 0 ? 'open' : ''}" id="bp-${section.id}">
          <button class="bp-toggle" onclick="this.parentElement.classList.toggle('open')">
            <span>${section.titre}</span>
            <i class="fas fa-chevron-down chevron"></i>
          </button>
          <div class="bp-content">
            <div class="bp-inner">
              <p>${section.contenu}</p>
              ${section.points_cles ? '<ul style="margin-top:12px">' + section.points_cles.map(p => '<li>' + p + '</li>').join('') + '</ul>' : ''}
              ${section.opportunites ? '<div style="margin-top:16px"><strong style="color:var(--success)">Opportunités :</strong><ul>' + section.opportunites.map(o => '<li>' + o + '</li>').join('') + '</ul></div>' : ''}
              ${section.menaces ? '<div style="margin-top:12px"><strong style="color:var(--danger)">Menaces :</strong><ul>' + section.menaces.map(m => '<li>' + m + '</li>').join('') + '</ul></div>' : ''}
              ${section.actions ? '<div style="margin-top:16px"><strong>Plan d\'action :</strong>' + section.actions.map(a => `<div style="display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--gray-100)"><span style="font-weight:700;color:var(--primary);min-width:80px">${a.mois}</span><div><strong>${a.action}</strong><p style="font-size:13px;color:var(--text-light)">${a.details}</p></div></div>`).join('') + '</div>' : ''}
              ${section.matrice_risques ? '<div style="margin-top:16px">' + section.matrice_risques.map(r => `<div style="padding:12px;margin-bottom:8px;border-left:3px solid ${r.principal ? 'var(--danger)' : 'var(--gray-300)'};background:var(--gray-100);border-radius:0 8px 8px 0"><strong>${r.risque}</strong> <span class="risk-badge ${r.impact === 'critique' || r.impact === 'élevé' ? 'high' : r.impact === 'moyen' ? 'medium' : 'low'}">${r.impact}</span><p style="font-size:13px;margin-top:4px;color:var(--text-light)">${r.mitigation}</p></div>`).join('') + '</div>' : ''}
              ${section.financements_recommandes ? '<div style="margin-top:16px"><strong>Sources de financement :</strong>' + section.financements_recommandes.map(f => `<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--gray-100);font-size:13px"><span><strong>${f.source}</strong> (${f.type})</span><span class="risk-badge ${f.pertinence === 'haute' ? 'low' : 'medium'}">${f.pertinence}</span></div>`).join('') + '</div>' : ''}
            </div>
          </div>
        </div>`;
      });

      content.innerHTML = html;
    } catch (err) {
      content.innerHTML = `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  exportBP() {
    document.body.classList.add('printing');
    const cleanup = () => {
      document.body.classList.remove('printing');
      window.removeEventListener('afterprint', cleanup);
    };
    window.addEventListener('afterprint', cleanup);
    setTimeout(cleanup, 1500);
    window.print();
  },

  // ==================== RAPPORT COMPLET ====================
  generateRapport() {
    const hasQ = Object.keys(this.questionnaireAnswers).length > 0;
    const hasS = !!this.simulationData;
    const hasD = !!this.diagnosticData;
    
    if (!hasQ && !hasS && !hasD) return; // show empty state
    
    document.getElementById('rapportEmpty')?.classList.add('hidden');
    document.getElementById('rapportData')?.classList.remove('hidden');
    
    const secteurLabels = {
      livraison: 'Livraison & Logistique', ecommerce: 'E-Commerce',
      services: 'Services Numériques', foodtech: 'Food Tech',
      edtech: 'EdTech', healthtech: 'HealthTech',
      fintech: 'FinTech', agritech: 'AgriTech', autre: 'Autre'
    };

    const stadeLabels = {
      idee: 'Juste une idée',
      mvp: 'J\'ai un MVP / prototype',
      lance: 'Déjà lancé, premiers clients',
      croissance: 'En croissance, je veux scaler'
    };

    const locLabels = {
      grand_tunis: 'Grand Tunis',
      sahel: 'Sahel (Sousse, Monastir, Mahdia)',
      sfax: 'Sfax',
      autre_region: 'Autre région',
      national: 'National (tout le pays)',
      international: 'International'
    };
    
    let html = '<div class="rapport-grid">';
    
    // Project summary
    html += `<div class="rapport-section">
      <h2><i class="fas fa-rocket" style="color:var(--primary)"></i> Votre Projet</h2>
      <div class="rapport-row"><span>Secteur</span><strong>${secteurLabels[this.questionnaireAnswers.secteur] || this.questionnaireAnswers.secteur || 'Non défini'}</strong></div>
      <div class="rapport-row"><span>Description</span><strong>${this.questionnaireAnswers.description_projet || 'Non défini'}</strong></div>
      <div class="rapport-row"><span>Stade</span><strong>${stadeLabels[this.questionnaireAnswers.stade_projet] || this.questionnaireAnswers.stade_projet || 'Non défini'}</strong></div>
      <div class="rapport-row"><span>Localisation</span><strong>${locLabels[this.questionnaireAnswers.localisation] || this.questionnaireAnswers.localisation || 'Non défini'}</strong></div>
    </div>`;
    
    // Simulation KPIs
    if (hasS) {
      const d = this.simulationData;
      html += `<div class="rapport-section">
        <h2><i class="fas fa-chart-line" style="color:var(--secondary)"></i> Stress-Test Financier</h2>
        <div class="rapport-row"><span>Résultat mensuel (normal)</span><strong style="color:${d.avant.resultat_mensuel >= 0 ? 'var(--success)' : 'var(--danger)'}">${d.avant.resultat_mensuel.toLocaleString('fr-FR')} DT</strong></div>
        <div class="rapport-row"><span>Résultat après chocs</span><strong style="color:${d.apres.resultat_mensuel >= 0 ? 'var(--success)' : 'var(--danger)'}">${d.apres.resultat_mensuel.toLocaleString('fr-FR')} DT</strong></div>
        <div class="rapport-row"><span>Seuil de rentabilité</span><strong>${d.avant.seuil_rentabilite || '∞'} commandes/mois</strong></div>
        <div class="rapport-row"><span>Marge unitaire</span><strong>${d.avant.marge_unitaire.toFixed(2)} DT</strong></div>
        <div class="rapport-row"><span>Variation sous stress</span><strong style="color:${d.variation_resultat >= 0 ? 'var(--success)' : 'var(--danger)'}">${d.variation_resultat >= 0 ? '+' : ''}${d.variation_resultat.toLocaleString('fr-FR')} DT (${d.variation_resultat_pct}%)</strong></div>
      </div>`;
    }
    
    // Diagnostic
    if (hasD) {
      const d = this.diagnosticData;
      html += `<div class="rapport-section">
        <h2><i class="fas fa-stethoscope" style="color:var(--warning)"></i> Diagnostic de Viabilité</h2>
        <div class="rapport-row"><span>Score global</span><strong style="color:${d.grade.couleur}">${d.note_globale.toFixed(1)}/100 — Grade ${d.grade.lettre} (${d.grade.label})</strong></div>
        <div class="rapport-row"><span>Points forts</span><strong style="color:var(--success)">${d.forces.join(', ') || 'Aucun'}</strong></div>
        <div class="rapport-row"><span>Points faibles</span><strong style="color:var(--danger)">${d.faiblesses.join(', ') || 'Aucun'}</strong></div>
        ${Object.entries(d.scores).map(([k, v]) => `<div class="rapport-row"><span>${k}</span><div style="display:flex;align-items:center;gap:12px;flex:1"><div style="flex:1;background:var(--gray-200);border-radius:4px;height:8px"><div style="width:${v}%;background:${v >= 70 ? 'var(--success)' : v >= 40 ? 'var(--warning)' : 'var(--danger)'};height:100%;border-radius:4px"></div></div><strong>${v}/100</strong></div></div>`).join('')}
      </div>`;
    }
    
    // Alertes
    if (hasS && this.simulationData.alerte) {
      html += `<div class="rapport-section rapport-full">
        <h2><i class="fas fa-bell" style="color:var(--danger)"></i> Alertes & Recommandations</h2>
        ${this.simulationData.alerte.map(a => `<div class="error-banner" style="margin-bottom:8px;background:${a.niveau === 'critique' ? 'rgba(231,76,60,0.08)' : a.niveau === 'attention' ? 'rgba(241,196,15,0.08)' : 'rgba(46,196,182,0.08)'}; border-color:${a.niveau === 'critique' ? 'rgba(231,76,60,0.2)' : a.niveau === 'attention' ? 'rgba(241,196,15,0.2)' : 'rgba(46,196,182,0.2)'}; color:${a.niveau === 'critique' ? 'var(--danger)' : a.niveau === 'attention' ? '#c89e00' : 'var(--secondary-dark)'}">${a.message}</div>`).join('')}
      </div>`;
    }
    
    html += '</div>';
    document.getElementById('rapportData').innerHTML = html;
  },

  // ==================== AI ADVICE ====================
  async askAdvice() {
    const input = document.getElementById('adviceInput');
    const question = input?.value?.trim();
    if (!question && !this.questionnaireAnswers.secteur) {
      alert('Veuillez saisir une question ou compléter le questionnaire d\'abord.');
      return;
    }

    const chatEl = document.getElementById('adviceChat');
    const emptyEl = document.getElementById('adviceEmpty');
    if (emptyEl) emptyEl.classList.add('hidden');

    // Add user message
    if (question) {
      chatEl.innerHTML += `<div class="advice-card" style="border-left-color:var(--gray-300);background:var(--gray-100)">
        <p style="font-size:14px"><i class="fas fa-user" style="color:var(--primary);margin-right:8px"></i> ${question}</p>
      </div>`;
      input.value = '';
    }

    // Loading
    chatEl.innerHTML += '<div class="loading-state" id="adviceLoading" style="padding:20px"><div class="spinner"></div></div>';

    try {
      const sim = this.simulationData;
      const margeEst = sim?.avant?.marge_brute_pct || 25;
      const resultatEst = sim?.avant?.resultat_mensuel || 0;

      // Build rich context with real numbers for AI
      const contexteChiffres = sim ? [
        `Résultat mensuel normal: ${sim.avant.resultat_mensuel.toLocaleString('fr-FR')} DT`,
        `Résultat après stress-test: ${sim.apres.resultat_mensuel.toLocaleString('fr-FR')} DT`,
        `Marge par commande: ${sim.avant.marge_unitaire.toFixed(2)} DT`,
        `Seuil de rentabilité: ${sim.avant.seuil_rentabilite || '?'} commandes/mois`,
        `Couverture charges fixes: ${sim.apres.taux_couverture.toFixed(0)}%`,
        `Impact transport: ${sim.decomposition_chocs.impact_transport.toLocaleString('fr-FR')} DT`,
        `Impact baisse demande: ${sim.decomposition_chocs.impact_demande.toLocaleString('fr-FR')} DT`,
        `Variation sous stress: ${sim.variation_resultat_pct}%`
      ] : [];

      const res = await fetch('/api/ai-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          secteur: this.questionnaireAnswers.secteur || 'ecommerce',
          stade: this.questionnaireAnswers.stade_projet || 'idee',
          budget: this.questionnaireAnswers.budget_initial || 'moyen',
          type_client: this.questionnaireAnswers.type_client || 'b2c',
          marge_pct: margeEst,
          resultat_mensuel: resultatEst,
          commandes_mois: parseFloat(document.getElementById('sim_commandes')?.value || 200),
          panier_moyen: parseFloat(document.getElementById('sim_panier')?.value || 89),
          cout_transport: parseFloat(document.getElementById('sim_cout_transport')?.value || 8),
          charges_fixes: parseFloat(document.getElementById('sim_charges')?.value || 3000),
          seuil_rentabilite: sim?.avant?.seuil_rentabilite || null,
          variation_resultat_pct: sim?.variation_resultat_pct || 0,
          contexte_chiffres: contexteChiffres,
          question_posee: question || null,
          concurrence: this.questionnaireAnswers.concurrence_directe || 'moyen',
          risque_principal: this.questionnaireAnswers.risque_principal || 'marche',
          modele_revenu: this.questionnaireAnswers.modele_revenu || [],
          description_projet: this.questionnaireAnswers.description_projet || ''
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      // Remove loading
      document.getElementById('adviceLoading')?.remove();

      // Score banner
      const sc = data.score_confiance;
      chatEl.innerHTML += `<div class="advice-card" style="border-left-color:${sc.score >= 70 ? 'var(--success)' : sc.score >= 50 ? 'var(--warning)' : 'var(--danger)'}">
        <div class="advice-header">
          <span style="font-size:28px">${sc.emoji}</span>
          <div>
            <strong style="font-size:18px">${sc.label}</strong>
            <span style="font-size:14px;color:var(--text-light)"> — Score: ${sc.score}/100</span>
          </div>
        </div>
        <p class="advice-text">${data.resume.message}</p>
      </div>`;

      // Advice cards by category
      Object.entries(data.conseils).forEach(([cat, items]) => {
        if (!Array.isArray(items) || !items.length) return;
        items.forEach(item => {
          const prio = item.priorite || 'recommandé';
          const prioCls = prio === 'critique' ? 'critique' : prio === 'haute' ? 'important' : 'recommande';
          chatEl.innerHTML += `<div class="advice-card ${prioCls}">
            <div class="advice-header">
              <span class="advice-badge ${prioCls}">${prio}</span>
              <span class="advice-category">${cat.replace(/_/g, ' ')}</span>
            </div>
            <strong style="display:block;margin-bottom:8px">${item.titre}</strong>
            <p class="advice-text">${item.description}</p>
            ${item.actions ? '<ul style="margin-top:10px;padding-left:20px;font-size:13px;color:var(--text)">' + item.actions.map(a => '<li style="margin-bottom:4px">' + a + '</li>').join('') + '</ul>' : ''}
            ${item.sources ? '<div style="margin-top:12px">' + item.sources.map(s => `<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:12px;border-bottom:1px solid var(--gray-100)"><span>${s.nom}</span><span style="color:var(--text-light)">${s.montant || ''}</span></div>`).join('') + '</div>' : ''}
          </div>`;
        });
      });

      chatEl.scrollTop = chatEl.scrollHeight;
    } catch (err) {
      document.getElementById('adviceLoading')?.remove();
      chatEl.innerHTML += `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  // ==================== STARTUP SUGGESTIONS ====================
  async getSuggestions() {
    const domain = document.getElementById('sugDomain')?.value;
    const budget = document.getElementById('sugBudget')?.value || '5000-20000';
    const skills = document.getElementById('sugSkills')?.value || '';

    if (!domain) {
      alert('Veuillez sélectionner un domaine.');
      return;
    }

    const budgetMap = {
      '0-5000': 'tres_petit',
      '5000-20000': 'petit',
      '20000-50000': 'moyen',
      '50000+': 'grand'
    };

    const container = document.getElementById('sugResults');
    container.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Recherche des meilleures idées…</p></div>';

    try {
      const res = await fetch('/api/startup-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          domain: domain.replace('-', ''),
          budget_range: budgetMap[budget] || 'moyen',
          skills: skills.split(',').map(s => s.trim()).filter(Boolean)
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error);

      let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px">';
      data.suggestions.forEach((s, i) => {
        const riskCls = s.risque === 'faible' ? 'low' : s.risque === 'moyen' ? 'medium' : 'high';
        html += `<div class="suggestion-card animate-slide-up" style="animation-delay:${i * 0.1}s">
          <h3>${s.nom}</h3>
          <p class="suggestion-desc">${s.description}</p>
          <div class="suggestion-meta">
            <div class="meta-row"><span>Investissement</span><strong>${s.investissement_initial_dt.toLocaleString('fr-FR')} DT</strong></div>
            <div class="meta-row"><span>Revenus estimés/mois</span><strong style="color:var(--success)">${s.revenus_mensuels_estimes_dt.toLocaleString('fr-FR')} DT</strong></div>
            <div class="meta-row"><span>ROI estimé</span><strong>${s.roi_estime_mois || '—'} mois</strong></div>
            <div class="meta-row"><span>Risque</span><span class="risk-badge ${riskCls}">${s.risque}</span></div>
            <div class="meta-row"><span>Matching</span><strong style="color:var(--secondary)">${s.score_matching}%</strong></div>
            <div style="margin-top:8px">
              <span style="font-size:12px;color:var(--text-light)">Opportunité de marché</span>
              <div class="opportunity-gauge"><div class="opportunity-fill" style="width:${Math.min(100, s.score_matching)}%"></div></div>
            </div>
          </div>
          ${s.dans_budget ? '<div class="recommended-badge" style="margin-top:12px"><i class="fas fa-check"></i> Dans votre budget</div>' : ''}
          <button class="btn btn-sm btn-ghost" style="width:100%;margin-top:12px" onclick="App._exploreSuggestion('${s.nom}')">
            <i class="fas fa-arrow-right"></i> Explorer cette idée
          </button>
        </div>`;
      });
      html += '</div>';
      container.innerHTML = html;
    } catch (err) {
      container.innerHTML = `<div class="error-banner"><i class="fas fa-exclamation-circle"></i> ${err.message}</div>`;
    }
  },

  _exploreSuggestion(name) {
    this.questionnaireAnswers.description_projet = name;
    this.navigateTo('questionnaire');
  }
};

// ==================== BOOT ====================
document.addEventListener('DOMContentLoaded', () => App.init());

// Enter key for advice input
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && e.target.id === 'adviceInput') {
    App.askAdvice();
  }
});
