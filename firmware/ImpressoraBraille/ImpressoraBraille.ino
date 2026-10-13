/*
 * ImpressoraBraille.ino - firmware da impressora braille (Arduino Mega 2560 + RAMPS 1.4)
 *
 * O carro de cima leva um solenoide que bate de cima para baixo; o carro de baixo leva a
 * matriz. Os dois andam juntos (motor X). O motor Y gira os roletes que empurram a folha.
 *
 * Conversa pela serial USB a 115200, uma linha por comando:
 *   texto qualquer      traduz para braille (portugues, grau 1) e imprime
 *   $H  referencia o carro (home)        $L  carrega a folha        $E  ejeta a folha
 *   $C 01031f...        imprime uma linha de celas ja traduzidas (2 digitos hex por cela)
 *   $F n                pula n linhas    $T n  padrao de teste (1 a 4)   $P n  n batidas paradas
 *   $X mm / $Y mm       move o carro / avanca o papel        $M 0|1  desliga/liga os motores
 *   $S nome=valor       muda um parametro    $I  lista tudo    $W  grava    $R  volta ao de fabrica
 *   $A texto            so traduz e devolve as celas em hexadecimal (para conferir o tradutor)
 *   !                   cancela o que estiver fazendo
 * Toda resposta termina com uma linha "ok", "fim_pagina" ou "erro: ...". Linhas "# ..." sao avisos.
 *
 * Nao usa biblioteca externa. Tabela braille: tabela_braille.h (gerada de software/braille-pt.js).
 */
#include <EEPROM.h>
#include <math.h>
#include "config.h"
#include "tabela_braille.h"

// ------------------------------------------------------------------ parametros ajustaveis
struct Parametros {
  uint16_t assinatura;
  float passosMmX, passosMmY, velX, acelX, velY, acelY;
  uint16_t tLigado, tDesligado, tAssenta;
  float ponto, cela, linha, margemEsq, margemTopo, homePapel, distRolete;
  uint8_t celas, linhas, recuo;
  uint8_t inverteX, inverteY, vaiEVem, fimXNF, usaFimX, usaSensor;
};
#define ASSINATURA 0xB7A3
Parametros par;

void parametrosDeFabrica() {
  par.assinatura = ASSINATURA;
  par.passosMmX = FAB_PASSOS_MM_X;  par.passosMmY = FAB_PASSOS_MM_Y;
  par.velX = FAB_VEL_X;  par.acelX = FAB_ACEL_X;  par.velY = FAB_VEL_Y;  par.acelY = FAB_ACEL_Y;
  par.tLigado = FAB_T_LIGADO;  par.tDesligado = FAB_T_DESLIGADO;  par.tAssenta = FAB_T_ASSENTA;
  par.ponto = FAB_PONTO;  par.cela = FAB_CELA;  par.linha = FAB_LINHA;
  par.margemEsq = FAB_MARGEM_ESQ;  par.margemTopo = FAB_MARGEM_TOPO;
  par.homePapel = FAB_HOME_PAPEL;  par.distRolete = FAB_DIST_ROLETE;
  par.celas = FAB_CELAS;  par.linhas = FAB_LINHAS;  par.recuo = FAB_RECUO;
  par.inverteX = FAB_INVERTE_X;  par.inverteY = FAB_INVERTE_Y;  par.vaiEVem = FAB_VAI_E_VEM;
  par.fimXNF = FAB_FIM_X_NF;  par.usaFimX = FAB_USA_FIM_X;  par.usaSensor = FAB_USA_SENSOR;
}

// ------------------------------------------------------------------ estado
long posX = 0;                 // passos a partir do fim de curso
long posPapel = 0;             // passos de avanco desde que a folha encostou no rolete
bool referenciado = false;     // o carro ja achou o fim de curso
bool temFolha = false;
bool cancelar = false;
bool motoresLigados = false;
uint8_t linhaAtual = 0;        // proxima linha de texto na folha (0 = primeira)
int8_t sentido = 1;            // sentido da proxima fileira (vai e vem)
unsigned long tUltimoPulso = 0;
unsigned long tUltimaAcao = 0;

char entrada[260];
uint16_t nEntrada = 0;
uint16_t codigos[220];         // linha de texto ja decodificada (codigos Unicode)
uint8_t celasTexto[340];       // celas da linha traduzida (0 = espaco)

