"""
servidor.py - Servidor HTTP em Python Puro (Sem JavaScript!)
Projeto: Mesa de Som Virtual (Workshop Didático)

Este arquivo é responsável por:
1. Servir a interface HTML e CSS diretamente pelo Python.
2. Processar envios de formulários HTML (POST /solicitar, POST /aceitar, POST /recusar, POST /auxiliar).
3. Atualizar o banco de dados SQLite (banco.py).
4. Redirecionar o navegador após cada ação (HTTP 303 Redirect).
5. A tela do operador se atualiza sozinha a cada 2 segundos via <meta http-equiv="refresh">.
"""

import http.server
import socketserver
import urllib.parse
import socket
import os
import banco

PORT = 8000

def calcular_angulo_knob(vol):
    """Calcula a rotação em graus para o botão rotatório AUX (-135deg a +135deg)."""
    return -135 + (vol / 100) * 270

class MesaSomSemJSHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        """Trata requisições GET renderizando páginas HTML dinâmicas em Python."""
        url_parsed = urllib.parse.urlparse(self.path)
        caminho = url_parsed.path
        params = urllib.parse.parse_qs(url_parsed.query)

        # 1. Rota da Tela do Músico (index.html)
        if caminho in ["/", "/index.html", "/musico"]:
            self._renderizar_tela_musico(params)
            return

        # 2. Rota da Tela do Operador (operador.html)
        if caminho in ["/operador", "/operador.html"]:
            self._renderizar_tela_operador()
            return

        # 3. Servir arquivos estáticos padrão (como style.css)
        return super().do_GET()

    def do_POST(self):
        """Trata envios de formulários HTML (POST tradicional)."""
        length = int(self.headers.get("Content-Length", 0))
        post_data_raw = self.rfile.read(length).decode("utf-8")
        post_data = urllib.parse.parse_qs(post_data_raw)

        url_parsed = urllib.parse.urlparse(self.path)
        caminho = url_parsed.path

        # 1. Músico cria solicitação de alteração de volume (POST /solicitar)
        if caminho == "/solicitar":
            inst_id = int(post_data.get("instrumento_id", [1])[0])
            novo_vol = int(post_data.get("volume_solicitado", [50])[0])
            banco.criar_solicitacao(inst_id, novo_vol)
            self._redirecionar(f"/?id={inst_id}&msg=solicitado")
            return

        # 2. Músico ou Operador altera o volume do Retorno Auxiliar (POST /auxiliar)
        if caminho == "/auxiliar":
            inst_id = int(post_data.get("instrumento_id", [1])[0])
            novo_aux = int(post_data.get("volume_auxiliar", [50])[0])
            origem = post_data.get("origem", ["musico"])[0]
            banco.atualizar_volume_auxiliar(inst_id, novo_aux)
            
            if origem == "operador":
                self._redirecionar("/operador")
            else:
                self._redirecionar(f"/?id={inst_id}")
            return

        # 3. Operador aceita solicitação (POST /aceitar)
        if caminho == "/aceitar":
            sol_id = int(post_data.get("solicitacao_id", [0])[0])
            banco.aceitar_solicitacao(sol_id)
            self._redirecionar("/operador")
            return

        # 4. Operador recusa solicitação (POST /recusar)
        if caminho == "/recusar":
            sol_id = int(post_data.get("solicitacao_id", [0])[0])
            banco.recusar_solicitacao(sol_id)
            self._redirecionar("/operador")
            return

        self._redirecionar("/")

    def _redirecionar(self, destino):
        """Envia um redirecionamento HTTP 303 (See Other) para o navegador."""
        self.send_response(303)
        self.send_header("Location", destino)
        self.end_headers()

    def _renderizar_tela_musico(self, params):
        """Renderiza o HTML da tela do Músico injetando dados do SQLite."""
        instrumentos = banco.listar_instrumentos()
        if not instrumentos:
            self.send_error(500, "Nenhum instrumento no banco")
            return

        # Identifica instrumento selecionado pela URL (?id=X)
        inst_id_selecionado = int(params.get("id", [instrumentos[0]["id"]])[0])
        inst = banco.obter_instrumento(inst_id_selecionado) or instrumentos[0]

        # Gera opções do <select>
        select_options_html = ""
        for item in instrumentos:
            selected = "selected" if item["id"] == inst["id"] else ""
            select_options_html += f'<option value="{item["id"]}" {selected}>{item["nome"]} ({item["musico"]})</option>\n'

        # Mensagem de status da solicitação
        msg_type = params.get("msg", [""])[0]
        if msg_type == "solicitado":
            status_html = "🟡 <strong>Solicitação enviada!</strong> Aguardando o operador da mesa..."
        else:
            status_html = f"<strong>Status:</strong> Pronto para solicitar alterações para <em>{inst['nome']}</em>."

        # Rotação do Knob de Girar AUX
        aux_vol = inst.get("volume_auxiliar", 50)
        angulo_knob = calcular_angulo_knob(aux_vol)

        with open("index.html", "r", encoding="utf-8") as f:
            template = f.read()

        html_final = template.replace("{{SELECT_OPTIONS}}", select_options_html)\
                             .replace("{{INST_ID}}", str(inst["id"]))\
                             .replace("{{VOLUME_ATUAL}}", str(inst["volume_atual"]))\
                             .replace("{{VOLUME_AUXILIAR}}", str(aux_vol))\
                             .replace("{{ANGULO_KNOB}}", str(angulo_knob))\
                             .replace("{{STATUS_MSG}}", status_html)

        self._enviar_html(html_final)

    def _renderizar_tela_operador(self):
        """Renderiza a tela do Operador com canais e solicitações dinâmicas."""
        instrumentos = banco.listar_instrumentos()
        solicitacoes = banco.listar_solicitacoes()

        # 1. Monta os canais da mesa de som
        canais_html = ""
        for inst in instrumentos:
            aux_vol = inst.get("volume_auxiliar", 50)
            angulo = calcular_angulo_knob(aux_vol)
            canais_html += f"""
            <div class="channel-strip">
              <div class="channel-name">{inst['nome']}</div>
              <div class="channel-musico">{inst['musico']}</div>

              <!-- Knob AUX (Rotatório) -->
              <form action="/auxiliar" method="POST">
                <input type="hidden" name="instrumento_id" value="{inst['id']}">
                <input type="hidden" name="origem" value="operador">
                <div class="knob-container">
                  <div class="knob-label">AUX RETORNO</div>
                  <div class="knob-dial-wrapper">
                    <div class="knob-numbers">
                      <span class="knob-number knob-num-0">0</span>
                      <span class="knob-number knob-num-3">3</span>
                      <span class="knob-number knob-num-5">5</span>
                      <span class="knob-number knob-num-7">7</span>
                      <span class="knob-number knob-num-10">10</span>
                    </div>
                    <div class="knob-body" style="transform: rotate({angulo}deg);">
                      <div class="knob-pointer"></div>
                    </div>
                  </div>
                  <input type="range" class="knob-range-input" name="volume_auxiliar" min="0" max="100" value="{aux_vol}" onchange="this.form.submit()">
                  <div class="knob-value-text">Aux: {aux_vol}%</div>
                </div>
              </form>

              <!-- Barra de Volume do Canal -->
              <div class="channel-volume-meter">
                <div class="channel-volume-fill" style="height: {inst['volume_atual']}%"></div>
              </div>
              <div class="channel-volume-text">{inst['volume_atual']}%</div>
            </div>
            """

        # 2. Monta a lista de solicitações pendentes
        pendentes = [s for s in solicitacoes if s["status"] == "pendente"]
        solicitacoes_html = ""

        if not pendentes:
          solicitacoes_html = '<div class="empty-msg">Nenhuma solicitação pendente no momento.</div>'
        else:
          for sol in pendentes:
            solicitacoes_html += f"""
            <div class="request-card">
              <div class="request-info">
                <div class="request-title">🔴 {sol['instrumento']} ({sol['musico']})</div>
                <div class="request-diff">Volume: {sol['volume_atual']}% → <strong>{sol['volume_solicitado']}%</strong></div>
              </div>
              <div class="request-actions">
                <form action="/aceitar" method="POST" style="display:inline;">
                  <input type="hidden" name="solicitacao_id" value="{sol['id']}">
                  <button type="submit" class="btn btn-accept">ACEITAR</button>
                </form>
                <form action="/recusar" method="POST" style="display:inline;">
                  <input type="hidden" name="solicitacao_id" value="{sol['id']}">
                  <button type="submit" class="btn btn-refuse">RECUSAR</button>
                </form>
              </div>
            </div>
            """

        with open("operador.html", "r", encoding="utf-8") as f:
            template = f.read()

        html_final = template.replace("{{CHANNELS_GRID}}", canais_html)\
                             .replace("{{REQUESTS_LIST}}", solicitacoes_html)

        self._enviar_html(html_final)

    def _enviar_html(self, conteudo_html):
        """Envia resposta HTML formatada."""
        body = conteudo_html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def obter_ip_local():
    """Descobre o IP da máquina na rede local."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def iniciar_servidor():
    banco.inicializar_banco()
    ip_local = obter_ip_local()

    print("=" * 60)
    print(" === SERVIDOR MESA DE SOM VIRTUAL (SEM JS) INICIADO ===")
    print("=" * 60)
    print(f" Acesso Local (este PC):  http://localhost:{PORT}")
    print(f" Tela do Musico:          http://{ip_local}:{PORT}")
    print(f" Tela do Operador:        http://{ip_local}:{PORT}/operador")
    print("=" * 60)
    print(" Pressione Ctrl+C para encerrar o servidor.")
    print("-" * 60)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), MesaSomSemJSHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")

if __name__ == "__main__":
    iniciar_servidor()
