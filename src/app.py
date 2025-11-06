import streamlit as st
import base64
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Portal do Calouro - DCC/UFRJ",
    page_icon="assets/logo_ic.png",
    layout="wide"
)

# --- CSS Customizado ---
# REMOVIDO: position: fixed e todos os ajustes de padding/z-index.
# Agora o header é mais simples e rola com a página.
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #ffffff;
        border-bottom: 1px solid #e0e0e0;
        width: 100%;
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .header-logo img {
        height: 60px;
    }
   
    .header-nav a {
        margin-left: 1.5rem;
        text-decoration: none;
        color: #003366; 
        font-weight: bold;
        font-size: 1rem;
    }
    .header-nav a:hover {
        text-decoration: underline;
    }
    
    /* Âncoras para o scroll (não precisam mais de ajuste de 'top') */
    a.anchor {
        display: block;
        position: relative;
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# --- Dados Fixos do Fórum (NOVA ESTRUTURA) ---
# Agora 'respostas_list' é uma lista de dicionários
perguntas_fixas = [
    {
        "texto": "Qual é o maior desafio do primeiro período?",
        "likes": 28,
        "respostas_count": 3,
        "tempo": "2 dias atrás",
        "respostas_list": [
            {"autor": "Ana B.", "texto": "Com certeza é Cálculo 1. A matéria é densa e o ritmo é rápido. Foque nas listas de exercício desde o dia 1!"},
            {"autor": "Marcos G. ", "texto": "Pra mim foi a gestão de tempo. São muitas matérias novas (Cálculo, ICC, IPD, Álgebra Linear) ao mesmo tempo."},
            {"autor": "Prof. Alan ", "texto": "O maior desafio é aprender a estudar de verdade. A faculdade é outro nível de profundidade e autonomia."}
        ]
    },
    {
        "texto": "Precisa ter um notebook para fazer ciência da computação?",
        "likes": 42,
        "respostas_count": 2,
        "tempo": "3 dias atrás",
        "respostas_list": [
            {"autor": "Lucas F. ", "texto": "Não é *obrigatório*, os laboratórios do IC (Labb-C) são muito bons e têm tudo que você precisa. Mas... ajuda muito. Ter seu próprio ambiente para estudar em casa ou na biblioteca faz uma diferença enorme na produtividade."},
            {"autor": "Carla", "texto": "Recomendo fortemente. Facilita para fazer os trabalhos em casa e rodar os códigos das aulas."}
        ]
    },
    {
        "texto": "Qual é a melhor editor de código / IDE para quem está começando programar em C?",
        "likes": 19,
        "respostas_count": 2,
        "tempo": "4 dias atrás",
        "respostas_list": [
            {"autor": "Julia T.", "texto": "VS Code (Visual Studio Code) é o mais popular hoje em dia. É leve, tem muitas extensões e a maioria dos veteranos usa. Você vai usar ele pra quase tudo na faculdade."},
            {"autor": "Rafael P.", "texto": "Se você quer se acostumar com o ambiente que vai usar nos laboratórios, aprenda o básico de um editor de terminal como Vim ou Nano. Mas para o dia a dia, VS Code."}
        ]
    },
    {
        "texto": "É utilizado Linux nos laboratórios da faculdade?",
        "likes": 31,
        "respostas_count": 2,
        "tempo": "5 dias atrás",
        "respostas_list": [
            {"autor": "Ryan Braga", "texto": "Sim! Todos os computadores dos laboratórios do IC rodam Linux (geralmente alguma distribuição como Ubuntu ou Debian)."},
            {"autor": "Beatriz M.", "texto": "Sim. É uma ótima oportunidade para já ir se acostumando, porque você vai *precisar* usar Linux em várias matérias avançadas (como Redes e Sistemas Operacionais)."}
        ]
    },
    {
        "texto": "É verdade que o bandejão possui fila grande?",
        "likes": 15,
        "respostas_count": 2,
        "tempo": "5 dias atrás",
        "respostas_list": [
            {"autor": "Bernardo", "texto": "Depende do horário. Se você for 12:00 em ponto, sim, a fila vai ser gigante. Minha dica é ir 11:30 ou depois das 13:15."},
            {"autor": "Maria", "texto": "Fui hoje 12:30 e demorei 40 minutos na fila. Mas a comida tava boa!"}
        ]
    },
    {
        "texto": "Como funcionam as monitorias?",
        "likes": 22,
        "respostas_count": 2,
        "tempo": "6 dias atrás",
        "respostas_list": [
            {"autor": "Clara", "texto": "Cada matéria oferece horários de monitoria (geralmente divulgados no site do departamento ou pelo professor). Você pode aparecer lá no horário e sala indicados para tirar dúvidas sobre a matéria, listas ou provas. É de graça e ajuda DEMAIS."},
            {"autor": "Bruno V.", "texto": "Use e abuse da monitoria. É a melhor forma de não ficar para trás. Os monitores são alunos que já passaram pela matéria e sabem exatamente onde estão as dificuldades."}
        ]
    }
]

# --- Inicialização do Session State ---
if 'novas_perguntas' not in st.session_state:
    st.session_state.novas_perguntas = []


# --- Função para Exibir uma Pergunta (ATUALIZADA) ---
# Função reutilizável para criar o "card" de cada pergunta
def exibir_pergunta(pergunta):
    # 'st.container(border=True)' cria a caixa/card
    with st.container(border=True):
        st.markdown(f"#### {pergunta['texto']}")
        
        # --- MUDANÇA AQUI: Dividido em colunas ---
        col1, col2 = st.columns([0.8, 0.2]) # 80% para metadados, 20% para botão
        
        # Coluna 1: Metadados
        with col1:
            st.markdown(
                f"👍 **{pergunta['likes']}** likes &nbsp;&nbsp; | &nbsp;&nbsp; 💬 **{pergunta['respostas_count']}** Respostas &nbsp;&nbsp; | &nbsp;&nbsp; 🕒 {pergunta['tempo']}",
                unsafe_allow_html=True
            )
        
        # Coluna 2: Botão Responder
        with col2:
            # Usamos o texto da pergunta como 'key' para garantir que cada botão seja único
            if st.button("Responder", key=pergunta['texto']):
                st.toast("Funcionalidade ainda não implementada!", icon="🚧")
                
        # O 'st.expander' continua igual, com o design limpo
        with st.expander("Ver Respostas"):
            if not pergunta['respostas_list']:
                st.write("Ainda não há respostas para esta pergunta.")
            else:
                for resposta in pergunta['respostas_list']:
                    st.markdown(f"**{resposta['autor']}:** {resposta['texto']}")
                    st.divider() # Adiciona uma linha fina entre as respostas

# =====================================================================
# --- LAYOUT DA PÁGINA ---
# =====================================================================

# --- 1. Cabeçalho (com HTML e CSS) ---
# Este HTML agora é mais simples
st.markdown(
    """
    <div class="header">
        <div class="header-logo">
            <img src="app/static/logo_ic.png" alt="Logo IC UFRJ" height="80px">
        </div>
        <nav class="header-nav">
            <a href="#inicio">Início</a>
            <a href="#entrevistas">Entrevistas</a>
            <a href="#forum">Forum P&R</a>
        </nav>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 2. Seção Início ---
st.markdown('<a class="anchor" id="inicio"></a>', unsafe_allow_html=True) 
st.title("Boas-vindas ao Portal do Calouro!")
st.subheader("Um guia feito por veteranos para facilitar seus primeiros passos na UFRJ.")
st.write("""
Este é um espaço para tirar dúvidas, controlar a ansiedade e se conectar com os veteranos do curso de Ciência da Computação. 
Aqui você encontrará uma entrevista com veteranos e um fórum para tirar suas principais dúvidas sobre o curso e a vida na universidade.
""")
st.divider()


# --- 3. Seção Entrevistas ---
st.markdown('<a class="anchor" id="entrevistas"></a>', unsafe_allow_html=True)
st.header("🎙️ Entrevistas com Veteranos")
st.write("Reunimos alguns veteranos para compartilhar suas experiências, dar dicas valiosas e contar o que gostariam de saber quando eram calouros. Dê o play!")

video_path = "assets/final.mp4" 

try:
    # Abrimos o arquivo de vídeo em modo de leitura binária ('rb')
    video_file = open(video_path, 'rb')
    video_bytes = video_file.read()
    
    # st.video exibe o player
    st.video(video_bytes)

except FileNotFoundError:
    st.error(f"Erro: Vídeo '{video_path}' não encontrado. Verifique o caminho e o nome do arquivo.")

st.divider()


# --- 4. Seção Fórum P&R ---
st.markdown('<a class="anchor" id="forum"></a>', unsafe_allow_html=True)
st.header("💬 Fórum de Perguntas e Respostas")
st.write("Tem alguma dúvida? Deixe aqui! Veteranos e monitores estão de olho para ajudar.")

with st.form("nova_duvida_form", clear_on_submit=True):
    nova_pergunta_texto = st.text_area(
        "**Deixe sua dúvida aqui:**", 
        placeholder="Ex: Como me inscrevo na monitoria de ICC?"
    )
    submitted = st.form_submit_button("Enviar Dúvida")

    if submitted and nova_pergunta_texto:
        nova_pergunta_data = {
            "texto": nova_pergunta_texto,
            "likes": 0,
            "respostas_count": 0,
            "tempo": "agora mesmo",
            "respostas_list": [] # Começa com a nova estrutura
        }
        st.session_state.novas_perguntas.insert(0, nova_pergunta_data)
        st.success("Sua dúvida foi enviada! (Ela desaparecerá ao recarregar a página)")

st.subheader("Dúvidas Recentes")
if not st.session_state.novas_perguntas:
    st.info("Nenhuma nova dúvida foi enviada ainda.")

for p in st.session_state.novas_perguntas:
    exibir_pergunta(p)

st.subheader("Dúvidas Antigas" )
for p in perguntas_fixas:
    exibir_pergunta(p)


# --- Hack para o Logo no Cabeçalho (Ainda necessário) ---
# Este código converte seu logo_ic.png em base64
# para que o HTML no st.markdown possa exibi-lo.
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def build_markup_for_logo(
    png_file,
    alt_text="Logo",
):
    bin_str = get_base64_of_bin_file(png_file)
    if bin_str:
        return f"""
        <style>
            img[alt="{alt_text}"] {{
                content: url("data:image/png;base64,{bin_str}");
            }}
        </style>
        """
    return ""

logo_markup = build_markup_for_logo("assets/logo_ic.png", alt_text="Logo IC UFRJ")
st.markdown(logo_markup, unsafe_allow_html=True)