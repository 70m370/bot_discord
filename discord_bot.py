import requests
import time
import investpy
import discord
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from pytz import timezone
import pytz


# Web driver
options = Options()
options.add_argument('--no-sandbox')
options.headless = True

driver = webdriver.Chrome(options=options, executable_path='C:\chromedriver.exe') # caminho para o Web driver

#Bonds from investing
bondsbr = investpy.get_bonds_overview('brazil')
usbonds = investpy.get_bonds_overview('united states')

#USD overview through 10 diferent currencys
usdow = investpy.get_currency_crosses_overview('usd', n_results=10)

#USD/AUD - USD/MXN  - last moth uptade with highs and lows
USDAUD = investpy.currency_crosses.get_currency_cross_recent_data('USD/AUD', as_json=False, order='descending', interval='Daily')
USDAUD.head()
USDMXN = investpy.currency_crosses.get_currency_cross_recent_data('USD/MXN', as_json=False, order='descending', interval='Daily')
USDBRL = investpy.currency_crosses.get_currency_cross_recent_data('USD/BRL', as_json=False, order='descending', interval='Daily')

def vol_ptax():
    x = datetime.now()
    var_ptax = ""
    for i in range(0,1):
        continua = True
       # x = x - datetime.timedelta(1)
        if(x.weekday()>4):
            x = x - timedelta(x.weekday()-4)
        while(continua):
            d = x.strftime("%m-%d-%Y")
            dn = x.strftime("%d/%m/%Y")
            url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='USD'&@dataInicial='" + d +"'&@dataFinalCotacao='" + d +"'&$top=1000&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim"
            r = requests.get(url)
            dados = r.json()
            if(len(dados["value"]) == 0):
                print("Não existe informação para o dia:" + dn + " (feriado?)")
                x = x - timedelta(1)
            else:
                continua = False
        print("Recuperando VOL da PTAX para o dia: " + dn)
        cot = 0
        _temp = []
        for pr in dados["value"]:
            _temp.append(round(pr["cotacaoVenda"] * 1000, 1))
        if (len(_temp) == 5):
            var_ptax = dn + "\nP1:\t" + str(_temp[0]) + "\nP2:\t" + str(_temp[1]) + "\nP3:\t" + str(_temp[2]) + "\nP4:\t" + str(_temp[3]) + "\nOFICIAL:\t" + str(_temp[4])
            print(var_ptax)
        if str(_temp[0]) > str(_temp[1]) and str(_temp[0]) > str(_temp[2]) and str(_temp[0]) > str(_temp[3]):
            previa_maior = float(_temp[0])

        if str(_temp[1]) > str(_temp[0]) and str(_temp[1]) > str(_temp[2]) and str(_temp[1]) > str(_temp[3]):
            previa_maior = float(_temp[1])

        if str(_temp[2]) > str(_temp[0]) and str(_temp[2]) > str(_temp[1]) and str(_temp[2]) > str(_temp[3]):
            previa_maior = float(_temp[2])

        if str(_temp[3]) > str(_temp[0]) and str(_temp[3]) > str(_temp[1]) and str(_temp[3]) > str(_temp[2]):
            previa_maior = float(_temp[3])

            # menor previa
        if str(_temp[0]) < str(_temp[1]) and str(_temp[0]) < str(_temp[2]) and str(_temp[0]) < str(_temp[3]):
            previa_menor = float(_temp[0])

        if str(_temp[1]) < str(_temp[0]) and str(_temp[1]) < str(_temp[2]) and str(_temp[1]) < str(_temp[3]):
            previa_menor = float(_temp[1])

        if str(_temp[2]) < str(_temp[0]) and str(_temp[2]) < str(_temp[1]) and str(_temp[2]) < str(_temp[3]):
            previa_menor = float(_temp[2])

        if str(_temp[3]) < str(_temp[0]) and str(_temp[3]) < str(_temp[1]) and str(_temp[3]) < str(_temp[2]):
            previa_menor = float(_temp[3])

        counter = 0
        volptax_op = previa_maior - previa_menor
        result_volptax = str(volptax_op)
        clean_vol_ptax = result_volptax[0:5]
        final_volptax = clean_vol_ptax
    return f'{dn}\tVOL PTAX:\t**{final_volptax}**'