// ------------------------------------------------------------------ sons e luzes
void bip(uint16_t hz, uint16_t ms) {
#if USA_BUZZER
  tone(PINO_BUZZER, hz, ms);
#endif
  delay(ms + 30);
}
void somPronta()  { bip(1760, 70); bip(2349, 90); }
void somFim()     { bip(1319, 90); bip(1760, 90); bip(2637, 160); }
void somErro()    { bip(330, 200); bip(262, 320); }
void somPapel()   { bip(988, 60); }

void luzes(bool pronta, bool erro) {
  digitalWrite(PINO_LED_PRONTA, pronta ? HIGH : LOW);
  digitalWrite(PINO_LED_ERRO, erro ? HIGH : LOW);
}

void erro(const __FlashStringHelper *msg) {
  digitalWrite(PINO_SOLENOIDE, LOW);
  Serial.print(F("erro: "));
  Serial.println(msg);
  luzes(false, true);
  somErro();
}

// ------------------------------------------------------------------ entradas
bool fimXApertado() {
  bool nivel = digitalRead(PINO_FIM_X);            // com pull-up: aberto = HIGH
  return par.fimXNF ? nivel : !nivel;              // NF abre (HIGH) ao apertar; NA fecha (LOW)
}
bool sensorComPapel() { return digitalRead(PINO_SENSOR_PAPEL) == LOW; }   // C + NA: fecha com papel
bool botao(uint8_t pino) {
#if USA_BOTOES
  if (digitalRead(pino) == LOW) { delay(25); return digitalRead(pino) == LOW; }
#endif
  return false;
}
void soltaBotao(uint8_t pino) { while (digitalRead(pino) == LOW) delay(10); delay(40); }

/** Olha se chegou "!" pela serial ou se apertaram o botao de cancelar. */
bool pediuCancelar() {
  if (cancelar) return true;
  if (Serial.peek() == '!') { Serial.read(); cancelar = true; }
#if USA_BOTOES
  else if (digitalRead(PINO_BT_CANCELAR) == LOW) cancelar = true;
#endif
  return cancelar;
}

// ------------------------------------------------------------------ motores
void ligaMotores(bool liga) {
  digitalWrite(PINO_X_LIGA, liga ? LOW : HIGH);
  digitalWrite(PINO_Y_LIGA, liga ? LOW : HIGH);
  if (liga && !motoresLigados) delay(20);
  if (!liga) referenciado = false;                 // sem torque o carro pode sair do lugar
  motoresLigados = liga;
}

/**
 * Da n passos com rampa de aceleracao e de freada (perfil trapezoidal).
 * vmax em passos/s, acel em passos/s2. Se olhaFimX, para quando o fim de curso apertar.
 * Devolve quantos passos deu.
 */
long movePassos(uint8_t pino, long n, float vmax, float acel, bool olhaFimX) {
  if (n <= 0) return 0;
  unsigned long cMin = (unsigned long)(1000000.0 / vmax);       // intervalo em velocidade de cruzeiro (us)
  float c0 = 1000000.0 * sqrt(2.0 / acel);                      // t(k) = sqrt(2k/acel): intervalo = c0*(sqrt(k+1)-sqrt(k))
  long nRampa = (long)(vmax * vmax / (2.0 * acel));             // passos ate a velocidade maxima
  if (nRampa > n / 2) nRampa = n / 2;
  if (nRampa < 1) nRampa = 1;
  unsigned long t = micros();
  long i;
  for (i = 0; i < n; i++) {
    if (olhaFimX && fimXApertado()) break;
    if ((i & 0x7F) == 0 && pediuCancelar()) break;
    digitalWrite(pino, HIGH);
    delayMicroseconds(3);
    digitalWrite(pino, LOW);
    long restam = n - i - 1;
    unsigned long c = cMin;
    long k = -1;
    if (i < nRampa) k = i + 1;                                  // acelerando
    else if (restam <= nRampa) k = restam;                      // freando
    if (k >= 0) {
      float ck = c0 * (sqrt((float)k + 1.0) - sqrt((float)k));
      if (ck > (float)cMin) c = (unsigned long)ck;
    }
    t += c;
    long atraso = (long)(micros() - t);
    if (atraso > 2000) t = micros();                            // nao tenta recuperar atraso grande
    else while ((long)(micros() - t) < 0) { }
  }
  tUltimaAcao = millis();
  return i;
}

/** Move o carro para x (mm a partir do fim de curso). */
bool moveX(float x) {
  if (x < 0) x = 0;
  if (x > CURSO_X_MM) x = CURSO_X_MM;
  long alvo = lround(x * par.passosMmX);
  long d = alvo - posX;
  if (d == 0) return true;
  bool positivo = d > 0;
  digitalWrite(PINO_X_DIR, (positivo != (par.inverteX != 0)) ? HIGH : LOW);
  delayMicroseconds(20);
  long n = labs(d);
  long feitos = movePassos(PINO_X_PASSO, n, par.velX * par.passosMmX, par.acelX * par.passosMmX, false);
  posX += positivo ? feitos : -feitos;
  return feitos == n;
}

