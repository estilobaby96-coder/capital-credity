# Regras de Negócio: Níveis de Clientes e Limites de Crédito

Este documento estabelece as diretrizes oficias do sistema **Capital Credity** referentes à classificação dos clientes (Score), as concessões de limites de crédito (tetos máximos para empréstimos) e as travas de inadimplência.

---

## 🎯 Evolução de Nível (Score de Crédito)

A evolução de nível do cliente ocorre de forma totalmente automática, baseada no histórico de pagamentos **integrais** (quitação da dívida). A rolagem de dívida (pagamento apenas de juros) não é contabilizada para fins de progressão de nível.

O sistema divide os clientes em quatro patamares principais:

### 🥉 Nível Bronze
*   **Condição:** 0 empréstimos quitados.
*   **Descrição:** É o nível de entrada. Todo cliente recém-cadastrado na plataforma inicia nesta categoria enquanto não possui histórico de encerramento de contratos no Capital Credity.

### 🥈 Nível Prata
*   **Condição:** 1 a 2 empréstimos quitados.
*   **Descrição:** O cliente já provou capacidade de pagamento ao liquidar totalmente pelo menos um contrato.

### 🥇 Nível Ouro
*   **Condição:** 3 a 4 empréstimos quitados.
*   **Descrição:** Clientes recorrentes que demonstram alta confiabilidade e histórico positivo estabelecido na instituição.

### 💎 Nível Diamante
*   **Condição:** 5 ou mais empréstimos quitados.
*   **Descrição:** Categoria máxima, destinada aos clientes premium da carteira, que possuem um relacionamento sólido e contínuo.

---

## 🛡️ Termômetro de Risco e Bloqueios

Além do Nível, o sistema realiza uma análise paralela do perfil de risco em tempo real.

### Indicadores Visuais de Risco

1.  🟢 **Baixo Risco:**
    *   Cliente pontual, com taxa de pagamento em dia acima de 90%.
    *   Pouco ou nenhum histórico de rolagens de dívida (menos que 3 rolagens).
2.  🟡 **Médio Risco:**
    *   Cliente possui taxa de pontualidade entre 70% e 89%.
    *   *Ou* já efetuou 3 ou mais rolagens de dívida (pagamento apenas de juros sem abater o capital) em seu histórico.
3.  🔴 **Alto Risco:**
    *   Taxa de pontualidade abaixo de 70%.
    *   *Ou* possui, no momento da consulta, empréstimos com status em **ATRASO**. Neste cenário, o sistema sinaliza como `INADIMPLENTE`.

---

## 🚫 Tolerância Zero com Inadimplência

Independente do nível de relacionamento do cliente (mesmo que seja um cliente **💎 Nível Diamante**), o sistema opera com a regra de tolerância zero para atrasos ativos:

> [!CAUTION]
> **Bloqueio Total por Inadimplência:**
> Se o cliente possuir **qualquer** empréstimo com status em **ATRASO**, o seu risco é elevado automaticamente para **🔴 Alto Risco (INADIMPLENTE)**.
> 
> Nessas condições, a funcionalidade de criar novos empréstimos é **totalmente bloqueada** para esse cliente. O sistema emitirá um Alerta de Segurança e não permitirá o avanço até que o cliente regularize a pendência (seja pagando o valor total ou realizando a rolagem com o pagamento dos juros).

> [!NOTE]
> Estas regras estão em vigor de forma automatizada no código. Para flexibilizar os limites ou as travas de segurança, o sistema necessita de uma atualização direta no motor de regras de negócio.
