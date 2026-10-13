/*
 * relevo.js - logica do programa Relevo: abre o arquivo, formata em braille, mostra as folhas
 * e conversa com a impressora pela porta USB (Web Serial, Edge ou Chrome).
 */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  window.addEventListener("error", function (e) { var g = $("erroGlobal"); g.hidden = false; g.textContent = "Erro no programa: " + e.message; });
  if (window.pdfjsLib) window.pdfjsLib.GlobalWorkerOptions.workerSrc = "lib/pdf.worker.min.js";

  var EXEMPLO = "# A impressora braille da escola\n\n" +
    "Este texto foi formatado **sozinho** pelo programa. Em braille não existe letra grande nem negrito: o título fica no centro, " +
    "entre linhas em branco, e o parágrafo começa na terceira cela.\n\n" +
    "## O que ela faz\n\n- lê arquivos do Word, PDF e texto\n- formata nas normas brasileiras\n- imprime 30 celas por linha e 23 linhas por folha\n\n" +
    "## Um poema\n\n> Minha terra tem palmeiras,\n> Onde canta o Sabiá;\n\nFeito em 2026, com 38 peças impressas e 7 chapas de MDF.\n";

  var doc = null, brfPronto = null, nomeArquivo = "documento", feitas = {}, atual = 0;
  var porta = null, escritor = null, fila = "", espera = null, ocupado = false, cancelou = false;

  // ------------------------------------------------------------------ abas
  var ABAS = ["Documento", "Impressora", "Ajuda"];
  function aba(nome) {
    ABAS.forEach(function (a) {
      $("tab" + a).hidden = a !== nome;
      $("aba" + a).setAttribute("aria-selected", a === nome ? "true" : "false");
    });
    if (nome === "Documento") setTimeout(redesenhaVisiveis, 30);
  }
  ABAS.forEach(function (a) { $("aba" + a).addEventListener("click", function () { aba(a); }); });

  // ------------------------------------------------------------------ configuracao
  function cfg() {
    return { celas: +$("cCelas").value || 30, linhasPagina: +$("cLinhas").value || 23, recuoParagrafo: +$("cRecuo").value || 0,
             numerarPaginas: $("cNumerar").checked, paginaTinta: $("cTinta").checked, tituloCentralizado: $("cCentro").checked,
             sublinharTitulo: $("cSublinha").checked, destaques: $("cDestaque").checked, capituloPaginaNova: $("cCapitulo").checked };
  }
  function margens() { return { me: +$("pMe").value || 20, mt: +$("pMt").value || 12 }; }
  var CAMPOS = ["cCelas", "cLinhas", "cRecuo", "cNumerar", "cTinta", "cCentro", "cSublinha", "cDestaque", "cCapitulo", "pMe", "pMt", "vTinta"];
  function guarda() {
    try {
      var o = {};
      CAMPOS.forEach(function (id) { var e = $(id); o[id] = e.type === "checkbox" ? e.checked : e.value; });
      localStorage.setItem("relevo.cfg", JSON.stringify(o));
      if (!brfPronto) localStorage.setItem("relevo.texto", $("texto").value.slice(0, 400000));
    } catch (e) { /* sem armazenamento: segue sem lembrar */ }
  }
  function lembra() {
    try {
      var o = JSON.parse(localStorage.getItem("relevo.cfg") || "{}");
      CAMPOS.forEach(function (id) { if (o[id] === undefined) return; var e = $(id); if (e.type === "checkbox") e.checked = !!o[id]; else e.value = o[id]; });
      return localStorage.getItem("relevo.texto");
    } catch (e) { return null; }
  }

  // ------------------------------------------------------------------ formatar e mostrar
  var espEdicao = null;
  function agenda() { clearTimeout(espEdicao); espEdicao = setTimeout(refaz, 220); }
  function refaz() {
    var c = cfg();
    feitas = {};
    doc = brfPronto ? Formatador.deBRF(brfPronto, c) : Formatador.formata($("texto").value, c);
    var t = doc.totais, pontos = 0, linhas = 0, tempo = 0;
    var lc = leiaute();
    doc.paginas.forEach(function (p) {
      var pg = Leiaute.pagina(p.linhas.map(function (l) { return l.celas; }), lc);
      pontos += pg.pontos.length; linhas += p.linhas.length; tempo += Leiaute.tempo(pg, lc) + 25;
    });
    var vazio = !pontos;
    $("resumo").innerHTML = vazio ? "Abra um arquivo ou escreva o texto para ver as folhas em braille." :
      "<strong>" + doc.paginas.length + (doc.paginas.length === 1 ? " folha" : " folhas") + "</strong> · " + linhas + " linhas · " +
      pontos.toLocaleString("pt-BR") + " pontos · cerca de " + (tempo < 100 ? Math.round(tempo) + " s" : Math.round(tempo / 60) + " min") + " de impressão";
    var av = [];
    var semCela = doc.avisos.filter(function (a) { return a.length <= 2; });
    if (semCela.length) av.push("Sem sinal braille (viraram espaço): " + semCela.join(" "));
    var maiorLinha = 0;
    doc.paginas.forEach(function (p) { p.linhas.forEach(function (l) { maiorLinha = Math.max(maiorLinha, l.celas.length); }); });
    if (maiorLinha > Leiaute.celasQueCabem(lc)) av.push("Há linha com " + maiorLinha + " celas e o carro só alcança " + Leiaute.celasQueCabem(lc) + ": o que passar não é impresso.");
    var muitas = doc.paginas.reduce(function (m, p) { return Math.max(m, p.linhas.length); }, 0);
    if (muitas > Leiaute.linhasQueCabem(lc)) av.push("Há folha com " + muitas + " linhas e só cabem " + Leiaute.linhasQueCabem(lc) + ".");
    if (c.celas > Leiaute.celasQueCabem(lc)) av.push("Com esta margem cabem no máximo " + Leiaute.celasQueCabem(lc) + " celas por linha.");
    if (c.linhasPagina > Leiaute.linhasQueCabem(lc)) av.push("Com esta margem cabem no máximo " + Leiaute.linhasQueCabem(lc) + " linhas por folha.");
    $("avisos").textContent = av.join(" ");
    montaPaginas(vazio);
    habilita();
    guarda();
  }
  function leiaute() { var m = margens(), c = cfg(); return Leiaute.config({ margemEsq: m.me, margemTopo: m.mt, celasPorLinha: c.celas, linhasPorPagina: c.linhasPagina }); }

  var observador = null;
  function montaPaginas(vazio) {
    var cx = $("paginas");
    cx.textContent = "";
    if (observador) observador.disconnect();
    if (vazio) {
      var d = document.createElement("div");
      d.className = "vazio"; d.textContent = "As folhas em braille aparecem aqui.";
      cx.appendChild(d); $("pagAtual").textContent = ""; return;
    }
    observador = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) { if (e.isIntersecting && !e.target.dataset.ok) desenha(e.target); });
    }, { rootMargin: "500px 0px" });
    doc.paginas.forEach(function (p, i) {
      var f = document.createElement("div");
      f.className = "folha"; f.dataset.i = i;
      f.style.aspectRatio = "210 / 297";
      f.setAttribute("role", "img");
      f.setAttribute("aria-label", "Folha " + (i + 1) + " de " + doc.paginas.length + ", " + p.linhas.length + " linhas. " +
        p.linhas.slice(0, 4).map(function (l) { return l.tinta; }).filter(Boolean).join(" / "));
      var n = document.createElement("span");
      n.className = "num"; n.textContent = "folha " + (i + 1) + " de " + doc.paginas.length;
      f.appendChild(n);
      cx.appendChild(f);
      observador.observe(f);
    });
    marcaAtual();
  }
  function desenha(f) {
    var i = +f.dataset.i, p = doc.paginas[i];
    if (!p) return;
    var cv = f.querySelector("canvas");
    if (!cv) { cv = document.createElement("canvas"); f.insertBefore(cv, f.firstChild); }
    var larg = f.clientWidth || 600, dpr = Math.min(window.devicePixelRatio || 1, 2);
    cv.width = Math.round(larg * dpr); cv.height = Math.round(larg * dpr * 297 / 210);
    var g = cv.getContext("2d"), s = cv.width / 210, m = margens(), c = doc.config, tinta = $("vTinta").checked;
    g.fillStyle = "#fbfaf5"; g.fillRect(0, 0, cv.width, cv.height);
    // faixa do fim da folha, que os roletes nao alcancam
    g.fillStyle = "#f1ede0"; g.fillRect(0, (297 - 48) * s, cv.width, 48 * s);
    g.fillStyle = "#a59d88"; g.font = (3 * s) + "px system-ui, sans-serif"; g.textAlign = "center";
    g.fillText("os últimos 48 mm ficam atrás dos roletes e não são impressos", 105 * s, (297 - 22) * s);
    // area do texto
    g.strokeStyle = "#e3dccb"; g.lineWidth = Math.max(1, 0.2 * s); g.setLineDash([1.2 * s, 1.2 * s]);
    g.strokeRect((m.me - 2.5) * s, (m.mt - 4.5) * s, ((c.celas - 1) * 6 + 2.5 + 5) * s, ((c.linhasPagina - 1) * 10 + 5 + 7) * s);
    g.setLineDash([]); g.textAlign = "left";
    var prontas = feitas[i] || 0;
    p.linhas.forEach(function (l, li) {
      var v = m.mt + li * 10;
      if (tinta && l.tinta) {
        var c0 = 0;
        while (c0 < l.celas.length && l.celas[c0] === 0) c0++;
        g.fillStyle = "#9a7b45"; g.font = (2.7 * s) + "px system-ui, sans-serif";
        var x0 = (m.me + c0 * 6 - 0.6) * s, maxL = cv.width - x0 - 3 * s, txt = l.tinta;
        while (txt.length > 3 && g.measureText(txt).width > maxL) txt = txt.slice(0, -2);
        g.fillText(txt === l.tinta ? txt : txt + "…", x0, (v - 1.9) * s);
      }
      g.fillStyle = li < prontas ? "#17703a" : "#20242b";
      l.celas.forEach(function (cela, ci) {
        if (!cela) return;
        var u = m.me + ci * 6;
        for (var b = 0; b < 6; b++) if (cela & (1 << b)) {
          g.beginPath(); g.arc((u + (b > 2 ? 2.5 : 0)) * s, (v + (b % 3) * 2.5) * s, 0.72 * s, 0, 6.3); g.fill();
        }
      });
    });
    f.dataset.ok = "1";
  }
  function redesenhaVisiveis() { Array.prototype.forEach.call(document.querySelectorAll(".folha[data-ok]"), desenha); }
  function marcaAtual() {
    var fs = document.querySelectorAll(".folha"), melhor = 0;
    for (var i = 0; i < fs.length; i++) { var r = fs[i].getBoundingClientRect(); if (r.bottom > 160) { melhor = i; break; } }
    atual = melhor;
    for (var k = 0; k < fs.length; k++) fs[k].classList.toggle("atual", k === atual && fs.length > 1);
    $("pagAtual").textContent = fs.length > 1 ? "à vista: folha " + (atual + 1) + " de " + fs.length : "";
  }
  var espRol = null;
  window.addEventListener("scroll", function () { if (!espRol) espRol = setTimeout(function () { espRol = null; marcaAtual(); }, 120); }, { passive: true });
  var espTam = null;
  window.addEventListener("resize", function () { clearTimeout(espTam); espTam = setTimeout(redesenhaVisiveis, 200); });

  // ------------------------------------------------------------------ abrir arquivo
  async function abre(arq) {
    if (!arq) return;
    $("origem").textContent = "Lendo " + arq.name + "…";
    try {
      var r = await Importar.importa(arq.name, await arq.arrayBuffer(), window.pdfjsLib);
      nomeArquivo = arq.name.replace(/\.[^.]+$/, "") || "documento";
      if (r.pronto) { brfPronto = r.texto; $("texto").value = "Arquivo braille pronto: " + arq.name + "\n(as linhas já vêm formatadas; nada a editar aqui)"; $("texto").disabled = true; }
      else { brfPronto = null; $("texto").disabled = false; $("texto").value = r.texto; }
      var palavras = r.pronto ? 0 : (r.texto.match(/[^\s#*>\-=]+/g) || []).length;
      $("origem").textContent = arq.name + " · " + r.tipo + (palavras ? " · " + palavras.toLocaleString("pt-BR") + " palavras" : "") +
        ". Confira os títulos e as listas no texto abaixo.";
      refaz();
      window.scrollTo({ top: 0 });
    } catch (e) { $("origem").textContent = "Não consegui ler " + arq.name + ": " + e.message; }
  }
  var zona = $("solta");
  zona.addEventListener("click", function () { $("arquivo").click(); });
  zona.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("arquivo").click(); } });
  $("arquivo").addEventListener("change", function () { abre(this.files[0]); this.value = ""; });
  ["dragenter", "dragover"].forEach(function (ev) { window.addEventListener(ev, function (e) { e.preventDefault(); zona.classList.add("sobre"); }); });
  ["dragleave", "drop"].forEach(function (ev) { window.addEventListener(ev, function (e) { e.preventDefault(); zona.classList.remove("sobre"); }); });
  window.addEventListener("drop", function (e) { if (e.dataTransfer && e.dataTransfer.files.length) { aba("Documento"); abre(e.dataTransfer.files[0]); } });

  // ------------------------------------------------------------------ ferramentas do texto
  function editavel() { if (brfPronto) { brfPronto = null; $("texto").disabled = false; $("texto").value = ""; } return $("texto"); }
  Array.prototype.forEach.call(document.querySelectorAll(".ferramentas button"), function (b) {
    b.addEventListener("click", function () {
      var t = editavel(), v = t.value, a = t.selectionStart, z = t.selectionEnd;
      if (b.dataset.marca) {
        var ini = v.lastIndexOf("\n", a - 1) + 1, fim = v.indexOf("\n", z);
        if (fim < 0) fim = v.length;
        var novo = v.slice(ini, fim).split("\n").map(function (l) {
          var limpo = l.replace(/^\s*(#{1,6}\s+|[-*+>]\s+)/, "");
          return l.indexOf(b.dataset.marca) === 0 ? limpo : (limpo ? b.dataset.marca + limpo : limpo);
        }).join("\n");
        t.value = v.slice(0, ini) + novo + v.slice(fim);
        t.setSelectionRange(ini, ini + novo.length);
      } else if (b.dataset.envolve) {
        var m = b.dataset.envolve, sel = v.slice(a, z) || "texto";
        t.value = v.slice(0, a) + m + sel + m + v.slice(z);
        t.setSelectionRange(a + m.length, a + m.length + sel.length);
      } else if (b.dataset.insere) {
        t.value = v.slice(0, a) + b.dataset.insere + v.slice(z);
        t.setSelectionRange(a + b.dataset.insere.length, a + b.dataset.insere.length);
      } else return;
      t.focus(); refaz();
    });
  });
  $("btExemplo").addEventListener("click", function () { editavel().value = EXEMPLO; $("origem").textContent = ""; nomeArquivo = "exemplo"; refaz(); });
  $("texto").addEventListener("input", agenda);
  CAMPOS.forEach(function (id) { $(id).addEventListener("input", agenda); });

  // ------------------------------------------------------------------ salvar e simular
  $("btBrf").addEventListener("click", function () {
    if (!doc) return;
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([Formatador.paraBRF(doc.paginas)], { type: "text/plain" }));
    a.download = nomeArquivo + ".brf";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });
  $("btSim").addEventListener("click", function () {
    if (!doc || !doc.paginas[atual]) return;
    var hex = doc.paginas[atual].linhas.map(function (l) { return BraillePT.paraHex(l.celas); }).join(".");
    window.open("../simulador/index.html?auto=1&celas=" + hex, "_blank");
  });

  // ------------------------------------------------------------------ serial
  function reg(txt, env) {
    var r = $("registro");
    r.textContent += (env ? "> " : "") + txt + "\n";
    if (r.textContent.length > 30000) r.textContent = r.textContent.slice(-20000);
    r.scrollTop = r.scrollHeight;
  }
  function estado(txt, classe) { var e = $("estado"); e.textContent = txt; e.className = "pilula " + (classe || ""); }
  function habilita() {
    var on = !!porta, tem = !!(doc && doc.paginas.some(function (p) { return p.linhas.length; }));
    Array.prototype.forEach.call(document.querySelectorAll("button[data-cmd], #btEnviar, #btAplicar, #btAutoteste"), function (b) { b.disabled = !on || ocupado; });
    $("btImprimir").disabled = !on || ocupado || !tem;
    $("btImprimir").title = on ? "" : "Conecte a impressora primeiro";
    $("btCancelar").disabled = !on || !ocupado;
    $("btConectar").textContent = on ? "Desconectar" : "Conectar";
  }
  async function conecta() {
    if (porta) { await desconecta(); return; }
    if (!("serial" in navigator)) { estado("use o Edge ou o Chrome no computador", "erro"); aba("Impressora"); return; }
    try {
      porta = await navigator.serial.requestPort();
      await porta.open({ baudRate: 115200 });
      escritor = porta.writable.getWriter();
      estado("impressora conectada", "ok");
      reg("porta aberta a 115200");
      le(); habilita();
    } catch (e) { porta = null; estado("não conectou", "erro"); reg("não conectou: " + e.message); habilita(); }
  }
  async function desconecta() {
    try { if (escritor) { escritor.releaseLock(); escritor = null; } if (porta) await porta.close(); } catch (e) { /* porta ja fechada */ }
    porta = null; estado("impressora desconectada"); habilita();
  }
  async function le() {
    var dec = new TextDecoder();
    while (porta && porta.readable) {
      var leitor = porta.readable.getReader();
      try {
        for (;;) {
          var r = await leitor.read();
          if (r.done) break;
          fila += dec.decode(r.value, { stream: true });
          var i;
          while ((i = fila.indexOf("\n")) >= 0) { var lin = fila.slice(0, i).replace(/\r/g, ""); fila = fila.slice(i + 1); recebe(lin); }
        }
      } catch (e) { reg("leitura: " + e.message); if (porta) { estado("a impressora parou de responder", "erro"); } break; }
      finally { try { leitor.releaseLock(); } catch (e2) { /* ja solto */ } }
    }
  }
  var MAPA = { me: "pMe", mt: "pMt", ton: "pTon" };
  function recebe(lin) {
    if (!lin) return;
    reg(lin);
    var m = /^# (\w+)=([-\d.]+)$/.exec(lin);
    if (m && MAPA[m[1]]) { $(MAPA[m[1]]).value = parseFloat(m[2]); agenda(); }
    if (espera && (lin === "ok" || lin === "fim_pagina" || lin.indexOf("erro:") === 0)) { var f = espera; espera = null; f.linhas.push(lin); f.resolve(lin); }
    else if (espera) espera.linhas.push(lin);
    else if (lin.indexOf("# coloque a folha") === 0) estado("coloque a folha nos roletes", "ocupada");
  }
  async function manda(txt) {
    if (!escritor) throw new Error("impressora desconectada");
    reg(txt, true);
    await escritor.write(new TextEncoder().encode(txt + "\n"));
  }
  function cmd(txt, tempoMax) {
    return new Promise(function (resolve, reject) {
      var t = setTimeout(function () { if (espera) { espera = null; reject(new Error("a impressora não respondeu a " + txt)); } }, tempoMax || 180000);
      espera = { linhas: [], resolve: function (r) { clearTimeout(t); resolve(r); } };
      manda(txt).catch(function (e) { clearTimeout(t); espera = null; reject(e); });
    });
  }
  async function cmdOk(txt, tempoMax) { var r = await cmd(txt, tempoMax); if (r !== "ok") throw new Error(r.replace(/^erro: /, "")); }
  async function simples(txt) {
    if (ocupado) return;
    ocupado = true; habilita(); estado("trabalhando…", "ocupada");
    try { var r = await cmd(txt); estado(r === "ok" ? "impressora pronta" : r, r === "ok" ? "ok" : "erro"); }
    catch (e) { estado(e.message, "erro"); }
    ocupado = false; habilita();
  }

  // ------------------------------------------------------------------ imprimir
  function pergunta(titulo, texto) {
    return new Promise(function (resolve) {
      var d = $("dialogo");
      $("dlgTitulo").textContent = titulo; $("dlgTexto").textContent = texto;
      function fim(v) { $("dlgSim").onclick = $("dlgNao").onclick = d.oncancel = null; d.close(); resolve(v); }
      $("dlgSim").onclick = function () { fim(true); };
      $("dlgNao").onclick = function () { fim(false); };
      d.oncancel = function () { fim(false); };
      d.showModal(); $("dlgSim").focus();
    });
  }
  async function imprime() {
    if (ocupado || !doc) return;
    var idx = [];
    doc.paginas.forEach(function (p, i) { if (p.linhas.some(function (l) { return l.celas.length; })) idx.push(i); });
    if ($("quais").value === "atual") idx = idx.filter(function (i) { return i === atual; });
    if (!idx.length) return;
    var total = idx.reduce(function (s, i) { return s + doc.paginas[i].linhas.length; }, 0), m = margens(), c = doc.config, feitasTotal = 0;
    ocupado = true; cancelou = false; feitas = {}; habilita();
    $("barra").hidden = false; $("barra").max = total; $("barra").value = 0;
    try {
      await cmdOk("$S linhas=" + c.linhasPagina);
      await cmdOk("$S me=" + m.me);
      await cmdOk("$S mt=" + m.mt);
      for (var k = 0; k < idx.length; k++) {
        var p = doc.paginas[idx[k]];
        if (k > 0 && !(await pergunta("Folha " + (k + 1) + " de " + idx.length,
          "Tire a folha pronta pela frente e vire-a para ler. Encoste a próxima folha nos roletes, por trás, e clique em Continuar."))) throw new Error("parado na troca de folha");
        estado("folha " + (k + 1) + " de " + idx.length + ": aguardando o papel", "ocupada");
        await cmdOk("$L", 120000);
        estado("imprimindo a folha " + (k + 1) + " de " + idx.length, "ocupada");
        var brancos = 0;
        for (var i = 0; i < p.linhas.length; i++) {
          if (cancelou) throw new Error("cancelado");
          var l = p.linhas[i];
          if (!l.celas.length) { brancos++; }
          else {
            if (brancos) { await cmdOk("$F " + brancos); brancos = 0; }
            await cmdOk("$C " + BraillePT.paraHex(l.celas), 600000);
          }
          feitas[idx[k]] = i + 1; $("barra").value = ++feitasTotal;
          var f = document.querySelector('.folha[data-i="' + idx[k] + '"]');
          if (f && f.dataset.ok) desenha(f);
        }
        await cmdOk("$E", 120000);
      }
      estado("pronto: " + idx.length + (idx.length === 1 ? " folha" : " folhas"), "ok");
    } catch (e) { estado(e.message, "erro"); }
    ocupado = false; habilita();
    setTimeout(function () { $("barra").hidden = true; }, 4000);
  }
  async function cancela() { cancelou = true; try { await manda("!"); } catch (e) { /* desconectada */ } }

  async function aplica() {
    if (ocupado) return;
    ocupado = true; habilita();
    try {
      await cmdOk("$S me=" + $("pMe").value); await cmdOk("$S mt=" + $("pMt").value); await cmdOk("$S ton=" + $("pTon").value);
      estado("ajustes enviados (use Gravar para guardar)", "ok");
    } catch (e) { estado(e.message, "erro"); }
    ocupado = false; habilita();
  }

  // confere o tradutor do firmware com o do programa, frase por frase
  var FRASES = ["abc xyz", "Brasil", "BRASIL", "ação pão àquela", "Olá, mundo!", "2026", "3,14", "1.000", "5a 5k", "10%",
                "12/10/2026", "(a) [b]", "tudo bem? sim!", "guarda-chuva", "a@b", "É à ü õ ô ê", "FEIRA DE CIENCIAS"];
  async function autoteste() {
    if (ocupado) return;
    ocupado = true; habilita();
    var erros = 0;
    try {
      for (var i = 0; i < FRASES.length; i++) {
        var f = FRASES[i], prom = cmd("$A " + f, 8000), alvo = espera;
        await prom;
        var hexFw = "";
        alvo.linhas.forEach(function (l) { var m = /^# ([0-9A-Fa-f]*)$/.exec(l); if (m) hexFw = m[1].toLowerCase(); });
        var hexJs = BraillePT.paraHex(BraillePT.traduz(f, { caixaAltaLonga: false }).celas);
        if (hexFw !== hexJs) { erros++; reg("DIFERENTE em \"" + f + "\": impressora " + hexFw + " / programa " + hexJs); }
      }
      estado(erros ? erros + " diferença(s) no tradutor: veja o registro" : "tradutor conferido: " + FRASES.length + " frases iguais", erros ? "erro" : "ok");
    } catch (e) { estado(e.message, "erro"); }
    ocupado = false; habilita();
  }

  // ------------------------------------------------------------------ eventos
  if (!("serial" in navigator)) $("semSerial").hidden = false;
  $("btConectar").addEventListener("click", conecta);
  $("btImprimir").addEventListener("click", imprime);
  $("btCancelar").addEventListener("click", cancela);
  $("btAplicar").addEventListener("click", aplica);
  $("btAutoteste").addEventListener("click", autoteste);
  $("btEnviar").addEventListener("click", function () { var v = $("livre").value.trim(); if (v) simples(v); });
  $("livre").addEventListener("keydown", function (e) { if (e.key === "Enter") $("btEnviar").click(); });
  Array.prototype.forEach.call(document.querySelectorAll("button[data-cmd]"), function (b) {
    b.addEventListener("click", function () { simples(b.getAttribute("data-cmd")); });
  });

  var Q = new URLSearchParams(location.search);
  if (Q.get("tema")) document.documentElement.setAttribute("data-theme", Q.get("tema"));
  var salvo = lembra();
  $("texto").value = Q.get("texto") || (Q.get("exemplo") === "1" ? EXEMPLO : (salvo !== null && salvo !== "" ? salvo : EXEMPLO));
  if (Q.get("aba")) aba(Q.get("aba"));
  refaz();
})();