/** Avanca o papel (mm; positivo = para a frente, saindo da maquina). */
bool avancaPapel(float mm) {
  long n = lround(fabs(mm) * par.passosMmY);
  if (n == 0) return true;
  bool frente = mm > 0;
  digitalWrite(PINO_Y_DIR, (frente != (par.inverteY != 0)) ? HIGH : LOW);
  delayMicroseconds(20);
  long feitos = movePassos(PINO_Y_PASSO, n, par.velY * par.passosMmY, par.acelY * par.passosMmY, false);
  posPapel += frente ? feitos : -feitos;
  return feitos == n;
}

/** Leva a folha ate a posicao v (mm a partir da borda de cima) ficar embaixo do puncao. So anda para a frente. */
bool papelPara(float v) {
  long alvo = lround((par.distRolete + v) * par.passosMmY);
  long d = alvo - posPapel;
  if (d <= 0) return true;
  return avancaPapel((float)d / par.passosMmY);
}

/** Acha o fim de curso do X. */
bool home() {
  ligaMotores(true);
  cancelar = false;
  if (!par.usaFimX) { posX = 0; referenciado = true; return true; }   // sem chave: confia na posicao atual
  float pm = par.passosMmX;
  bool dirHome = (par.inverteX != 0);                                  // sentido "para a esquerda"
  if (fimXApertado()) {                                                // ja esta em cima da chave: afasta
    digitalWrite(PINO_X_DIR, dirHome ? LOW : HIGH);
    movePassos(PINO_X_PASSO, lround(6 * pm), VEL_HOME * pm, par.acelX * pm, false);
    if (fimXApertado()) { erro(F("fim de curso do X sempre apertado (fio solto? use $I)")); return false; }
  }
  digitalWrite(PINO_X_DIR, dirHome ? HIGH : LOW);
  delayMicroseconds(20);
  movePassos(PINO_X_PASSO, lround((CURSO_X_MM + 30) * pm), VEL_HOME * pm, par.acelX * pm, true);
  if (cancelar) { erro(F("cancelado")); return false; }
  if (!fimXApertado()) { erro(F("fim de curso do X nao encontrado (confira a chave ou use $S invx=1)")); return false; }
  digitalWrite(PINO_X_DIR, dirHome ? LOW : HIGH);                      // afasta 3 mm
  movePassos(PINO_X_PASSO, lround(3 * pm), VEL_HOME * pm, par.acelX * pm, false);
  digitalWrite(PINO_X_DIR, dirHome ? HIGH : LOW);                      // encosta devagar
  delayMicroseconds(20);
  movePassos(PINO_X_PASSO, lround(8 * pm), VEL_HOME_FINO * pm, par.acelX * pm, true);
  if (!fimXApertado()) { erro(F("fim de curso do X falhou na segunda passada")); return false; }
  posX = 0;
  referenciado = true;
  return true;
}

// ------------------------------------------------------------------ solenoide
void bate() {
  // protecao termica: respeita o ciclo maximo (tempo ligado / tempo total)
  unsigned long cicloMin = (unsigned long)par.tLigado * 100UL / CICLO_MAX_PCT;
  while (millis() - tUltimoPulso < cicloMin) { }
  delay(par.tAssenta);
  tUltimoPulso = millis();
  digitalWrite(PINO_LED_PLACA, HIGH);
  digitalWrite(PINO_SOLENOIDE, HIGH);
  delay(par.tLigado);
  digitalWrite(PINO_SOLENOIDE, LOW);
  digitalWrite(PINO_LED_PLACA, LOW);
  delay(par.tDesligado);
}

// ------------------------------------------------------------------ folha
bool carrega() {
  ligaMotores(true);
  cancelar = false;
  if (par.usaSensor) {
    unsigned long t0 = millis(), tBip = 0;
    if (!sensorComPapel()) Serial.println(F("# coloque a folha ate encostar nos roletes"));
    while (!sensorComPapel()) {
      if (pediuCancelar()) { erro(F("cancelado")); return false; }
      if (millis() - t0 > 60000UL) { erro(F("sem papel")); return false; }
      if (millis() - tBip > 3000UL) { tBip = millis(); somPapel(); }
    }
    delay(800);                                    // tempo de a pessoa encostar a folha no rolete
  }
  posPapel = 0;
  linhaAtual = 0;
  sentido = 1;
  if (!papelPara(par.margemTopo)) { erro(F("cancelado")); return false; }
  temFolha = true;
  luzes(true, false);
  return true;
}