#function loop and confirmation on web
def click_element(xpath,expected_url,delay=2):
    try:
        button = driver.find_elements_by_xpath(xpath)
    except NoSuchElementException:
        return 0
    print(len(button))
    print(button)
    time.sleep(delay)
    if driver.current_url == expected_url:
        return 1
    return 0

def CMEINV():
    driver.get("https://br.investing.com/currencies/brazilian-real-futures-streaming-chart")
    element = driver.find_element_by_xpath('//*[@id="last_last"]')
    element_format = element.text
    cmeval = 1 / float(element.text.replace(',', '.'))
    cmeval_str = str(cmeval)
    new_str = cmeval_str[0:5]
    final_cme = new_str
    return f'{final_cme}\t{element_format}'

def CDS():
    if driver.current_url != 'https://br.investing.com/rates-bonds/brazil-cds-5-years-usd':
        driver.get('https://br.investing.com/rates-bonds/brazil-cds-5-years-usd')
    cdsfive = driver.find_element_by_xpath('//*[@id="last_last"]')
    cdss = float(cdsfive.text.replace(',','.'))
    driver.refresh()
    return cdss

def riskbrazil():
    driver.get('https://www.puentenet.com/cotizaciones/riesgo-pais')
    time.sleep(1)
    element_risk = driver.find_element_by_xpath("/html/body/main/div[3]/div[2]/div/table/tbody/tr[2]/td[2]")
    final_elementr = element_risk.text
    return final_elementr

def dxy_value():
    driver.get("https://finance.yahoo.com/quote/DX-Y.NYB/")
    element = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    element_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    val_dxy = element.text
    number_dxy = element_number.text
    return f'**{number_dxy}**\t{val_dxy}'

def VIX():
    driver.get("https://finance.yahoo.com/quote/%5EVIX/")
    element = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    element_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    val_vix = element.text
    number_vix = element_number.text
    return f'**{number_vix}**\t{val_vix}'

def sp_500():
    driver.get('https://finance.yahoo.com/quote/%5EGSPC?p=%5EGSPC')
    sp_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    sp_variation = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    sp_final_number = sp_number.text
    sp_final_variation = sp_variation.text
    return f'**{sp_final_number}**\t{sp_final_variation}'


def morning_information():
    url = 'http://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-parametros-de-abertura-ptBR.asp'
    df = pd.read_html(url, decimal=',', thousands='.')
    dfs = df[0]
    dfss = dfs.tail(1)
    dfsss = dfss['Taxa de abertura']
    final_dfs = dfsss.to_string(index=False)
    risk_element = driver.get('https://www.puentenet.com/cotizaciones/riesgo-pais')
    element_risk = driver.find_element_by_xpath("/html/body/main/div[3]/div[2]/div/table/tbody/tr[2]/td[2]")
    final_elementr = element_risk.text
    cmeval = driver.get("https://br.investing.com/currencies/brazilian-real-futures-streaming-chart")
    element = driver.find_element_by_xpath('//*[@id="last_last"]')
    element_format = element.text
    cmeval = 1 / float(element.text.replace(',', '.'))
    cmeval_str = str(cmeval)
    new_str = cmeval_str[0:5]
    cmefinal = new_str

    return (f"O parâmetro de abertura é **{final_dfs}**\nO último valor do contrato REAL CME/investing é **{cmefinal}**\t{element_format}\nO Risco País no fechamento de ontem é **{final_elementr}** ")

def us5yt():
    us5y = driver.get('https://finance.yahoo.com/quote/%5EFVX?p=%5EFVX')
    us5y_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    us5y_val = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    us5yf_n = us5y_number.text
    us5yf_v = us5y_val.text
    return f'US 5Y = **{us5yf_n}**  {us5yf_v}'

