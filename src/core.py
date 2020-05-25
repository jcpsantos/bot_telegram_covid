from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext
from conf.settings import BASE_API_URL, TELEGRAM_TOKEN, BASE_CSV_URL, BASE_GRAFICO_URL, IMAGE_GRAFICO
import pandas as pd 
import io
import requests
import logging
import datetime
import matplotlib.pyplot as plt


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def base(city):
    url = BASE_API_URL+city
    r = requests.get(url).json()
    base = r['results']
    return base

def base_br():
    url=BASE_CSV_URL
    s = requests.get(url).content
    dados = pd.read_csv(io.StringIO(s.decode('utf-8')))
    dados = dados.loc[dados['state'] == 'TOTAL']
    dados = dados.to_dict(orient='records')
    return dados[0]

def base_grafico():
    url=BASE_GRAFICO_URL
    img = IMAGE_GRAFICO
    s = requests.get(url).content
    dados = pd.read_csv(io.StringIO(s.decode('utf-8')))
    dados = dados.loc[dados['state'] == 'TOTAL']
    data = dados['date'].tail(7)
    total = dados['totalCases'].tail(7)
    
    fig, ax = plt.subplots()
    ax.plot(data, total)
    ax.set(xlabel='Data', ylabel='Quantidade de Casos',
       title='Quantidade de Casos de Covid19 nos últimos 7 dias')
    ax.grid()
    plt.tick_params(labelcolor='r', labelsize='small', width=10)
    fig.savefig(img)
    return img


def start(update, context):
    update.message.reply_text('Olá você estará recebendo atualizações dos dados sobre a COVID 19  no Brasil.\nPara receber as atualizações sobre uma cidade especifica \nDigite /cidade <nome da cidade> \nEx.: /cidade Salvador\nPara parar as atualizações\nDigite /stop \nPara receber dados de Covid19 no Brasil imediatamente \nDigite /brasil \nPara receber um gráfico com a atualização dos casos nos últimos 7 dias: \nDigite /grafico \n\n Fonte de Dados \nMinistério da Saúde e Secretárias Estaduais \nhttps://covid19br.wcota.me/ \nhttps://brasil.io/dataset/covid19/caso_full/')
    new_job = context.job_queue.run_repeating(callback_br, context=update.message.chat_id, interval=28800)
    context.chat_data['job'] = new_job

def unknown(update, context):
    response_message = "Para receber as atualizações sobre uma cidade especifica \nDigite /cidade <nome da cidade> \nEx.: /cidade Salvador\nPara parar as atualizações\nDigite /stop \nPara receber dados de Covid19 no Brasil imediatamente \nDigite /brasil"
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=response_message
    )

def now(update, context):
    dados = base_br()
    date = str(dados['date']).split("-")
    response_message = "Covid19 no Brasil \n\nData de Atualização: "+str(date[2])+"-"+str(date[1])+"-"+str(date[0])+"\n\nCasos Confirmados: "+str(dados['totalCases'])+"\n\nÓbitos: "+str(dados['deaths'])+"\n\nRecuperados: "+str(int(dados['recovered']))+"\n\nSuspeitos: "+str(int(dados['suspects']))+"\n\nTestes: "+str(int(dados['tests']))+"\n\nNovos Casos: "+str(dados['newCases'])+"\nNovos Óbtios: "+str(dados['newDeaths'])+"\n\nCasos por 100 mil Hab.:"+str(round(float(dados['totalCases_per_100k_inhabitants']), 2))+"\n\nÓbitos por 100 mil Hab.: "+str(round(float(dados['deaths_per_100k_inhabitants']), 2))+"\n\nTestes por 100 mil Hab.: "+str(round(float(dados['tests_per_100k_inhabitants']), 2))
    grf = base_grafico()
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=response_message
    )
    context.bot.sendPhoto(
        chat_id=update.message.chat_id,
        photo=open(grf, 'rb')
    )

def grafico(update, context):
    grf = base_grafico()
    context.bot.sendPhoto(
        chat_id=update.message.chat_id,
        photo=open(grf, 'rb')
    )

def callback_br(context: CallbackContext):
    job = context.job
    dados = base_br()
    date = str(dados['date']).split("-")
    grf = base_grafico()
    response_message = "Covid19 no Brasil \n\nData de Atualização: "+str(date[2])+"-"+str(date[1])+"-"+str(date[0])+"\n\nCasos Confirmados: "+str(dados['totalCases'])+"\n\nÓbitos: "+str(dados['deaths'])+"\n\nRecuperados: "+str(int(dados['recovered']))+"\n\nSuspeitos: "+str(int(dados['suspects']))+"\n\nTestes: "+str(int(dados['tests']))+"\n\nNovos Casos: "+str(dados['newCases'])+"\n\nNovos Óbtios: "+str(dados['newDeaths'])+"\n\nCasos por 100 mil Hab.:"+str(round(float(dados['totalCases_per_100k_inhabitants']), 2))+"\n\nÓbitos por 100 mil Hab.: "+str(round(float(dados['deaths_per_100k_inhabitants']), 2))+"\n\nTestes por 100 mil Hab.: "+str(round(float(dados['tests_per_100k_inhabitants']), 2))
    context.bot.send_message(job.context, text=response_message)
    context.bot.sendPhoto(
        chat_id=update.message.chat_id,
        photo=open(grf, 'rb')
    )

def city(update,context):
    citys = context.args
    city = ' '.join(str(e) for e in citys)
    try:
        date = str(base(city)[0]['date']).split("-")
        response_message = "Cidade: "+str(base(city)[0]['city']) +"\nData da atualização: "+str(date[2])+"-"+str(date[1])+"-"+str(date[0])+"\nCasos Confirmados: "+str(base(city)[0]['confirmed'])+"\nÓbitos: "+str(base(city)[0]['deaths'])+"\nPopulação estimada: "+str(base(city)[0]['estimated_population_2019'])+"\nCasos por 100 mil Hab.: "+str(base(city)[0]['confirmed_per_100k_inhabitants'])
        update.message.reply_text('Olá você estará recebendo dados sobre a COVID 19 em '+str(base(city)[0]['city']))
        context.bot.send_message(chat_id = update.effective_chat.id , text=response_message)
    except (IndexError, ValueError):
        update.message.reply_text("Verifique a grafia utilizada, o nome da cidade tem que estar com a primeira letra maiúscula: \nEx.:/cidade Lauro de Freitas")

def stop(update, context):
    """Remove the job if the user changed their mind."""
    if 'job' not in context.chat_data:
        update.message.reply_text('Você não tem nenhuma atualização sobre Covid19 Ativa')
        return

    job = context.chat_data['job']
    job.schedule_removal()
    del context.chat_data['job']

    update.message.reply_text('As atualizações foram paradas com sucesso!')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Atualização "%s" causou erro "%s"', update, context.error)


def main():
    """Run bot."""
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("brasil", now))
    #dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler('cidade', city, pass_args=True,
                    pass_job_queue=True,
                    pass_chat_data=True))
    dp.add_handler(CommandHandler('grafico', grafico))
    dp.add_handler(CommandHandler("stop", stop, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print ("press CTRL + C to cancel.")
    main()