void ejeta() {
  ligaMotores(true);
  // a borda de tras passa 15 mm do rolete; o resto a pessoa puxa pela frente
  float vFim = PAPEL_ALTURA - par.distRolete + 15.0;
  long alvo = lround((par.distRolete + vFim) * par.passosMmY);
  if (alvo > posPapel) avancaPapel((float)(alvo - posPapel) / par.passosMmY);
  temFolha = false;
  linhaAtual = 0;
  somFim();
}

/** Garante carro referenciado e folha no lugar. Devolve 0 = ok, 1 = erro, 2 = pagina cheia (ejetou). */
uint8_t prepara(bool trocaSozinho) {
  if (!referenciado && !home()) return 1;
  if (temFolha && linhaAtual >= par.linhas) {
    moveX(0);
    ejeta();
    if (!trocaSozinho) return 2;
    Serial.println(F("# pagina cheia: coloque outra folha"));
    if (!par.usaSensor) {                          // sem sensor: espera o botao ou um "+" pela serial
      while (!botao(PINO_BT_CARREGAR)) {
        if (Serial.peek() == '+') { Serial.read(); break; }
        if (pediuCancelar()) { erro(F("cancelado")); return 1; }
      }
    } else {
      unsigned long t0 = millis();
      while (sensorComPapel() && millis() - t0 < 30000UL) { }       // espera tirarem a folha pronta
      delay(500);
    }
  }
  if (!temFolha && !carrega()) return 1;
  return 0;
}

/** Marca uma linha de n celas na linha atual da folha. */
bool marcaLinha(const uint8_t *celas, uint8_t n) {
  static float xs[2 * MAX_CELAS];
  if (n > MAX_CELAS) n = MAX_CELAS;
  for (uint8_t f = 0; f < 3; f++) {
    uint8_t qt = 0;
    for (uint8_t c = 0; c < n; c++) {
      float u = par.margemEsq + c * par.cela;
      if (celas[c] & (1 << f)) xs[qt++] = u;
      if (celas[c] & (1 << (f + 3))) xs[qt++] = u + par.ponto;
    }
    if (qt == 0) continue;
    float v = par.margemTopo + linhaAtual * par.linha + f * par.ponto;
    if (par.distRolete + v > PAPEL_ALTURA - FOLGA_FIM_PAPEL) { erro(F("linha fora do alcance dos roletes")); return false; }
    if (par.usaSensor && !sensorComPapel() && v < PAPEL_ALTURA - par.distRolete - 20.0) {
      temFolha = false;
      erro(F("a folha acabou ou saiu do sensor"));
      return false;
    }
    if (!papelPara(v)) { erro(F("cancelado")); return false; }
    bool volta = par.vaiEVem && sentido < 0;
    for (uint8_t j = 0; j < qt; j++) {
      float x = xs[volta ? (qt - 1 - j) : j] - par.homePapel;
      if (x < 0 || x > CURSO_X_MM) continue;       // ponto fora do curso do carro: pula
      if (!moveX(x) || pediuCancelar()) { erro(F("cancelado")); return false; }
      bate();
    }
    if (par.vaiEVem) sentido = -sentido;
  }
  linhaAtual++;
  return true;
}

// ------------------------------------------------------------------ texto -> braille
uint8_t celaDaLetra(uint16_t cod) {                // cod = letra minuscula; 0xFF se nao existe
  if (cod > 255) return 0xFF;
  for (uint8_t i = 0; i < N_LETRAS; i++)
    if (pgm_read_byte(&TAB_LETRAS[i][0]) == (uint8_t)cod) return pgm_read_byte(&TAB_LETRAS[i][1]);
  return 0xFF;
}
bool ehMaiuscula(uint16_t c) { return (c >= 'A' && c <= 'Z') || (c >= 0xC0 && c <= 0xDE && c != 0xD7); }
uint16_t minuscula(uint16_t c) { return ehMaiuscula(c) ? c + 0x20 : c; }
bool ehLetra(uint16_t c) { return celaDaLetra(minuscula(c)) != 0xFF; }
bool ehDigito(uint16_t c) { return c >= '0' && c <= '9'; }

