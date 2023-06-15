# -*- coding: utf-8 -*-
'''
OBJETIVOS:
    - Estudiar el impacto de los dividendos en las series de datos hitóricos de cotización.
    - Estudiar diferentes métodos de ajuste de dividendos (los tradicionales y nuevas propuestas).
    - Discernir sobre la mejor eleccion en el tratamiento de los datos según el tipo de backtests/análisis/comparativas/... a realizar en cada momento.
    - Sentar las bases para elaborar una sistemática de trabajo adequada y viable para realizar BD's de datos históricos.
    - Valorar la afectación de los impuestos en la rentabilidad real con reinversión de dividendos (o sin reinversión).

.....
ver readme
'''

import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
 
start = '2020-01-01'
end = '2023-05-31'
ticker = 'KO'

capital = float(10000)
divitax = float(0.20)
if capital == 0 or divitax == 0:
    raise Exception("Error: El capital o divitax no pueden ser cero")


ticker_benchmark = False #'^SPX'   # False o 'ticker'
benchmark_adjust = True
# CALCULOS ACTIVO DE REFERENCIA
if (ticker_benchmark != False): 
    benchmark = yf.download(ticker_benchmark , start, end, interval = '1d', actions = True, auto_adjust= benchmark_adjust )   # AJUSTADO O NO AJUSTADO??
    
    benchmark['Pct'] = benchmark['Close'].pct_change().fillna(0)
    benchmark['Return'] = (1 + benchmark['Pct']).cumprod()
    benchmark['NAV'] = capital * benchmark['Return']
    benchmark['Close_recalc'] = benchmark['NAV'] / (benchmark['NAV'].iloc[0] / benchmark['Close'].iloc[0])
    benchmark['Return_recalc'] = benchmark['NAV'] / benchmark['NAV'].iloc[0] 
    benchmark['Close_TR'] = benchmark['Close'].iloc[0] * benchmark['Return_recalc']
    benchmark['%Profit'] = ((benchmark['Close_recalc']-benchmark['Close_recalc'][0]) / benchmark['Close_recalc'][0]) *100
    
# Creacion de Casos y alimentacion de datos
case1 = yf.download(ticker , start, end, interval = '1d', actions = True, auto_adjust=False)[['Close', 'Dividends', 'Stock Splits']].copy()
case2 = yf.download(ticker , start, end, interval = '1d', actions = True, auto_adjust=True)[['Close', 'Dividends', 'Stock Splits']].copy()
case3 = case1.copy()
case4 = case1.copy()
case5 = case1.copy()
case6 = case1.copy()


# CASO 1. DATOS SIN AJUSTAR A DIVIDENDOS DE YF. Con basico de rentabilidades
case1['Pct'] = case1['Close'].pct_change().fillna(0)
case1['Return'] = (1 + case1['Pct']).cumprod()
case1['NAV'] = capital * case1['Return']
case1['Close_recalc'] = case1['NAV'] / (case1['NAV'].iloc[0] / case1['Close'].iloc[0])
case1['Return_recalc'] = case1['NAV'] / case1['NAV'].iloc[0] 
case1['Close_TR'] = case1['Close'].iloc[0] * case1['Return_recalc']
case1['%Profit'] = ((case1['Close_recalc']-case1['Close_recalc'][0]) / case1['Close_recalc'][0]) *100

# CASO 2. DATOS AJUSTADOS A DIVIDENDOS DE YF. Con basico de rentabilidades
case2['Pct'] = case2['Close'].pct_change().fillna(0)
case2['Return'] = (1 + case2['Pct']).cumprod()
case2['NAV'] = capital * case2['Return']
case2['Close_recalc'] = case2['NAV'] / (case2['NAV'].iloc[-1] / case2['Close'].iloc[-1])
case2['Return_recalc'] = case2['NAV'] / case2['NAV'].iloc[0] 
case2['Close_TR'] = case1['Close'].iloc[0] * case2['Return_recalc']    # Precio de origen de la serie no ajustada
case2['%Profit'] = ((case2['Close_recalc']-case2['Close_recalc'][0]) / case2['Close_recalc'][0]) *100

## CASO 3. AJUSTE TEORICO DE DIVIDENDOS. 
## INTENTO IMITAR EL METODO DE AJUSTE CLASICO DE DIVIDENDO PROPORCIONAL POR 'FACTOR DE AJUSTE'

