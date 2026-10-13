// config.h - pinos e valores de fabrica da impressora braille
// Placa: Arduino Mega 2560 + RAMPS 1.4.  Os valores de "fabrica" podem ser mudados
// pela serial (comando $S nome=valor) e gravados na EEPROM ($W), sem recompilar.
#ifndef CONFIG_H
#define CONFIG_H

#define VERSAO "1.0"

// ----------------------------------------------------------------- pinos (RAMPS 1.4)
#define PINO_X_PASSO    54    // soquete X  (A0)
#define PINO_X_DIR      55    //            (A1)
#define PINO_X_LIGA     38    // ENABLE, ativo em nivel baixo
#define PINO_Y_PASSO    60    // soquete Y  (A6)
#define PINO_Y_DIR      61    //            (A7)
#define PINO_Y_LIGA     56    //            (A2)
#define PINO_FIM_X       3    // barra ENDSTOPS, X-  (X_MIN)
#define PINO_SENSOR_PAPEL 14  // barra ENDSTOPS, Y-  (Y_MIN)
#define PINO_SOLENOIDE   8    // saida D8 (MOSFET)
#define PINO_BUZZER      4    // barra SERVOS, D4 (buzzer passivo + 100 ohm)
#define PINO_BT_CARREGAR 59   // AUX-2 A5: carregar / ejetar a folha
#define PINO_BT_TESTE    63   // AUX-2 A9: imprimir a linha de teste
#define PINO_BT_CANCELAR 64   // AUX-2 A10: cancelar
#define PINO_LED_PRONTA  40   // AUX-2 D40 (verde)
#define PINO_LED_ERRO    42   // AUX-2 D42 (vermelho)
#define PINO_LED_PLACA   13

// ----------------------------------------------------------------- mecanica (ver cad/parametros.py)
#define PASSOS_VOLTA     200
#define MICROPASSOS      16         // DRV8825: so o jumper MS3.  A4988: os 3 jumpers.
#define POLIA_DENTES     20
#define GT2_PASSO_MM     2.0
#define ROLETE_DIAMETRO  26.5       // rolete com O-ring 20 x 3

#define FAB_PASSOS_MM_X  (PASSOS_VOLTA * MICROPASSOS / (POLIA_DENTES * GT2_PASSO_MM))    // 80,00
#define FAB_PASSOS_MM_Y  (PASSOS_VOLTA * MICROPASSOS / (3.14159265 * ROLETE_DIAMETRO))   // 38,44

#define CURSO_X_MM       196.0      // do fim de curso ate o limite direito
#define FAB_HOME_PAPEL   8.0        // o fim de curso fica 8 mm para DENTRO da borda esquerda da folha
#define FAB_DIST_ROLETE  48.0       // do rolete de tracao ate a linha de puncao
#define PAPEL_ALTURA     297.0
#define FOLGA_FIM_PAPEL  4.0

// ----------------------------------------------------------------- movimento
#define FAB_VEL_X        120.0      // mm/s
#define FAB_ACEL_X       3000.0     // mm/s2
#define FAB_VEL_Y        30.0
#define FAB_ACEL_Y       400.0
#define VEL_HOME         30.0
#define VEL_HOME_FINO    5.0

// ----------------------------------------------------------------- solenoide
#define FAB_T_LIGADO     25         // ms de pulso
#define FAB_T_DESLIGADO  30         // ms para o embolo subir antes de mover o carro
#define FAB_T_ASSENTA    5          // ms parado antes de bater
#define T_LIGADO_MAX     80         // limite de seguranca do pulso (ms)
#define CICLO_MAX_PCT    40         // o solenoide nunca fica ligado mais que 40 % do tempo

// ----------------------------------------------------------------- pagina (mm)
#define FAB_PONTO        2.5
#define FAB_CELA         6.0
#define FAB_LINHA        10.0
#define FAB_MARGEM_ESQ   20.0
#define FAB_MARGEM_TOPO  12.0
#define FAB_CELAS        30
#define FAB_LINHAS       23
#define FAB_RECUO        2          // celas em branco no inicio do paragrafo
#define MAX_CELAS        40         // maior linha aceita

// ----------------------------------------------------------------- opcoes (1 = sim)
#define FAB_INVERTE_X    0
#define FAB_INVERTE_Y    0
#define FAB_VAI_E_VEM    1          // fileiras alternam o sentido
#define FAB_FIM_X_NF     1          // fim de curso ligado em C + NF (abre ao apertar)
#define FAB_USA_FIM_X    1
#define FAB_USA_SENSOR   1          // sensor de papel em C + NA (fecha com papel)
#define USA_BUZZER       1
#define USA_BOTOES       1

#define SERIAL_VELOCIDADE 115200

#endif