/** Decodifica UTF-8 em codigos Unicode. Devolve a quantidade. */
uint16_t decodifica(const char *s, uint16_t *dest, uint16_t maximo) {
  uint16_t n = 0;
  while (*s && n < maximo) {
    uint8_t b = (uint8_t)*s++;
    uint16_t c;
    if (b < 0x80) c = b;
    else if ((b & 0xE0) == 0xC0 && *s) { c = ((uint16_t)(b & 0x1F) << 6) | ((uint8_t)*s++ & 0x3F); }
    else if ((b & 0xF0) == 0xE0 && s[0] && s[1]) {
      c = ((uint16_t)(b & 0x0F) << 12) | ((uint16_t)((uint8_t)s[0] & 0x3F) << 6) | ((uint8_t)s[1] & 0x3F);
      s += 2;
    } else { while (((uint8_t)*s & 0xC0) == 0x80) s++; c = ' '; }
    if (c == 0xBA) c = 'o';                        // ordinais: º e ª
    if (c == 0xAA) c = 'a';
    if (c == 0xA0 || c == '\t') c = ' ';
    dest[n++] = c;
  }
  return n;
}

/** Traduz os codigos para celas. Devolve a quantidade de celas (0 = espaco entre palavras). */
uint16_t traduz(const uint16_t *cs, uint16_t n, uint8_t *out, uint16_t maximo) {
  uint16_t m = 0;
  bool numero = false;
  #define POE(c) do { if (m < maximo) out[m++] = (c); } while (0)
  for (uint16_t i = 0; i < n; i++) {
    uint16_t ch = cs[i];
    if (ch == ' ') { POE(0); numero = false; continue; }
    if (ehDigito(ch)) {
      if (!numero) { POE(CELA_NUMERO); numero = true; }
      POE(pgm_read_byte(&TAB_DIGITOS[ch - '0']));
      continue;
    }
    if (numero && (ch == ',' || ch == '.') && i + 1 < n && ehDigito(cs[i + 1])) {
      POE(ch == ',' ? 0x02 : 0x04);                // virgula decimal / ponto de milhar
      continue;
    }
    if (ehLetra(ch)) {
      uint16_t mi = minuscula(ch);
      if (numero && mi >= 'a' && mi <= 'j') POE(CELA_LETRA);
      numero = false;
      bool inicio = (i == 0) || !ehLetra(cs[i - 1]);
      if (inicio) {                                // palavra inteira em maiusculas (2 letras ou mais)?
        uint16_t j = i;
        bool todas = true;
        while (j < n && ehLetra(cs[j])) { if (!ehMaiuscula(cs[j])) todas = false; j++; }
        if (todas && j - i >= 2) {
          POE(CELA_MAIUSCULA); POE(CELA_MAIUSCULA);
          for (; i < j; i++) POE(celaDaLetra(minuscula(cs[i])));
          i--;
          continue;
        }
      }
      if (ehMaiuscula(ch)) POE(CELA_MAIUSCULA);
      POE(celaDaLetra(mi));
      continue;
    }
    numero = false;
    if (ch == 0x2013 || ch == 0x2014) { POE(CELA_HIFEN); POE(CELA_HIFEN); continue; }      // travessao
    if (ch == 0x2026) { POE(0x04); POE(0x04); POE(0x04); continue; }                        // reticencias
    if (ch == 0x201C || ch == 0x201D) ch = '"';
    if (ch == 0x2018 || ch == 0x2019) ch = '\'';
    bool achou = false;
    if (ch < 256) {
      for (uint8_t k = 0; k < N_SINAIS; k++) {
        if (pgm_read_byte(&TAB_SINAIS[k][0]) == (uint8_t)ch) {
          uint8_t q = pgm_read_byte(&TAB_SINAIS[k][1]);
          for (uint8_t z = 0; z < q; z++) POE(pgm_read_byte(&TAB_SINAIS[k][2 + z]));
          achou = true;
          break;
        }
      }
    }
    if (!achou) POE(0);                            // caractere sem cela: vira espaco
  }
  #undef POE
  return m;
}