def calculate_adjusted_prices_mod(df, column):
    '''
    FUNCION MODIFICADA DE https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/
    PASANDO DE LOS SPLITS. SE DEBERÍA REVISAR COMO PUEDE AFECTAR EN DIVERSOS CASOS.
    SI SE QUISIERA UTILIZAR PARA BD DE DATOS HISTÓRICOS SE DEBERÍA REVISAR
    '''
    """ Vectorized approach for calculating the adjusted prices for the
    specified column in the provided DataFrame. This creates a new column
    called 'adj_<column name>' with the adjusted prices. This function requires
    that the DataFrame have columns with dividend and split_ratio values.

    :param df: DataFrame with raw prices along with dividend and split_ratio
        values
    :param column: String of which price column should have adjusted prices
        created for it
    :return: DataFrame with the addition of the adjusted price column
    """
    adj_column = column + '_recalc'
    df = df.copy()
    # Reverse the DataFrame order, sorting by date in descending order
    df.sort_index(ascending=False, inplace=True)
    price_col = df[column].values
    # split_col = df['Stock Splits'].values
    dividend_col = df['Dividends'].values
    adj_price_col = np.zeros(len(df.index))
    adj_price_col[0] = price_col[0]

    for i in range(1, len(price_col)):
        adj_price_col[i] = round((adj_price_col[i - 1] + adj_price_col[i - 1] *
                                  (((price_col[i]) -
                                    price_col[i - 1] -
                                    dividend_col[i - 1]) / price_col[i - 1])), 4)

    df[adj_column] = adj_price_col
    # Change the DataFrame order back to dates ascending
    df.sort_index(ascending=True, inplace=True)
    return df

case3 = calculate_adjusted_prices_mod(case3, 'Close')
case3['Pct'] = case3['Close_recalc'].pct_change().fillna(0)
case3['Return_recalc'] = (1 + case3['Pct']).cumprod()
case3['NAV'] = capital * case3['Return_recalc']
case3['Close_TR'] = case3['Close'].iloc[0] * case3['Return_recalc'] 
case3['%Profit'] = ((case3['Close_recalc']-case3['Close_recalc'][0]) / case3['Close_recalc'][0]) *100

# CASO 4. AJUSTE DE DIVIDENDOS SIN REINVERSION DE LOS DIVIDENDOS.
# EQUIVALE A LA RENTABILIDAD FINAL CONSIDERANDO QUE METO LOS DIVIDENDOS EN EL CERDITO (HUCHA) Y LOS MANTENGO AHÍ SIN RENTABILIDAD
case4['Pct'] = case4['Close'].pct_change().fillna(0)
case4['Return'] = (1 + case4['Pct']).cumprod()
case4['NAV_sindivi'] = capital * case4['Return']
case4['Dividend_'] = ((case4['NAV_sindivi'] / case4['Close']) * case4['Dividends'])
case4['Dividend_Acum'] = case4['Dividend_'].cumsum()
case4['NAV'] = case4['NAV_sindivi'] + case4['Dividend_Acum']
case4['Close_recalc'] = case4['NAV'] / (case4['NAV'].iloc[-1] / case4['Close'].iloc[-1])
case4['Return_recalc'] = case4['NAV'] / case4['NAV'].iloc[0] 
case4['Close_TR'] = case4['Close'].iloc[0] * case4['Return_recalc']
case4['%Profit'] = ((case4['Close_recalc']-case4['Close_recalc'][0]) / case4['Close_recalc'][0]) *100

# CASO 5. AJUSTE DE DIVIDENDOS CON REINVERSION DE LOS DIVIDENDOS.
# EQUIVALE A LA RENTABILIDAD FINAL CONSIDERANDO QUE REINVIERTO LOS DIVIDENDOS EN EL MISMO ACTIVO
case5['Pct'] = case5['Close'].pct_change().fillna(0)
case5['NAV'] = capital
for i in range(1, len(case5)):
    case5['NAV'][i] = (case5['NAV'][i-1] * (1 + case5['Pct'][i])) + ((case5['NAV'][i-1] / case5['Close'][i-1]) * case5['Dividends'][i])

case5['Close_recalc'] = case5['NAV'] / (case5['NAV'].iloc[-1] / case5['Close'].iloc[-1])
case5['Return_recalc'] = case5['NAV'] / case5['NAV'].iloc[0] 
case5['Close_TR'] = case5['Close'].iloc[0] * case5['Return_recalc']
case5['%Profit'] = ((case5['Close_recalc']-case5['Close_recalc'][0]) / case5['Close_recalc'][0]) *100

