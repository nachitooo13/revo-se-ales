import pandas as pd
import time
import requests
import telegram
from datetime import datetime, timezone

# Datos del bot de Telegram
chat_id = '-1002129033539'
bot_token = '6573227109:AAEUSIaPvBcrNyc_RQbB9U64qK-01jvcB5I'
bot = telegram.Bot(token=bot_token)

# Registro de señales enviadas
last_signal_time = {}

# Función para calcular el RSI
def calculate_rsi(df, window=14):
    delta = df.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
    avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

while True:
    symbols = ['BTCUSDT','EURUSDT', 'SOLUSDT', 'ETHUSDT', 'BNBUSDT', 'LTCUSDT', 'DOGEUSDT', 
               'MATICUSDT', 'XRPUSDT', 'ADAUSDT', 'DOTUSDT', 'BCHUSDT', 'AVAXUSDT', 
               'FTMUSDT', 'ALGOUSDT', 'NEARUSDT']
    timeinterval = 5
    
    for symbol in symbols:
        # Construye la URL para obtener los datos de la criptomoneda en el intervalo de tiempo de 1 minutos
        url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={timeinterval}m&limit=300'
        data = requests.get(url).json()
        
        # Verifica si se obtuvieron datos correctamente
        if data:
            # Convierte los datos a un DataFrame de Pandas
            df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume',
                                             'close_time', 'qav', 'num_trades', 'taker_base_vol',
                                             'taker_quote_vol', 'is_best_match'])
            
            # Convierte la columna 'close' a tipo numérico
            df['close'] = pd.to_numeric(df['close'])
            
            # Calcula el RSI
            rsi = calculate_rsi(df['close'])
            
            # Verifica si hay suficientes datos para calcular el RSI
            if len(rsi) > 0:
                current_rsi = rsi.iloc[-1]
                
                # Verifica si el RSI está sobrecomprado o sobrevendido
                if current_rsi > 70:
                    # Verifica si se envió una señal anteriormente para este par dentro de los últimos 125 minutos
                    if symbol in last_signal_time and (datetime.now() - last_signal_time[symbol]).total_seconds() <= 7500:  # 125 minutos = 7500 segundos
                        # Verifica si la diferencia de tiempo entre las señales es de al menos 35 minutos
                        if (datetime.now() - last_signal_time[symbol]).total_seconds() >= 2100:  # 35 minutos = 2100 segundos
                            # Envía una alerta de posible divergencia
                            signal = f'🚨¡Alerta de Posible Divergencia!🚨\n💰{symbol} en SOBRECOMPRA!\n📈RSI: {current_rsi:.2f}\n💲Prepara VENTA!'
                            bot.sendMessage(chat_id=chat_id, text=signal)
                    else:
                        # Envía una alerta de sobrecompra
                        signal = f'⚠️¡Atención!⚠️\n💰{symbol} en Sobrecompra.\n📈RSI: {current_rsi:.2f}'
                        bot.sendMessage(chat_id=chat_id, text=signal)
                    
                    # Actualiza el tiempo de la última señal para este par
                    last_signal_time[symbol] = datetime.now()
                        
                elif current_rsi < 30:
                    # Verifica si se envió una señal anteriormente para este par dentro de los últimos 125 minutos
                    if symbol in last_signal_time and (datetime.now() - last_signal_time[symbol]).total_seconds() <= 7500:  # 125 minutos = 7500 segundos
                        # Verifica si la diferencia de tiempo entre las señales es de al menos 35 minutos
                        if (datetime.now() - last_signal_time[symbol]).total_seconds() >= 2100:  # 35 minutos = 2100 segundos
                            # Envía una alerta de posible divergencia
                            signal = f'🚨¡Alerta de Posible Divergencia!🚨\n💰{symbol} en SOBREVENTA!\n📈RSI: {current_rsi:.2f}\n💲Prepara COMPRA!'
                            bot.sendMessage(chat_id=chat_id, text=signal)
                    else:
                        # Envía una alerta de sobreventa
                        signal = f'⚠️¡Atención!⚠️\n💰{symbol} en Sobreventa.\n📈RSI: {current_rsi:.2f}'
                        bot.sendMessage(chat_id=chat_id, text=signal)
                    
                    # Actualiza el tiempo de la última señal para este par
                    last_signal_time[symbol] = datetime.now()
                
    # Espera 5 minutos antes de revisar nuevamente
    time.sleep(300)  # 300 segundos = 5 minutos