/** Imprime um paragrafo de celas, quebrando as linhas sem partir palavras. */
bool imprimeParagrafo(const uint8_t *cel, uint16_t n) {
  uint8_t linha[MAX_CELAS];
  uint8_t larg = par.celas > MAX_CELAS ? MAX_CELAS : par.celas;
  uint8_t usado = 0;
  bool vazia = true;
  for (uint8_t r = 0; r < par.recuo && usado < larg; r++) linha[usado++] = 0;
  uint16_t i = 0;
  while (i < n) {
    while (i < n && cel[i] == 0) i++;              // pula espacos
    if (i >= n) break;
    uint16_t j = i;
    while (j < n && cel[j] != 0) j++;              // palavra = cel[i..j)
    uint16_t tam = j - i;
    if (!vazia && usado + 1 + tam > larg) {        // nao cabe: fecha a linha
      uint8_t r = prepara(true);
      if (r || !marcaLinha(linha, usado)) return false;
      usado = 0; vazia = true;
    }
    if (!vazia) linha[usado++] = 0;
    while (tam > (uint16_t)(larg - usado)) {       // palavra maior que a linha: parte com hifen
      uint8_t cabe = larg - usado - 1;
      for (uint8_t k = 0; k < cabe; k++) linha[usado++] = cel[i++];
      linha[usado++] = CELA_HIFEN;
      tam -= cabe;
      uint8_t r = prepara(true);
      if (r || !marcaLinha(linha, usado)) return false;
      usado = 0;
    }
    while (i < j) linha[usado++] = cel[i++];
    vazia = false;
  }
  if (!vazia) {
    uint8_t r = prepara(true);
    if (r || !marcaLinha(linha, usado)) return false;
  }
  return true;
}

// ------------------------------------------------------------------ padroes de teste
bool teste(uint8_t qual) {
  uint8_t linha[MAX_CELAS];
  uint8_t larg = par.celas > MAX_CELAS ? MAX_CELAS : par.celas;
  if (prepara(true)) return false;
  if (qual == 1) {                                 // celas cheias: confere espacamento e altura do ponto
    for (uint8_t i = 0; i < larg; i++) linha[i] = 0x3F;
    return marcaLinha(linha, larg);
  }
  if (qual == 2) {                                 // alfabeto
    uint8_t n = 0;
    for (char c = 'a'; c <= 'z' && n < larg; c++) linha[n++] = celaDaLetra(c);
    return marcaLinha(linha, n);
  }
  if (qual == 3) {                                 // colunas alternadas: mostra folga entre ida e volta
    for (uint8_t i = 0; i < larg; i++) linha[i] = (i & 1) ? 0x07 : 0x38;
    return marcaLinha(linha, larg);
  }
  if (qual == 4) {                                 // escada de tempo de pulso: 9 grupos de 4 pontos,
    uint16_t guarda = par.tLigado;                 // com 10, 15, 20 ... 50 ms (da esquerda para a direita)
    bool ok = papelPara(par.margemTopo + linhaAtual * par.linha);
    for (uint8_t p = 0; p < 9 && ok; p++) {
      par.tLigado = 10 + 5 * p;
      for (uint8_t i = 0; i < 4 && ok; i++) {
        ok = moveX(par.margemEsq + p * 15.0 + i * par.ponto - par.homePapel) && !pediuCancelar();
        if (ok) bate();
      }
    }
    par.tLigado = guarda;
    if (!ok) { erro(F("cancelado")); return false; }
    linhaAtual++;
    return true;
  }
  erro(F("teste desconhecido (use 1 a 4)"));
  return false;
}

// ------------------------------------------------------------------ parametros pela serial
struct NomePar { const char *nome; uint8_t tipo; void *ptr; };    // tipo: 0 float, 1 uint16, 2 uint8
const NomePar NOMES[] = {
  {"ppx", 0, &par.passosMmX}, {"ppy", 0, &par.passosMmY}, {"vx", 0, &par.velX}, {"ax", 0, &par.acelX},
  {"vy", 0, &par.velY}, {"ay", 0, &par.acelY}, {"ton", 1, &par.tLigado}, {"toff", 1, &par.tDesligado},
  {"tass", 1, &par.tAssenta}, {"ponto", 0, &par.ponto}, {"cela", 0, &par.cela}, {"linha", 0, &par.linha},
  {"me", 0, &par.margemEsq}, {"mt", 0, &par.margemTopo}, {"home", 0, &par.homePapel}, {"rolete", 0, &par.distRolete},
  {"celas", 2, &par.celas}, {"linhas", 2, &par.linhas}, {"recuo", 2, &par.recuo}, {"invx", 2, &par.inverteX},
  {"invy", 2, &par.inverteY}, {"vaievem", 2, &par.vaiEVem}, {"fcnf", 2, &par.fimXNF}, {"fimx", 2, &par.usaFimX},
  {"sensor", 2, &par.usaSensor}
};
const uint8_t N_NOMES = sizeof(NOMES) / sizeof(NOMES[0]);