# CASO 6. AJUSTE DE DIVIDENDOS CON REINVERSION DE LOS DIVIDENDOS CONTEMPLANDO LA CARGA FISCAL.
# EQUIVALE A LA RENTABILIDAD FINAL CONSIDERANDO QUE REINVIERTO LOS DIVIDENDOS EN EL MISMO ACTIVO Y TENIENDO EN CUENTA LA CARGA FISCAL
case6['Pct'] = case6['Close'].pct_change().fillna(0)
case6['NAV'] = capital
for i in range(1, len(case6)):
    case6['NAV'][i] = (case6['NAV'][i-1] * (1 + case6['Pct'][i])) + (((case6['NAV'][i-1] / case6['Close'][i-1]) * case6['Dividends'][i]) * (1 -divitax))

case6['Close_recalc'] = case6['NAV'] / (case6['NAV'].iloc[-1] / case6['Close'].iloc[-1])
case6['Return_recalc'] = case6['NAV'] / case6['NAV'].iloc[0] 
case6['Close_TR'] = case6['Close'].iloc[0] * case6['Return_recalc']
case6['%Profit'] = ((case6['Close_recalc']-case6['Close_recalc'][0]) / case6['Close_recalc'][0]) *100



'''
GRAFICO
Se descartan en algunos graficos los casos 3 y 5 dado que se superponen con el caso 2.
Se pueden descomentar las lineas pertinentes sii se quieren comprobar los resultados de las series
'''
# GRAFICO DE COTIZACIONES AJUSTADAS Y SUS COMBINACIONES
fig, ax = plt.subplots(figsize=(12,6))
# Graficar cada columna 'Close' en un gráfico de líneas
if ticker_benchmark != False: 
    ax.plot(benchmark['Close_recalc'], label=f'BENCHMARK ({ticker_benchmark})')

ax.plot(case1['Close_recalc'], label='NO AJUSTADO')
ax.plot(case2['Close_recalc'], label='AJUSTADO')
# ax.plot(case3['Close_recalc'], label='AJUSTE PROPIO POR FACTOR')
# ax.plot(case4['Close_recalc'], label='AJUSTADO SIN REINVERSION DE DIVIDENDOS')
# ax.plot(case5['Close_recalc'], label='AJUSTADO CON REINVERSION DE DIVIDENDOS')
# ax.plot(case6['Close_recalc'], label='AJUSTADO CON REINVERSION - CARGA FISCAL')
ax.legend()
ax.set_xlabel('Fecha')
ax.set_ylabel('Precio de cierre')
plt.title(f'{ticker} - GRAFICO DE COTIZACIONES AJUSTADAS')
ax.grid(True)
plt.show()


# GRAFICO DE COTIZACIONES AJUSTADAS COMO 'TOTAL RETURN' Y SUS COMBINACIONES
fig, ax = plt.subplots(figsize=(12,6))
# Graficar cada columna 'Close_TR' en un gráfico de líneas
if ticker_benchmark != False: 
    ax.plot(benchmark['Close_TR'], label=f'BENCHMARK ({ticker_benchmark})')

ax.plot(case1['Close_TR'], label='NO AJUSTADO YF (PRECIO REAL)')
ax.plot(case2['Close_TR'], label='TR AJUSTADO YF')
# ax.plot(case3['Close_TR'], label='AJUSTE PROPIO POR FACTOR')
ax.plot(case4['Close_TR'], label='TR SIN REINVERSION DE DIVIDENDOS')
# ax.plot(case5['Close_TR'], label='TR CON REINVERSION DE DIVIDENDOS')
ax.plot(case6['Close_TR'], label='TR CON REINVERSION - CARGA FISCAL')
ax.legend()
ax.set_xlabel('Fecha')
ax.set_ylabel('Precio de cierre')
plt.title(f'{ticker} - GRAFICO DE COTIZACIONES AJUSTADAS CON SISTEMA "TOTAL RETURN"')
ax.grid(True)
plt.show()


# GRAFICO DE RETORNOS ACUMULADOS POR CASOS EN BASE 100 (se puede cambiar la base)
base = 10
fig, ax = plt.subplots(figsize=(12,6))
# Graficar cada columna 'Return' en un gráfico de líneas
if ticker_benchmark != False: 
    ax.plot((benchmark['Return_recalc'])*base , label=f'BENCHMARK ({ticker_benchmark})')