def us10yt():
    us10y = driver.get("https://finance.yahoo.com/quote/%5ETNX?p=%5ETNX")
    us10y_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    us10y_val = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    us10y_n = us10y_number.text
    us10y_v = us10y_val.text
    return f'US 10Y = **{us10y_n}**  {us10y_v}'

def us30yt():
    us30y = driver.get('https://finance.yahoo.com/quote/%5ETYX?p=%5ETYX')
    us30y_number = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[1]')
    us30y_val = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[2]/div/div/div[4]/div/div/div/div[3]/div[1]/div/span[2]')
    us30y_n = us30y_number.text
    us30y_v = us30y_val.text
    return f'US 30Y = **{us30y_n}**   {us30y_v}'

#alertas/ loops

#DISCLAIMER
alert_disclaimer = ("""**DISCLAIMER:** @everyone RETORNOS PASSADOS NÃO SÃO GARANTIA DE RETORNO FUTURO. 
INVESTIMENTOS ENVOLVEM RISCOS E PODEM CAUSAR PERDAS AO INVESTIDOR. 
AS ESTRATÉGIAS E RACIONAIS AQUI FALADAS COM ATIVOS E DERIVATIVOS ENVOLVEM RISCOS E PODEM TRAZER PERDAS SUPERIORES AO CAPITAL INVESTIDO.
OS RESULTADOS PODEM VARIAR DE PESSOA PARA PESSOA. PARA SEGUIR AS ESTRATÉGIAS É NECESSÁRIO QUE VOCÊ DEDIQUE TEMPO. 
NUNCA INVISTA OU ESPECULE COM RECURSOS DESTINADOS A DESPESAS IMEDIATAS OU DE EMERGÊNCIA.
NÓS RECOMENDAMOS QUE ESTUDE SOMENTE NO MODO SIMULADOR ATÉ QUE TENHA EXPERIENCIA REAL DO QUE ESTÁ FAZENDO. 
É ALTAMENTE RECOMENDADO TAMBÉM QUE VOCÊ CONHEÇA SEU PERFIL DE INVESTIDOR. 
EM NENHUM MOMENTO RECOMENDAMOS COMPRA OU VENDA DE VALORES MOBILIÁRIOS. 
É IMPORTANTE LEMBRAR QUE VOCÊ É O ÚNICO RESPONSÁVEL POR SUAS OPERAÇÕES E PRECISA FICAR CLARO QUE NÃO SOMOS ANALISTAS DE VALORES MOBILIARIOS.
""")

alert_talk_to_me = ("""**12:30PM** @everyone""")


#BOT COMMAND PART
bot = commands.Bot(command_prefix='-')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("#comandos-bot"))
    print("Bot is ready.")

#comentario -morningcall / bot da valores de parametro de abertura etc
@bot.command()
async def morningcall(ctx):
    await ctx.send(f'{morning_information()}\n{vol_ptax()}')

#comentario -riscopais / shows the last value of close in Risk
@bot.command()
async def riscopais(ctx):
    await ctx.send(f'O Risco-país é = {riskbrazil()} ')

#comentario -cme / shows the last value of CME/1
@bot.command()
async def cme(ctx):
    await ctx.send(f'O último valor do contrato REAL CME/investing é = **{CMEINV()}**')

#comentario -usd / overview through other currency daily change
@bot.command()
async def usd(ctx):
    await ctx.send(usdow)

#comentario -usdaud / show the close of the last 21 days in USD/AUD
@bot.command()
async def usdaud(ctx):
    await ctx.send(USDAUD)

#comentario -usdmxn / show the last 21 days currency market close USD/MXN
@bot.command()
async def usdmxn(ctx):
    await ctx.send(USDMXN)

#comentario -usdbrl / shows the last 21 days of the market high, low, and close of usd/brl
@bot.command()
async def usdbrl(ctx):
    await ctx.send(USDBRL)