void limita() {
  if (par.tLigado > T_LIGADO_MAX) par.tLigado = T_LIGADO_MAX;
  if (par.tLigado < 2) par.tLigado = 2;
  if (par.celas > MAX_CELAS) par.celas = MAX_CELAS;
  if (par.celas < 4) par.celas = 4;
  if (par.recuo > par.celas / 2) par.recuo = par.celas / 2;
  if (par.linhas < 1) par.linhas = 1;
  if (par.passosMmX < 1) par.passosMmX = FAB_PASSOS_MM_X;
  if (par.passosMmY < 1) par.passosMmY = FAB_PASSOS_MM_Y;
  if (par.velX < 1) par.velX = 1;
  if (par.velX > 250) par.velX = 250;
  if (par.acelX < 50) par.acelX = 50;
  if (par.velY < 1) par.velY = 1;
  if (par.velY > 80) par.velY = 80;
  if (par.acelY < 20) par.acelY = 20;
}

void lista() {
  Serial.print(F("# Impressora braille v")); Serial.println(F(VERSAO));
  for (uint8_t i = 0; i < N_NOMES; i++) {
    Serial.print(F("# ")); Serial.print(NOMES[i].nome); Serial.print('=');
    if (NOMES[i].tipo == 0) Serial.println(*(float *)NOMES[i].ptr, 3);
    else if (NOMES[i].tipo == 1) Serial.println(*(uint16_t *)NOMES[i].ptr);
    else Serial.println(*(uint8_t *)NOMES[i].ptr);
  }
  Serial.print(F("# estado: carro ")); Serial.print(referenciado ? F("referenciado") : F("sem referencia"));
  Serial.print(F(", x=")); Serial.print(posX / par.passosMmX, 2);
  Serial.print(F(" mm, folha ")); Serial.print(temFolha ? F("carregada") : F("ausente"));
  Serial.print(F(", linha ")); Serial.print(linhaAtual);
  Serial.print(F(", fim de curso ")); Serial.print(fimXApertado() ? F("apertado") : F("livre"));
  Serial.print(F(", sensor ")); Serial.println(sensorComPapel() ? F("com papel") : F("sem papel"));
}

bool ajusta(char *txt) {                           // txt = "nome=valor"
  char *ig = strchr(txt, '=');
  if (!ig) return false;
  *ig = 0;
  for (uint8_t i = 0; i < N_NOMES; i++) {
    if (strcmp(txt, NOMES[i].nome) == 0) {
      double v = atof(ig + 1);
      if (NOMES[i].tipo == 0) *(float *)NOMES[i].ptr = v;
      else if (NOMES[i].tipo == 1) *(uint16_t *)NOMES[i].ptr = (uint16_t)v;
      else *(uint8_t *)NOMES[i].ptr = (uint8_t)v;
      limita();
      return true;
    }
  }
  return false;
}

