import discord
from discord.ext import commands
from discord.ui import Button, View
import os

TOKEN = os.environ['TOKEN']
CARGO_GRF_ID = int(os.environ['CARGO_GRF_ID'])
# Configurações
PIX_KEY = 'korppirag@gmail.com - Meu nome é Felippe'


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Opções
CHAO_OPCOES = ["chao padrao", "chao preto versao 1", "chao preto versao 2"]
FENDA_OPCOES = ["set da fenda 1 - selvagem", "set da fenda 2 - encantada", "set da fenda 3 - submarina", 
                "set da fenda 4 - maligna", "set da fenda 5 - reptiliana"]
DIMENSIONAL_OPCOES = ["set dimensional 1 - sol e sakura", "set dimensional 2 - era uma vez", 
                       "set dimensional 3 - idade das trevas", "set dimensional 4 - ocultistas", 
                       "set dimensional 5 - dimensao zero", "set dimensional 6 - ultima caçada"]
FONTE_DANO_OPCOES = ["Fonte de dano 1 - Runas", "Fonte de dano 2 - normal", "Fonte de dano 3 - qnomon", 
                     "Fonte de dano 4 - Pixels", "Fonte de dano 5 - asmodeus", "Fonte de dano 6 - lovebomb"]

# Sessões por usuário
sessoes = {}

class SessaoUsuario:
    def __init__(self):
        self.passo_atual = 0  # 0=chão, 1=fenda, 2=dimensional, 3=fonte1, 4=fonte2
        self.escolhas = {
            "chao": None,
            "fenda": None,
            "dimensional": None,
            "fonte_dano_1": None,
            "fonte_dano_2": None
        }
        self.mensagens = {}  # Armazena as mensagens do bot por passo

def criar_botoes(opcoes, passo):
    view = View()
    for i, opcao in enumerate(opcoes):
        btn = Button(label=opcao, custom_id=str(i), style=discord.ButtonStyle.primary)
        btn.callback = lambda i, p=passo: responder(i, p)
        view.add_item(btn)
    if passo > 0:
        btn_voltar = Button(label="Voltar", style=discord.ButtonStyle.danger)
        btn_voltar.callback = lambda i: voltar(i)
        view.add_item(btn_voltar)
    return view

@bot.command(name="comprar")
async def comprar(ctx):
    user_id = ctx.author.id
    sessoes[user_id] = SessaoUsuario()

    if ctx.guild:
        await ctx.send(f"{ctx.author.mention}, vou te enviar as opções no privado!")
    else:
        await ctx.send("Use este comando em um servidor.")
        return

    try:
        await ctx.author.send(" # Vamos começar seu pedido! Faça suas escolhas, por favor::")
        await enviar_pergunta(ctx.author, 0)
    except discord.Forbidden:
        await ctx.send(f"{ctx.author.mention}, habilite DMs para receber o formulário!")

async def enviar_pergunta(user, passo):
    user_id = user.id
    sessao = sessoes[user_id]
    sessao.passo_atual = passo

    perguntas = [
        (" ## Escolha o tipo de chão:", CHAO_OPCOES),
        (" ## Escolha o set da fenda:", FENDA_OPCOES),
        (" ## Escolha o set dimensional:", DIMENSIONAL_OPCOES),
        (" ## Escolha a **primeira** fonte de dano:", FONTE_DANO_OPCOES),
        (" ## Escolha a **segunda** fonte de dano:", FONTE_DANO_OPCOES)
    ]

    pergunta, opcoes = perguntas[passo]
    view = criar_botoes(opcoes, passo)

    # Apaga a mensagem anterior se existir
    if passo in sessao.mensagens:
        try:
            await sessao.mensagens[passo].delete()
        except:
            pass

    # Envia a nova mensagem e armazena
    mensagem = await user.send(pergunta, view=view)
    sessao.mensagens[passo] = mensagem

async def responder(interaction, passo):
    user_id = interaction.user.id
    sessao = sessoes[user_id]

    escolha_idx = int(interaction.data["custom_id"])
    chaves = ["chao", "fenda", "dimensional", "fonte_dano_1", "fonte_dano_2"]
    opcoes = [CHAO_OPCOES, FENDA_OPCOES, DIMENSIONAL_OPCOES, FONTE_DANO_OPCOES, FONTE_DANO_OPCOES]

    sessao.escolhas[chaves[passo]] = opcoes[passo][escolha_idx]

    if passo < 4:
        await enviar_pergunta(interaction.user, passo + 1)
    else:
        await finalizar_pedido(interaction.user)

    await interaction.response.defer()

async def voltar(interaction):
    user_id = interaction.user.id
    sessao = sessoes[user_id]

    if sessao.passo_atual > 0:
        # Apaga a mensagem atual
        try:
            await sessao.mensagens[sessao.passo_atual].delete()
        except:
            pass

        # Reseta escolhas dos passos seguintes
        chaves = ["chao", "fenda", "dimensional", "fonte_dano_1", "fonte_dano_2"]
        for i in range(sessao.passo_atual, 5):
            sessao.escolhas[chaves[i]] = None

        # Volta ao passo anterior
        await enviar_pergunta(interaction.user, sessao.passo_atual - 1)

    await interaction.response.defer()

async def finalizar_pedido(user):
    user_id = user.id
    sessao = sessoes[user_id]

    resumo = (
        f"**Novo Pedido de <@{user_id}>:**\n"
        f"Chão: {sessao.escolhas['chao']}\n"
        f"Set da Fenda: {sessao.escolhas['fenda']}\n"
        f"Set Dimensional: {sessao.escolhas['dimensional']}\n"
        f"Fonte de Dano 1: {sessao.escolhas['fonte_dano_1']}\n"
        f"Fonte de Dano 2: {sessao.escolhas['fonte_dano_2']}\n"
    )

    dono = await bot.fetch_user(1255607557821563007)
    view = View()
    btn = Button(label="Confirmar Venda", style=discord.ButtonStyle.success)
    btn.callback = lambda i: confirmar_venda(i, user)
    view.add_item(btn)
    await dono.send(resumo, view=view)

    await user.send(f"Muito obrigado pela preferência! Seu pedido será confirmado após o envio do comprovante de `R$20 ou 60k de ROPs` para <@1255607557821563007>.\n\n Aqui está a chave PIX para pagamento: {PIX_KEY}\n\n Caso escolha pagar por ROPs, envie via RODEX para o personagem Pocket Korppi (é um Hyper Aprendiz nv 273)\n\n")

async def confirmar_venda(interaction, user):
    cargo = interaction.guild.get_role(CARGO_GRF_ID)
    await user.add_roles(cargo)
    await interaction.response.send_message(f"Cargo GRF concedido para {user.mention}!", ephemeral=True)

bot.run(TOKEN)