#comentario -bondsusa / show 1m to 30y USA bonds
@bot.command()
async def bondsusa(ctx):
    await ctx.send(usbonds)

#comentario -bondsbrazil / shows brazilian bonds 3m to 10y
@bot.command()
async def bondsbrazil(ctx):
    await ctx.send(bondsbr)

#comentario -cds5 / run selenium to get the lastest CDS 5 YEAR VALUE
@bot.command()
async def cds5(ctx):
    await ctx.send(f'O valor do CDS de 5 anos é = **{CDS()}**')

#comentario -vix
@bot.command()
async def vix(ctx):
    await ctx.send(f'últimos valores do VIX são = {VIX()}')

#comentario -dxy
@bot.command()
async def dxy(ctx):
    await ctx.send(f'últimos valores do DXY são = {dxy_value()}')

#US 5Y T, US 10Y T, US 30Y T
@bot.command()
async def treasury(ctx):
    await ctx.send(f'{us5yt()}\n{us10yt()}\n{us30yt()}')

@bot.command()
async def sp500(ctx):
    await ctx.send(f'Últimos Valores do S&P500 são = {sp_500()}')

@bot.command()
async def ptax(ctx,arg):
    def ptax_search():
        data = str(arg)
        dia = int(data[0:2])
        mes = int(data[3:5])
        ano = int(data[6:10])
        actual_day = datetime(ano, mes, dia)
        x = actual_day
        print(x)
        var_ptax = ""
        for i in range(0, 1):
            continua = True
            # x = x - datetime.timedelta(1)
            if (x.weekday() > 4):
                x = x - timedelta(x.weekday() - 4)
            while (continua):
                d = x.strftime("%m-%d-%Y")
                dn = x.strftime("%d/%m/%Y")
                url = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoMoedaPeriodo(moeda=@moeda,dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@moeda='USD'&@dataInicial='" + d + "'&@dataFinalCotacao='" + d + "'&$top=1000&$format=json&$select=cotacaoCompra,cotacaoVenda,dataHoraCotacao,tipoBoletim"
                r = requests.get(url)
                dados = r.json()
                if (len(dados["value"]) == 0):
                    print("Não existe informação para o dia:" + dn + " (feriado?)")
                    x = x - timedelta(1)
                else:
                    continua = False
                # print("Recuperando VOL da PTAX para o dia: " + dn)
                cot = 0
                _temp = []
                for pr in dados["value"]:
                    _temp.append(round(pr["cotacaoVenda"] * 1000, 1))

                if (len(dados["value"]) == 0):
                    var_ptax = ("Não existe informação para o dia:" + dn + " (feriado?)")

                if (len(_temp) == 5):
                    var_ptax = dn + "\nP1:\t" + str(_temp[0]) + "\nP2:\t" + str(_temp[1]) + "\nP3:\t" + str(
                        _temp[2]) + "\nP4:\t" + str(_temp[3]) + "\nOFICIAL:\t" + str(_temp[4])

                    # maior previa
                if str(_temp[0]) > str(_temp[1]) and str(_temp[0]) > str(_temp[2]) and str(_temp[0]) > str(_temp[3]):
                    previa_maior = float(_temp[0])

                if str(_temp[1]) > str(_temp[0]) and str(_temp[1]) > str(_temp[2]) and str(_temp[1]) > str(_temp[3]):
                    previa_maior = float(_temp[1])

                if str(_temp[2]) > str(_temp[0]) and str(_temp[2]) > str(_temp[1]) and str(_temp[2]) > str(_temp[3]):
                    previa_maior = float(_temp[2])

                if str(_temp[3]) > str(_temp[0]) and str(_temp[3]) > str(_temp[1]) and str(_temp[3]) > str(_temp[2]):
                    previa_maior = float(_temp[3])

                    # menor previa
                if str(_temp[0]) < str(_temp[1]) and str(_temp[0]) < str(_temp[2]) and str(_temp[0]) < str(_temp[3]):
                    previa_menor = float(_temp[0])

                if str(_temp[1]) < str(_temp[0]) and str(_temp[1]) < str(_temp[2]) and str(_temp[1]) < str(_temp[3]):
                    previa_menor = float(_temp[1])

                if str(_temp[2]) < str(_temp[0]) and str(_temp[2]) < str(_temp[1]) and str(_temp[2]) < str(_temp[3]):
                    previa_menor = float(_temp[2])

                if str(_temp[3]) < str(_temp[0]) and str(_temp[3]) < str(_temp[1]) and str(_temp[3]) < str(_temp[2]):
                    previa_menor = float(_temp[3])

                counter = 0
                volptax_op = previa_maior - previa_menor
                result_volptax = str(volptax_op)
                clean_vol_ptax = result_volptax[0:5]
                final_volpatx = clean_vol_ptax

        return f'{var_ptax}\nVOL PTAX:\t**{final_volpatx}**'
    await ctx.send(ptax_search())

@bot.command()
async def calendario(ctx):
    def calendario_hour_news_country():
        driver.get('https://br.investing.com/economic-calendar/')
        lista_restante = ""
        lista_brl = ""
        lista_usd = ""
        rows = driver.find_elements_by_xpath("/html/body/div[5]/section/div[6]/table/tbody/tr")
        rows_len = len(rows) - 1

        for count in range(rows_len):
            counter = count + 1
            element_hour = driver.find_element_by_xpath(
                f'/html/body/div[5]/section/div[6]/table/tbody/tr[{1 + counter}]/td[1]').text
            element_country = driver.find_element_by_xpath(
                f'html/body/div[5]/section/div[6]/table/tbody/tr[{1 + counter}]/td[2]').text
            element_news = driver.find_element_by_xpath(
                f'/html/body/div[5]/section/div[6]/table/tbody/tr[{1 + counter}]/td[4]').text
            linha = f'{element_hour}\t{element_country}\t{element_news}'

            country = element_country.strip()

            if (country == "BRL"):
                lista_brl = lista_brl + f'{linha}\n'
            elif (country == "USD"):
                lista_usd = lista_usd + f'{linha}\n'
            else:
                lista_restante = lista_restante + f'{linha}\n'

        return f'Noticias BRL\n{lista_brl}\nNoticias USD\n{lista_usd}'
    await ctx.send(calendario_hour_news_country()[0:1999]) # limitação de caracteres por mensagem no discord


#Loop 12:30
@tasks.loop(hours=1)
async def talktomeloop():
    now = datetime.now(timezone('America/Sao_Paulo'))
    start = now.replace(hour=10, minute=00, second=0, microsecond=0)
    end = now.replace(hour=12, minute=00, second=0, microsecond=0)
    if now.weekday() < 5 and start <= now <= end:
        bot_enter_channel = bot.get_channel('') #id canal
        print(f"Bot_comment_meiodia{bot_enter_channel}")
        await bot_enter_channel.send(alert_talk_to_me)

@talktomeloop.before_loop
async def before():
    await bot.wait_until_ready()
    print("talktomeloop_READY")

#loop disclaimer
@tasks.loop(hours=2) #função async discor.py para criar os loops
async def disclaimerloop():
    utc = pytz.utc
    now = datetime.now(timezone('America/Sao_Paulo')) #utilização do pytz para ajustar ao horario brasileiro/diferente do servidor
    start = now.replace(hour=8, minute=30, second=0, microsecond=0)
    end = now.replace(hour=18, minute=50, second=0, microsecond=0)
    if now.weekday() < 5 and start <= now <= end:
        entra_canal = bot.get_channel('') #id canal
        print(f"Bot_comment_disclaimer{entra_canal}")
        await entra_canal.send(alert_disclaimer)

@disclaimerloop.before_loop
async def before():
    await bot.wait_until_ready()
    print("disclaimerloop READY")


disclaimerloop.start()
talktomeloop.start()

bot.run(' ') # key do seu bot