int8_t hexDigito(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

// ------------------------------------------------------------------ comandos
void comando(char *s) {
  char c = s[1];
  char *arg = s + 2;
  while (*arg == ' ') arg++;
  bool ok = true;
  cancelar = false;
  luzes(false, false);
  switch (c) {
    case 'H': case 'h': ok = home(); break;
    case 'L': case 'l':
      if (temFolha && linhaAtual == 0) break;        // folha ja esta no lugar e em branco
      if (temFolha) ejeta();                         // folha usada: sai antes de entrar a proxima
      ok = (referenciado || home()) && carrega();
      break;
    case 'E': case 'e': ejeta(); break;
    case 'I': case 'i': case '?': lista(); break;
    case 'W': case 'w': EEPROM.put(0, par); break;
    case 'R': case 'r': parametrosDeFabrica(); break;
    case 'M': case 'm': ligaMotores(atoi(arg) != 0); break;
    case 'S': case 's': if (!ajusta(arg)) { erro(F("parametro desconhecido (use $I para ver a lista)")); ok = false; } break;
    case 'T': case 't': ok = teste((uint8_t)atoi(arg)); break;
    case 'X': case 'x': ok = (referenciado || home()) && moveX(atof(arg)); break;
    case 'Y': case 'y': ligaMotores(true); ok = avancaPapel(atof(arg)); break;
    case 'A': case 'a': {                          // so traduz e devolve as celas em hexadecimal (autoteste)
      uint16_t n = decodifica(arg, codigos, sizeof(codigos) / sizeof(codigos[0]));
      uint16_t m = traduz(codigos, n, celasTexto, sizeof(celasTexto));
      Serial.print(F("# "));
      for (uint16_t i = 0; i < m; i++) {
        if (celasTexto[i] < 16) Serial.print('0');
        Serial.print(celasTexto[i], HEX);
      }
      Serial.println();
      break;
    }
    case 'P': case 'p': {                          // batidas paradas, para regular o puncao e a matriz
      int n = atoi(arg);
      if (n < 1) n = 1;
      if (n > 200) n = 200;
      for (int i = 0; i < n && !pediuCancelar(); i++) bate();
      break;
    }
    case 'F': case 'f': {
      int n = atoi(arg);
      if (n < 1) n = 1;
      uint8_t r = prepara(false);
      if (r == 2) { Serial.println(F("fim_pagina")); return; }
      ok = (r == 0);
      if (ok) linhaAtual = (linhaAtual + n > par.linhas) ? par.linhas : linhaAtual + n;
      break;
    }
    case 'C': case 'c': {
      uint8_t linha[MAX_CELAS];
      uint8_t n = 0;
      while (arg[0] && arg[1] && n < MAX_CELAS) {
        int8_t a = hexDigito(arg[0]), b = hexDigito(arg[1]);
        if (a < 0 || b < 0) break;
        linha[n++] = ((a << 4) | b) & 0x3F;
        arg += 2;
      }
      uint8_t r = prepara(false);
      if (r == 2) { Serial.println(F("fim_pagina")); return; }
      ok = (r == 0) && marcaLinha(linha, n);
      break;
    }
    default: erro(F("comando desconhecido")); ok = false;
  }
  if (ok) { Serial.println(F("ok")); luzes(true, false); }
}

void texto(char *s) {
  cancelar = false;
  luzes(false, false);
  uint16_t n = decodifica(s, codigos, sizeof(codigos) / sizeof(codigos[0]));
  uint16_t m = traduz(codigos, n, celasTexto, sizeof(celasTexto));
  bool ok = (m == 0) ? true : imprimeParagrafo(celasTexto, m);
  if (ok) { Serial.println(F("ok")); luzes(true, false); }
}

// ------------------------------------------------------------------ setup / loop
void setup() {
  pinMode(PINO_SOLENOIDE, OUTPUT);
  digitalWrite(PINO_SOLENOIDE, LOW);               // primeira coisa: solenoide desligado
  const uint8_t saidas[] = {PINO_X_PASSO, PINO_X_DIR, PINO_X_LIGA, PINO_Y_PASSO, PINO_Y_DIR, PINO_Y_LIGA,
                            PINO_LED_PRONTA, PINO_LED_ERRO, PINO_LED_PLACA, PINO_BUZZER};
  for (uint8_t i = 0; i < sizeof(saidas); i++) { pinMode(saidas[i], OUTPUT); digitalWrite(saidas[i], LOW); }
  digitalWrite(PINO_X_LIGA, HIGH);                 // drivers desligados ate o primeiro comando
  digitalWrite(PINO_Y_LIGA, HIGH);
  const uint8_t entradas[] = {PINO_FIM_X, PINO_SENSOR_PAPEL, PINO_BT_CARREGAR, PINO_BT_TESTE, PINO_BT_CANCELAR};
  for (uint8_t i = 0; i < sizeof(entradas); i++) pinMode(entradas[i], INPUT_PULLUP);

  EEPROM.get(0, par);
  if (par.assinatura != ASSINATURA) parametrosDeFabrica();
  limita();

  Serial.begin(SERIAL_VELOCIDADE);
  Serial.println(F("# Impressora braille v" VERSAO " pronta. $I mostra os parametros."));
  luzes(true, false);
  somPronta();
  tUltimaAcao = millis();
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\r') continue;
    if (ch == '\n') {
      entrada[nEntrada] = 0;
      if (nEntrada == 0) { }                       // linha vazia: nada a fazer (para pular linha use $F 1)
      else if (entrada[0] == '$') comando(entrada);
      else if (!(nEntrada == 1 && (entrada[0] == '!' || entrada[0] == '+'))) texto(entrada);
      nEntrada = 0;
      tUltimaAcao = millis();
    } else if (nEntrada < sizeof(entrada) - 1) entrada[nEntrada++] = ch;
  }
#if USA_BOTOES
  if (botao(PINO_BT_CARREGAR)) {                   // carrega; se ja tem folha, ejeta
    soltaBotao(PINO_BT_CARREGAR);
    cancelar = false;
    if (temFolha) ejeta();
    else if (referenciado || home()) carrega();
    tUltimaAcao = millis();
  }
  if (botao(PINO_BT_TESTE)) {
    soltaBotao(PINO_BT_TESTE);
    cancelar = false;
    teste(2);
    tUltimaAcao = millis();
  }
#endif
  // 3 minutos parada e sem folha: solta os motores para nao esquentar
  if (motoresLigados && !temFolha && millis() - tUltimaAcao > 180000UL) ligaMotores(false);
}