ax.plot((case1['Return_recalc'])*base, label='NO AJUSTADO YF')
ax.plot((case2['Return_recalc'])*base, label='AJUSTADO YF')
# ax.plot((case3['Return_recalc'])*100, label='AJUSTE PROPIO POR FACTOR')
ax.plot((case4['Return_recalc'])*base, label='AJUSTADO SIN REINVERSION DE DIVIDENDOS')
# ax.plot((case5['Return_recalc'])*100, label='AJUSTADO CON REINVERSION DE DIVIDENDOS')
ax.plot((case6['Return_recalc'])*base, label='AJUSTADO CON REINVERSION - CARGA FISCAL')
ax.legend()
ax.set_xlabel('Fecha')
ax.set_ylabel('Retornos acumulados')
plt.title(f'{ticker} - GRAFICO DE RETORNOS ACUMULADOS POR CASOS - BASE {str(base)}')
ax.grid(True)
plt.show()


# GRAFICO DE NAV POR CASOS 
fig, ax = plt.subplots(figsize=(12,6))
# Graficar cada columna 'NAV' en un gráfico de líneas
if ticker_benchmark != False: 
    ax.plot(benchmark['NAV'] , label=f'BENCHMARK ({ticker_benchmark})')

ax.plot(case1['NAV'], label='NO AJUSTADO YF')
ax.plot(case2['NAV'], label='AJUSTADO YF')
# ax.plot(case3['NAV'], label='AJUSTE PROPIO POR FACTOR')
ax.plot(case4['NAV'], label='AJUSTADO SIN REINVERSION DE DIVIDENDOS')
# ax.plot(case5['NAV'], label='AJUSTADO CON REINVERSIÓN DE DIVIDENDOS')
ax.plot(case6['NAV'], label='AJUSTADO CON REINVERSIÓN - CARGA FISCAL')
ax.legend()
ax.set_xlabel('Fecha')
ax.set_ylabel('Capital')
plt.title(f'{ticker} - GRAFICO DE NAV POR CASOS - EN BASE AL CAPITAL INICIAL')
ax.grid(True)
plt.show()


# GRAFICO DE % RENTABILIDAD
fig, ax = plt.subplots(figsize=(12,6))
# Graficar cada columna 'Return' en un gráfico de líneas
if ticker_benchmark != False: 
    ax.plot(benchmark['%Profit'] , label=f'BENCHMARK ({ticker_benchmark})')

ax.plot(case1['%Profit'], label='NO AJUSTADO')
ax.plot(case2['%Profit'], label='AJUSTADO')
# ax.plot(case3['%Profit'], label='AJUSTE PROPIO POR FACTOR')
ax.plot(case4['%Profit'], label='AJUSTADO SIN REINVERSION DE DIVIDENDOS')
# ax.plot(case5['%Profit'], label='AJUSTADO CON REINVERSION DE DIVIDENDOS')
ax.plot(case6['%Profit'], label='AJUSTADO CON REINVERSION - CARGA FISCAL')
ax.legend()
ax.set_xlabel('Fecha')
ax.set_ylabel('Rentabilidad %')
plt.title(f'{ticker} - GRAFICO DE % DE RENTABILIDAD')
ax.grid(True)
plt.show()







''' Comparacion series de yf según opciones de 'download()'
# Series sin ajustes y se incluye la columna 'Adj close'
# yf = yf.download(ticker , start, interval = '1d', actions = True, auto_adjust=False, back_adjust=False)
# Ajusta todas las columnas (Open, High, Low y Close)  
# yf_auto = yf.download(ticker , start, interval = '1d', actions = True, auto_adjust=True, back_adjust=False)
yf['Close'] == yf_back['Close']
yf['Adj Close'] == yf_auto['Close']    >>> No pasa la prueba de equal por diferencias mas pequeñas del 5to decimal
# son_iguales = np.array_equal(yf['Adj Close'][1:], yf_auto['Close'][1:])

No se exactamente que hace el back_adjust. Lo descarto de momento
# quotes_yfback = yf.download(ticker , start, interval = '1d', actions = True, auto_adjust=False, back_adjust=True)
# quotes_yfautoback = yf.download(ticker , start, interval = '1d', actions = True, auto_adjust=True, back_adjust=True)
'''






