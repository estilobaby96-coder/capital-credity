# Capital Credity - Documentação Mestre: Regras de Negócio e Operações

Este documento serve como a **Bíblia Operacional** do sistema Capital Credity. Ele contém todas as lógicas de negócio, regras financeiras, mecânicas de empréstimos, pagamentos e classificação de clientes. 
Qualquer nova IA ou Desenvolvedor que assuma o projeto deve usar este arquivo como fonte absoluta da verdade sobre o funcionamento do sistema.

---

## 1. 💰 Modalidades de Empréstimo e Parcelamento

O sistema permite a criação de empréstimos em três modalidades distintas. A escolha da modalidade afeta como o capital e os juros são fatiados e como o sistema lida com rolagem de dívidas.

### 1.1. Modalidade MENSAL (Padrão Tradicional)
- **Parcelas:** 1 parcela única.
- **Funcionamento:** O cliente pega o valor X e concorda em pagar X + Juros em uma data futura (geralmente dali a um mês).
- **Rolagem de Dívida (Permitida):** Se o cliente não tiver o valor cheio na data do vencimento, ele pode pagar **apenas o valor dos juros**. 
  - Ao fazer isso, o sistema registra o pagamento como "JUROS (ROLAGEM)".
  - A parcela volta ao seu valor total (Capital + Juros) e a data de vencimento é empurrada (rolada) para +1 mês à frente.

### 1.2. Modalidade SEMANAL
- **Parcelas:** 4 parcelas.
- **Intervalo:** A cada 7 dias a partir da data do empréstimo.
- **Fatiamento:** O valor total (Capital Solicitado + Juros Totais) é dividido igualmente por 4.
- **Ajuste de Centavos:** A última parcela (4ª) absorve qualquer diferença de centavos gerada pela divisão, garantindo que a soma exata das parcelas bata com o valor total devido.
- **Rolagem de Dívida (Bloqueada):** O cliente **não pode** pagar apenas juros para empurrar a dívida. Ele deve pagar o valor total da parcela semanal.

### 1.3. Modalidade QUINZENAL
- **Parcelas:** 2 parcelas.
- **Intervalo:** A cada 15 dias a partir da data do empréstimo.
- **Fatiamento:** O valor total (Capital Solicitado + Juros Totais) é dividido por 2, com ajuste de centavos na última parcela.
- **Rolagem de Dívida (Bloqueada):** Assim como na modalidade semanal, não é permitida a rolagem de juros. O pagamento da parcela deve ser integral.

---

## 2. 💸 Lógica de Pagamentos, Atrasos e Multas

A camada transacional do sistema (`PagamentoService`) possui regras estritas sobre o recebimento de valores.

### 2.1. Inadimplência e Atrasos (Parcelas Atrasadas)
Se o cliente não pagar uma parcela (Semanal, Quinzenal ou Mensal) até a data de vencimento:
- A parcela muda o status para `ATRASADA`.
- O cliente é automaticamente marcado como `INADIMPLENTE` (Risco Alto), o que **bloqueia totalmente** a tomada de novos empréstimos.
- **Cobrança de Atrasados:** Quando o cliente for pagar na próxima semana/quinzena, ele é obrigado a pagar a **parcela que estava atrasada (com juros de mora/multa)** + a **parcela da semana atual**. O sistema lida com cada parcela como uma entidade separada na tabela `parcelas`.

### 2.2. Multa e Mora (Juros de Atraso)
O sistema aplica encargos sobre parcelas atrasadas (calculados dinamicamente ou na baixa da parcela):
- **Multa Diária:** Adição de valor fixo por dia de atraso (ex: R$ 1,00/dia).
- **Juros de Mora:** Porcentagem sobre o valor da parcela (ex: 2%).
*(Nota: O valor exato dos encargos é definido nas configurações dinâmicas do sistema, mas a lógica de acréscimo recai sempre sobre o `valor_atualizado` da parcela).*

### 2.3. Validações de Pagamento (Tolerância)
- O sistema aceita pagamentos com uma margem de tolerância de R$ 0,05 (para lidar com arredondamentos).
- Valores menores que o exigido (que não sejam rolagem autorizada) são recusados.

---

## 3. 🎯 Evolução de Nível (Score de Crédito) e Limites

O sistema implementa uma gamificação e análise de risco baseada no histórico de pagamentos.

### 3.1. Níveis de Cliente
A evolução ocorre baseada em **Empréstimos Quitados** (pagamento do capital, liquidando o contrato). Rolagens não contam pontos para subir de nível.

1. **🥉 Bronze:** 0 empréstimos quitados (Iniciantes).
2. **🥈 Prata:** 1 a 2 empréstimos quitados.
3. **🥇 Ouro:** 3 a 4 empréstimos quitados.
4. **💎 Diamante:** 5 ou mais empréstimos quitados.

O nível do cliente define o **Limite Máximo de Crédito** (Teto) que ele pode solicitar.

### 3.2. Termômetro de Risco
Calculado em tempo real ao consultar o cliente:

- 🟢 **Baixo Risco:** Pontualidade > 90% e menos de 3 rolagens no histórico.
- 🟡 **Médio Risco:** Pontualidade entre 70% e 89% OU possui 3+ rolagens de dívida.
- 🔴 **Alto Risco (INADIMPLENTE):** Pontualidade < 70% OU possui alguma parcela com status `ATRASADA` no momento atual.

> **Tolerância Zero:** Se o risco for 🔴 Alto (Inadimplente), o botão de aprovar novos empréstimos fica bloqueado pelo backend e pelo frontend (Mensagem: "Bloqueio de Segurança").

---

## 4. 🏗️ Arquitetura Técnica Relevante para as Lógicas

- **Models (`models/`):**
  - `Emprestimo`: Guarda a `modalidade` (MENSAL, SEMANAL, QUINZENAL), o `valor_emprestado`, `taxa_juros`, e `status`.
  - `Parcela`: Guarda o `numero_parcela`, `capital`, `juros`, `valor_atualizado`, `data_vencimento` e `status` (A VENCER, PAGA, ATRASADA).
- **Services (`services/`):**
  - `EmprestimoService.simulate_installments()`: Contém o algoritmo matemático de fatiamento de parcelas e ajuste de centavos.
  - `PagamentoService.registrar_pagamento()`: Contém as travas de rolagem de juros (bloqueadas para != MENSAL) e a lógica de quitação de parcelas.
- **Interfaces (`views/` e `templates/`):**
  - O sistema possui interface Desktop (CustomTkinter) e interface Web (HTML/FastAPI). Ambas consomem a mesma lógica e requerem que novos campos (como a modalidade) sejam refletidos em ambos os formulários.

---
**FIM DA DOCUMENTAÇÃO MESTRE**
