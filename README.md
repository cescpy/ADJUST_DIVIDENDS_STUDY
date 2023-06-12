# adjust_dividends_study
Study of various adjustments for dividends in historical price // Estudio de diferentes ajustes por dividendos en las cotizaciones históricas

'''
OBJETIVOS:
- Estudiar el impacto de los dividendos en las series de datos hitóricos de cotización.
- Estudiar diferentes métodos de ajuste de dividendos (los tradicionales y nuevas propuestas) y cálculo de rentabilidades históricas.
- Discernir sobre la mejor eleccion en el tratamiento de los datos según el tipo de backtests/análisis/comparativas/... a realizar en cada momento.
- Sentar las bases para elaborar una sistemática de trabajo adequada y viable para realizar BD's de datos históricos.
- Valorar la afectación de los impuestos en la rentabilidad real con reinversión de dividendos (o sin reinversión).
'''
'''
ESTUDIO DE DIFERENTES METODOS PARA EL AJUSTE DE DIVIDENDOS PARA LOS CALCULOS DE RENTABILIDAD:

CASO 1: DATOS SIN AJUSTAR A DIVIDENDOS OBTENIDOS DE Yahoo Finance

CASO 2: DATOS AJUSTADOS A DIVIDENDOS OBTENIDOS DE Yahoo Finance (en teoría ajustados por factor de ajuste)

CASO 3: AJUSTE CALCULADO POR METODO ESTANDAR DE DIVIDENDO PROPORCIONAL CON FACTOR DE AJUSTE
Fuentes:
https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/
?? https://albertlobo.com/markets/adjusted-ohlc-values
?? https://tradewithpython.com/cleaning-stock-dividend-data-using-pandas-and-calculating-dividend-factor

CASO 4: AJUSTE DE COTIZACION >> DATOS SIN AJUSTAR + DIVIDENDOS GUARDADOS SIN RENTABILIDAD
Limitaciones del cálculo: 
    - Se supone que se cobra el dividendo en la fecha ex-dividend, lo cual normalmente no es cierto.
    - No tiene en cuenta la carga fiscal de los dividendos.

CASO 5: AJUSTE DE COTIZACION >> DATOS SIN AJUSTAR + DIVIDENDOS REINVERTIDOS EN EL MISMO ACTIVO
Limitaciones del cálculo: 
    - Se supone que se cobra el dividendo en la fecha ex-dividend, lo cual normalmente no es cierto.
    - No tiene en cuenta la carga fiscal de los dividendos.
    - Podría ser equivalente a un ETF de acumulación.
Fuentes:
https://dqydj.com/stock-return-calculator/
https://www.dividendchannel.com/drip-returns-calculator/

CASO 6: AJUSTE DE COTIZACION >> DATOS SIN AJUSTAR + DIVIDENDOS REINVERTIDOS EN EL MISMO ACTIVO - CARGA FISCAL
Limitaciones del cálculo: 
- Se supone que se cobra el dividendo en la fecha ex-dividend, lo cual normalmente no es cierto.
- Se supone que se pagan los impuestos en el momento de cobrar el dividendom, lo cual no es cierto.
'''

'''
CONCLUSIONES
==> El ajuste de dividendos cambia toda la serie de datos históricos anteriores!!
==> Los precios que tengo no són los que realmente fueron...
==> Pueden cambiar significativamente las señales pasadas de indicadores, soportes, resistencias, etc... haciendo backtests
==> Además con datos ajustados cambia toda la serie histórica de datos a cada dividendo (si hago una BD no me sirven)
==> Pero en comparación de rentabilidades a largo plazo , si no ajusto o tengo en cuenta los dividendos, el resultado puede diferir muchísimo del real
!!  PARA HACER COMPARACIONES DE RENTABILIDADES ES IMPRESCINDIBLE REALIZAR ALGUN AJUSTE DE DIVIDENDOS (SOBRETODO A LARGO PLAZO)

Idealmente: Trabajar siempre con datos no ajustados e incluir en los cáculos y backtest los posibles cobros de dividendos
(Aunque en algunas ocasiones puede ser excesivamente engorroso...)

Entonces idealmente:
- Backtest intradia     >> Datos sin ajustar (trabajamos sobre lo que realmente fué)
- Backtest swing        >> Datos sin ajustar + ¿Cálculo de si se han recivido dividendos? 
(Valorar en cada caso porque incluir los dividendos también puede distorsionar el resultado si no se buscaba recivir dividendos...)

- Estrategias Buy&Hold  >> Todos lo datos ajustados a dividendos!! O sin ajustar + calculo alternativo de suma dividendos recividos...
- Comparación rentabilidades a plazo   >> Todos lo datos ajustados a dividendos!! O sin ajustar + calculo alternativo de suma dividendos recividos...

- Uso de Benchmark >> El Benchmark tiene que ser con datos ajustados!! O estremos subestimando la rentabilidad del Benchmark


SOLUCIÓN PARA HACER UNA BASE DE DATOS DE COTIZACIONES HISTÓRICAS:
- Recopilar y guardar los datos no ajustados + dividendos + ¿splits? (los splits parece que acostumbran a venir ajustados siempre por defecto)
- Como estos no deben cambiar con el tiempo se pueden actualizar datos nuevos sobre los que ya se tienen.
- Tener una función para convertir los datos no ajustados a ajustados con los datos guardados de dividendos ¿y splits?
 

A ESTUDIAR: hacer un ajustador de dividendos de estilo TOTAL RETURN para comparaciones de rentabilidades a plazo.

HECHOS OBSERVADOS A ESTUDIAR:
- En los ÍNDICES (SPX se ha observado) no se realizan ajustes por dividendo? 

--> Tiene sentido utilizar un índice como Benchmark si no se puede invertir directamente en esa cotización?
--> Estamos comparando contra una cotización que no incluye ni tiene en cuenta la rentabilidad por dividendo?
(Por ejemplo si comparo el SPY incluyendo rentabilidad del dividendo contra el SPX me sale superior en la del SPY...)

SIMPLIFICACIÓN DE CASOS SIMILARES: 
- Los casos 2,3 y 5 són prácticamente iguales.
- Curiosamente el caso 5 sale idéntico al caso 2, pero no debería ser así (¿nos enganya YF sobre el método de cálculo que utiliza?).
- En cambio el caso 3 debería ser idéntico al caso 2 pero no es exacto del todo.

REFLEXIÓN EXTRA: Para realizar AT (Analisis Técnico) ajuste o no ajuste?
>> El AT puede cambiar bastante de una serie ajustada o una sin ajustar. 
>> Pero que importa más, la fiabilidad del AT en si o que sea el AT que todo el mundo mira (profecías autocumplidas)??
'''

'''
CONTENIDO DE CADA COLUMNA DE LOS DF's:
caseX['Close']      ==> Precios originales sin ajuste (excepto 'case2' -> descarga ajustada de YF que incorporan ajuste estandar de dividendos) 
caseX['Dividends']  ==> Dividendos recividos 
caseX['Pct']        ==> Variación percentual diaria del caseX['Close'] 
caseX['Return']     ==> Rendimientos acumulados del caseX['Close'] 
caseX['NAV']        ==> NAV del caso en una cartera de xx.xxxx 'capital' (variable)
caseX['Close_Adjust']     ==> 'Close' de las serie, recalculado segun cada caso 
caseX['Return_Adjust']    ==>  Rendimientos acumulados del caseX['Close_Adjust'] 
caseX['Close_TR']   ==> 'Close'de la serie, recalculado segun el caso con sistema TOTAL RETURN
'''
