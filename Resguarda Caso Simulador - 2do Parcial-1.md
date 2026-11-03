## CASO DE ESTUDIO · DIRECCIÓN DE OPERACIONES

## Resguarda: producir al ritmo de la demanda

Capacidad, cuello de botella y crecimiento en una planta de ensamblaje · Caso con datos para simulación

Caso preparado por Félix J. Rodriguez P. con fines docentes, como base para la discusión en clase y para la construcción de un tablero de simulación con herramientas de inteligencia artificial o de inteligencia de negocios. La empresa, las personas y las cifras son ficticias; la situación se inspira en el caso «Parcel Guard: Keeping Up with Demand» (Ivey Publishing, 2020), con datos y supuestos nuevos. No pretende ilustrar una gestión correcta o incorrecta.

| Parte | Contenido | Uso |
| --- | --- | --- |
| I. El caso | Narrativa de la situación y la decisión | Lectura previa y discusión en clase |
| II. Anexos de datos | Producto, proceso, personal, turnos, opciones, calidad, inventario, finanzas, espacio y demanda semanal | Datos de entrada del simulador |
| III. Guía del tablero | Objetivos, preguntas, requisitos, fórmulas, modelo de datos, valores de control y evaluación | Construcción y validación del tablero |

## Parte I. El caso

## Una semana para decidir

El lunes 28 de septiembre de 2026, Mariela Santos, directora de operaciones de Hogar Conectado del Caribe, S.R.L. (HCC), abrió el pronóstico de ventas que el equipo comercial había cerrado durante el fin de semana. Las cifras confirmaban lo que intuía desde el lanzamiento: la demanda de Resguarda, el buzón inteligente para paquetes de la empresa, superaría muy pronto la capacidad de la planta. El pronóstico base preveía 700 unidades en la primera semana de octubre, 1.300 a mediados de noviembre y un pico de 1.900 en la semana del Black Friday. La planta, con dos líneas de ensamblaje en un solo turno, producía algo más de 530 unidades por semana.

Andrés Peña, presidente de HCC, le había pedido una propuesta para la reunión del consejo del viernes 2 de octubre. No quería una lista de opciones, sino un tablero que permitiera ver, semana a semana, cuánto se produciría, cuánto se dejaría de vender y cuánto costaría cada alternativa en los distintos escenarios de demanda. «Si el consejo va a aprobar una inversión», le dijo, «quiero que pueda mover las variables y ver qué pasa».

## La empresa

HCC se fundó en 2014 en Santo Domingo como importadora de cerraduras electrónicas y cámaras para el hogar. En 2021 empezó a diseñar productos propios y en 2024 abrió una pequeña planta de ensamblaje en una nave alquilada dentro de una zona franca industrial de Santo Domingo Oeste. La empresa vendía en República Dominicana, Puerto Rico, Panamá y, a través de distribuidores de comercio electrónico, en Florida. En 2025 facturó US\$ 14,2 millones con 96 empleados, de los cuales 15 trabajaban en la planta.

La decisión de ensamblar localmente, en lugar de comprar el producto terminado a un fabricante asiático, se tomó para reducir el plazo de entrega a los clientes del Caribe y de Florida (de ocho semanas a una), controlar la calidad y adaptar el producto a la humedad y la salinidad de la región.

## El producto y el mercado

Resguarda es un buzón de polímero reforzado, resistente a la intemperie, que se ancla junto a la puerta de la vivienda. Incorpora una cerradura electrónica, conexión Wi-Fi, una cámara activada por movimiento, una alarma y una aplicación móvil que avisa al propietario cuando se deposita un paquete. Se fabrica en dos versiones: R1 Estándar y R1 Pro, que añade una segunda cámara, una batería de respaldo y un módulo celular para zonas con Wi-Fi inestable. La versión Pro representaba el 30 % de los pedidos y el equipo comercial esperaba que llegara al 35 % a partir de abril de 2027 (Anexo 1).

El comercio electrónico en la región crecía a doble dígito y los robos de paquetes en urbanizaciones se habían convertido en un tema recurrente en la prensa. Dos cadenas de tiendas de mejoras para el hogar y un operador logístico de entregas a domicilio habían firmado acuerdos de distribución para la temporada de fin de año. La


demanda era estacional: Black Friday y Navidad concentraban las mayores compras, enero era un mes flojo y el Día de las Madres, a finales de mayo, generaba un segundo pico.

## La planta y el proceso

La planta ocupa 420 m² de la nave. Dos líneas idénticas de seis estaciones ocupan 240 m²; el resto se usa como almacén de componentes y producto terminado. Trabajan un supervisor, un manipulador de materiales, un técnico de retrabajo y seis personas en cada línea (Anexo 2).

El gabinete, la puerta y la base llegan moldeados desde un proveedor local. En la primera estación se monta el gabinete y se suelda por ultrasonido. En la segunda se arma el subconjunto de la puerta, de diseño complicado por el mecanismo de la cerradura. En la tercera se instalan la puerta y el arnés de cables. En la cuarta se completa el cableado y se montan los componentes eléctricos; en la versión Pro esta estación instala además la segunda cámara y el módulo celular. La quinta estación inspecciona visualmente cada unidad y la somete a una prueba eléctrica automatizada que admite tres unidades a la vez. La sexta empaca y paletiza en grupos de seis. Los tiempos estándar de cada estación figuran en el Anexo 3.

Cada cambio de variante en una línea exige cambiar plantillas, cargar otro programa de prueba y reabastecer componentes, lo que detiene la línea unos 20 minutos. Para limitar estas paradas, la planta produce en lotes de 100 unidades de una misma variante.

## Las primeras semanas de producción

Las seis semanas de producción piloto dejaron varias lecciones. Las líneas producían algo menos de lo previsto, con una media observada de 46 unidades en proceso por línea. El 4 % de las unidades Estándar y el 6 % de las Pro fallaban la prueba final; el técnico de retrabajo recuperaba ocho de cada diez y el resto se desechaba. Julio Cabrera, jefe de ingeniería industrial, observó que en las semanas con más pedidos Pro las colas se formaban en la estación de cableado y no en la de instalación de la puerta, que era la que él consideraba el cuello de botella.

Cabrera había preparado una propuesta para reequilibrar cada línea con ocho operadores. Su informe destacaba un «tiempo de ciclo medio» de 5,0 minutos por unidad y estimaba que la capacidad casi se duplicaría (Anexo 4).

## El pronóstico y sus dudas

Laura Méndez, directora comercial, presentó tres escenarios (Anexo 11). En el escenario base, al que asignaba un 50 % de probabilidad, la demanda alcanzaba 1.900 unidades en la semana del Black Friday, bajaba en enero y crecía después a un ritmo cercano al 0,8 % semanal. En el escenario optimista (25 %), los acuerdos con las cadenas se ampliaban a toda la región y la demanda superaba en un 20 % a la del escenario base desde noviembre. En el escenario de llenado de canal (25 %), los distribuidores compraban fuerte para la temporada, pero sus ventas finales eran menores de lo esperado y, a partir de enero, reducían los pedidos a unas 650 unidades semanales.

Ricardo Almonte, director financiero, recordó que el presupuesto de inversión del año fiscal estaba limitado a US\$ 120.000 sin aprobación expresa del consejo, y que el margen de Resguarda dependía mucho de no perder ventas en la temporada alta. «Cada Resguarda que no entregamos en noviembre es un cliente que compra el de la competencia», advirtió Méndez. «Y cada línea que montamos para un pico que no se repite es dinero parado», respondió Almonte.

## Las opciones

Santos y Cabrera habían identificado siete palancas, combinables entre sí (Anexo 6):

- Reequilibrar las líneas con ocho operadores. Requiere US\$ 9.000 en plantillas y herramientas por línea y tres semanas de preparación.

- Instalar una tercera línea. Igual a las actuales, con seis operadores y un manipulador adicional; US\$ 48.000 y ocho semanas de plazo.

- Añadir un segundo o un tercer turno. Sin inversión en equipos, pero con un líder por turno, primas salariales y un rendimiento menor que el del primer turno.


- Pasar a células de trabajo. Cada célula, de US\$ 15.000, la comparten tres trabajadores polivalentes que ensamblan la unidad completa.

- Instalar un dispositivo semiautomático para la puerta. Reduce los tiempos de las estaciones de la puerta; US\$ 22.000 por línea y diez semanas de plazo.

- Subcontratar el subconjunto de la puerta. El proveedor del gabinete lo entregaría armado y probado, con un sobrecoste por unidad y un límite de volumen.

- Trabajar sábados con horas extra. Disponible de inmediato, con un recargo del 50 % y un máximo de tres sábados al mes.

La planta tenía límites. Quedaban 180 m² libres en la nave y el propietario ofrecía 200 m² adicionales desde mediados de diciembre. Recursos Humanos podía incorporar como máximo doce personas por semana, y cada persona nueva necesitaba unas cuatro semanas para alcanzar el rendimiento estándar (Anexo 10).

## La decisión

Santos sabía que cualquier equipo que no se ordenara esa semana llegaría después del Black Friday. También sabía que la opción más barata para la temporada no tenía por qué ser la mejor para el resto del año, y que el consejo querría ver el riesgo de cada alternativa, no solo su resultado en el escenario base. El viernes debía presentar una recomendación y el tablero que la respaldara.

| Personaje | Cargo | Posición |
| --- | --- | --- |
| Mariela Santos | Directora de operaciones | Responsable de la decisión y del tablero |
| Andrés Peña | Presidente | Pide ver el riesgo de cada alternativa |
| Laura Méndez | Directora comercial | Prioriza no perder ventas en temporada |
| Ricardo Almonte | Director financiero | Limita la inversión y teme el exceso de capacidad |
| Julio Cabrera | Jefe de ingeniería industrial | Propone el reequilibrio a ocho operadores |


## Parte II. Anexos de datos

Moneda: dólares estadounidenses (US\$). Semana laboral de lunes a viernes. Los datos de esta parte son los parámetros de entrada del simulador.

*Anexo 1. Producto, precios y costes variables*

| Concepto | R1 Estándar | R1 Pro |
| --- | --- | --- |
| Precio neto medio a canales (US$/u) | 129,00 | 169,00 |
| Materiales y componentes (US$/u) | 58,00 | 74,00 |
| Margen de contribución antes de mano de obra (US$/u) | 71,00 | 95,00 |
| Participación en la demanda, semanas 1–26 | 70 % | 30 % |
| Participación en la demanda, semanas 27–52 | 65 % | 35 % |
| Devoluciones en garantía (% de unidades vendidas) | 0,8 % | 0,8 % |
| Coste por devolución en garantía (US$) | 85,00 | 85,00 |

*Anexo 2. Plantilla actual y costes laborales*

| Puesto | Personas actuales | Salario (US$/h) | Observaciones |
| --- | --- | --- | --- |
| Operador de línea (estaciones E1–E4 y E6) | 10 | 6,50 | 5 por línea |
| Técnico de pruebas (estación E5) | 2 | 7,50 | 1 por línea |
| Manipulador de materiales | 1 | 7,50 | Atiende hasta 3 líneas o 6 células por turno |
| Técnico de retrabajo | 1 | 7,50 | Fuera de línea; 1 por turno |
| Líder de turno (turnos 2.º y 3.º) | 0 | 9,00 | Sustituye al manipulador en esos turnos |
| Trabajador polivalente de célula | 0 | 7,20 | Ensambla la unidad completa |
| Supervisor de planta | 1 | US$ 1.050 por semana | Fijo, uno para toda la planta |

Cargas sociales y beneficios: 30 % sobre el salario. Horas pagadas por turno: 8,0 (esquema de 1 o 2 turnos) y 7,5 (esquema de 3 turnos). Contratación y formación inicial: US\$ 350 por persona nueva.

## Anexo 3. Ruta de proceso y tiempos estándar (línea de seis estaciones)

|   | Estación Operación | Estándar (min/u) | Pro (min/u) | Variabilidad (CV) | Base del tiempo |
| --- | --- | --- | --- | --- | --- |
| E1 | Gabinete: montaje y soldadura ultrasónica | 6,50 | 6,50 | 10 % | Cronometraje |
| E2 | Subconjunto de puerta | 6,20 | 6,20 | 18 % | Operador experto |
| E3 | Instalación de puerta y arnés | 8,00 | 8,00 | 15 % | Cronometraje |
| E4 | Cableado y montaje eléctrico | 7,00 | 8,60 | 12 % | Pro: segunda cámara y módulo celular |
| E5 | Inspección y prueba eléctrica | 6,50 | 7,50 | 5 % | Inspección 1,5 min/u + prueba de 15 min (Pro: 18 min) por lote de 3 unidades |
| E6 | Empaque y paletizado | 5,67 | 5,67 | 8 % | 5 min/u + 4 min por paleta de 6 unidades |

CV: coeficiente de variación (desviación típica / media), para quienes deseen simular variabilidad. Cambio de variante: 20 min de parada de toda la línea; lote actual: 100 unidades por variante. Inventario medio en proceso observado: 46 unidades por línea.


## Anexo 4. Propuesta de ingeniería: línea de ocho operadores

|   | Puesto Operación | Estándar (min/u) | Pro (min/u) |
| --- | --- | --- | --- |
| L1 | Ensamblaje de gabinete | 5,00 | 5,00 |
| L2 | Soldadura de gabinete | 5,20 | 5,20 |
| L3 | Ensamblaje de puerta | 5,80 | 5,80 |
| L4 | Cableado | 4,10 | 4,10 |
| L5 | Instalación de puerta | 4,30 | 4,30 |
| L6 | Montaje eléctrico e inspección | 4,80 | 6,40 |
| L7 | Pruebas | 5,00 | 6,00 |
| L8 | Embalaje | 5,67 | 5,67 |
|   | Tiempo de ciclo medio (según el informe) | 5,0 | — |

Inversión: US\$ 9.000 por línea. Plazo de preparación: 3 semanas. Personal: 7 operadores y 1 técnico de pruebas por línea.

## Anexo 5. Jornada, turnos y calendario

| Parámetro | Esquema de 1 o 2 turnos | Esquema de 3 turnos |
| --- | --- | --- |
| Horas programadas por turno | 8,5 | 8,0 |
| Almuerzo no pagado | 30 min | 30 min |
| Descansos pagados | 2 × 15 min | 2 × 15 min |
| Horas productivas por turno | 7,5 | 7,0 |
| Horas pagadas por turno | 8,0 | 7,5 |
| Rendimiento respecto del primer turno | 2.º turno: 92 % | 2.º turno: 92 % · 3.er turno: 88 % |
| Prima salarial | 2.º turno: +8 % | 2.º turno: +8 % · 3.er turno: +15 % |
| Coste fijo adicional por turno (energía, seguridad) US$ 600 por semana |   | US$ 600 por semana y turno |

Sábados: 6,5 h productivas (7 h pagadas) con recargo del 50 %; máximo 3 sábados al mes y solo en el primer turno. Costes fijos de planta (alquiler de la nave actual, mantenimiento, energía base): US\$ 3.200 por semana.

## Anexo 6. Opciones de capacidad

| Opción | Inversión (US$) | Plazo | Efecto en el proceso | Personal | Restricciones |
| --- | --- | --- | --- | --- | --- |
| O1. Ocho operadores por línea | 9.000 por línea 3 semanas |   | Tiempos del Anexo 4 | +2 operadores por línea — |   |
| O2. Tercera línea | 48.000 | 8 semanas | Igual a las actuales (Anexo 3) | 6 en línea; el manipulador actual atiende hasta 3 líneas | 120 m² de espacio |
| O3. Turnos 2.º y 3.º | 0 | 2 semanas (contratación) | Rendimiento y primas del Anexo 5 | Plantilla de línea + líder + técnico de retrabajo por turno | Curva de aprendizaje |
| O4. Células de trabajo | 15.000 por célula | 5 semanas (hasta 4 células por pedido) | Un trabajador ensambla la unidad completa; tiempo = contenido de trabajo × (1 + penalización por polivalencia) | 3 trabajadores por célula y turno | 40 m² por célula; cambio de variante 5 min |
| O5. Dispositivo para la puerta | 22.000 por línea | 10 semanas | Línea de 6: E2 5,6 y E3 6,0 min. Línea de 8: L3 5,2 y L5 3,3 min | Sin cambios | Solo líneas |
| O6. Subcontratar la puerta | 0 | 4 semanas | Desaparece E2; E3 baja a 7,2 min; la línea opera con 5 personas | –1 operador por línea | +US$ 4,80 por unidad; máximo 1.200 u/semana |
| O7. Sábados con horas extra | 0 | Inmediato | Capacidad del primer turno durante 6,5 h | Plantilla existente | Máximo 3 sábados al mes |

Penalización por polivalencia en células: estimación central 8 %, rango 0–20 %, según la experiencia de otra planta del sector. Las opciones pueden combinarse. Valor residual de los equipos al final de las 52 semanas: 80 % de la inversión (vida útil de 5 años).


## Anexo 7. Calidad y retrabajo

| Parámetro | Estándar | Pro | Observaciones |
| --- | --- | --- | --- |
| Unidades que fallan la prueba final | 4 % | 6 % | Datos de la producción piloto |
| Unidades recuperables por retrabajo | 80 % | 80 % | El resto se desecha (se pierde el material) |
| Tiempo de retrabajo por unidad | 15 min | 15 min | Técnico de retrabajo, fuera de línea |
| Efecto de las células en las fallas | –1 punto | –1 punto | Supuesto: el trabajador responde de la unidad completa |

## Anexo 8. Inventario, nivel de servicio y faltantes

| Parámetro | Valor |
| --- | --- |
| Inventario inicial de producto terminado (semana 1) | 300 unidades (70 % Estándar) |
| Coste de mantener inventario | 24 % anual sobre el coste de materiales |
| Demanda no atendida que espera (pedido pendiente) | 50 %, hasta 2 semanas; después se pierde |
| Penalización por pedido pendiente | US$ 3 por unidad y semana |
| Demanda no atendida que se pierde | 50 % de inmediato |
| Coste de una venta perdida | Margen de contribución + US$ 10 de pérdida de imagen |
| Inventario máximo de producto terminado | 1.500 unidades (espacio de almacén) |

## Anexo 9. Parámetros financieros

| Parámetro | Valor |
| --- | --- |
| Horizonte de evaluación | 52 semanas (5 de octubre de 2026 a 1 de octubre de 2027) |
| Tasa de descuento | 12 % anual (equivalente semanal: (1,12)^(1/52) – 1) |
| Pago de las inversiones | En la semana en que se ordenan |
| Valor residual de equipos y células | 80 % de la inversión al final del horizonte |
| Límite de inversión sin aprobación del consejo | US$ 120.000 en el año fiscal |
| Probabilidades de los escenarios | Base 50 % · Optimista 25 % · Llenado de canal 25 % |

## Anexo 10. Espacio y recursos humanos

| Parámetro | Valor |
| --- | --- |
| Superficie actual de la planta | 420 m², de los que 240 m² ocupan las dos líneas |
| Superficie libre | 180 m² |
| Espacio por línea / por célula | 120 m² / 40 m² |
| Ampliación disponible | 200 m² desde la semana 11, a US$ 6 por m² y semana, contrato mínimo de 26 semanas |
| Incorporaciones máximas por semana | 12 personas |
| Curva de aprendizaje de personal nuevo | Semana 1: 70 % · semana 2: 80 % · semana 3: 90 % · semana 4: 95 % · semana 5 en adelante: 100 % |
| Rotación de personal de planta | 2 % mensual (opcional en el modelo) |

## Anexo 11. Pronóstico de demanda semanal (unidades)

| Sem. | Inicio | Base | Optim. | Canal | Sem. | Inicio | Base | Optim. | Canal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 05/10 | 700 | 700 | 700 | 27 | 05/04 | 1.060 | 1.270 | 680 |
| 2 | 12/10 | 800 | 800 | 800 | 28 | 12/04 | 1.070 | 1.280 | 680 |
| 3 | 19/10 | 950 | 950 | 950 | 29 | 19/04 | 1.080 | 1.300 | 680 |
| 4 | 26/10 | 1.050 | 1.050 | 1.050 | 30 | 26/04 | 1.090 | 1.310 | 680 |


| Sem. | Inicio | Base | Optim. | Canal | Sem. | Inicio | Base | Optim. | Canal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 02/11 | 1.150 | 1.380 | 1.150 | 31 | 03/05 | 1.100 | 1.320 | 690 |
| 6 | 09/11 | 1.300 | 1.560 | 1.300 | 32 | 10/05 | 1.110 | 1.330 | 690 |
| 7 | 16/11 | 1.550 | 1.860 | 1.550 | 33 | 17/05 | 1.280 | 1.540 | 760 |
| 8 | 23/11 | 1.900 | 2.280 | 1.900 | 34 | 24/05 | 1.290 | 1.550 | 760 |
| 9 | 30/11 | 1.750 | 2.100 | 1.750 | 35 | 31/05 | 1.130 | 1.360 | 690 |
| 10 | 07/12 | 1.700 | 2.040 | 1.700 | 36 | 07/06 | 1.140 | 1.370 | 700 |
| 11 | 14/12 | 1.650 | 1.980 | 1.300 | 37 | 14/06 | 1.150 | 1.380 | 700 |
| 12 | 21/12 | 1.300 | 1.560 | 1.000 | 38 | 21/06 | 1.160 | 1.390 | 700 |
| 13 | 28/12 | 900 | 1.080 | 650 | 39 | 28/06 | 1.170 | 1.400 | 700 |
| 14 | 04/01 | 960 | 1.150 | 650 | 40 | 05/07 | 1.180 | 1.420 | 700 |
| 15 | 11/01 | 970 | 1.160 | 650 | 41 | 12/07 | 1.190 | 1.430 | 710 |
| 16 | 18/01 | 970 | 1.160 | 660 | 42 | 19/07 | 1.200 | 1.440 | 710 |
| 17 | 25/01 | 980 | 1.180 | 660 | 43 | 26/07 | 1.210 | 1.450 | 710 |
| 18 | 01/02 | 990 | 1.190 | 660 | 44 | 02/08 | 1.220 | 1.460 | 710 |
| 19 | 08/02 | 1.000 | 1.200 | 660 | 45 | 09/08 | 1.230 | 1.480 | 720 |
| 20 | 15/02 | 1.000 | 1.200 | 660 | 46 | 16/08 | 1.240 | 1.490 | 720 |
| 21 | 22/02 | 1.010 | 1.210 | 670 | 47 | 23/08 | 1.250 | 1.500 | 720 |
| 22 | 01/03 | 1.020 | 1.220 | 670 | 48 | 30/08 | 1.260 | 1.510 | 720 |
| 23 | 08/03 | 1.030 | 1.240 | 670 | 49 | 06/09 | 1.270 | 1.520 | 720 |
| 24 | 15/03 | 1.040 | 1.250 | 670 | 50 | 13/09 | 1.280 | 1.540 | 730 |
| 25 | 22/03 | 1.050 | 1.260 | 670 | 51 | 20/09 | 1.290 | 1.550 | 730 |
| 26 | 29/03 | 1.050 | 1.260 | 680 | 52 | 27/09 | 1.300 | 1.560 | 730 |

*Semana 1: 5 de octubre de 2026; las fechas indican el lunes de cada semana (dd/mm). Semana 8: Black Friday. Semanas 33–34: Día de las Madres. Totales anuales: base 60.720; optimista 72.170; llenado de canal 42.870 unidades. La mezcla Pro es del 30 % en las semanas 1–26 y del 35 % en las semanas 27–52 en los tres escenarios.*


## Parte III. Guía para construir el tablero simulador

## Objetivos de aprendizaje

- Calcular e interpretar los parámetros fundamentales de un sistema de producción: tiempo de ciclo, cuello de botella, capacidad, takt time, eficiencia del balance, utilización, inventario en proceso, tiempo de flujo y coste unitario.

- Reconocer cómo el cuello de botella cambia con la mezcla de productos, los lotes y las mejoras parciales.

- Comparar alternativas de capacidad con criterios económicos (margen, coste, inversión, valor actual) y operativos (nivel de servicio, flexibilidad, riesgo).

- Contrastar una decisión estática (comprometer toda la capacidad desde el inicio) con una decisión secuencial (por fases, con puntos de decisión) bajo incertidumbre de demanda.

- Construir un modelo de simulación reproducible con herramientas de IA o de BI y validarlo contra valores de control.

## Preguntas del caso

- ¿Cuál es la capacidad real de la planta hoy? ¿Dónde está el cuello de botella para cada variante y para la mezcla?

- ¿Es correcta la conclusión del informe de ingeniería sobre la línea de ocho operadores?

- ¿Por qué el dispositivo para la puerta aporta menos capacidad de la que parece?

- ¿Qué combinación de opciones cubre la temporada alta con la inversión permitida?

- ¿Qué estrategia maximiza el valor esperado en los tres escenarios? ¿Cuál limita mejor la pérdida en el peor escenario?

- ¿Qué recomendaría a Mariela Santos para el viernes, y qué puntos de decisión fijaría para los meses siguientes?

## Requisitos mínimos del tablero

## Palancas (datos de entrada que el usuario puede modificar):

| Palanca | Rango sugerido |
| --- | --- |
| Escenario de demanda y probabilidades | Base / optimista / llenado de canal; probabilidades editables |
| Número de líneas y operadores por línea | 2–3 líneas; 6, 8 o 5 (si se subcontrata la puerta) |
| Turnos y semana de inicio de cada turno | 1–3 turnos; semana 1–52 |
| Sábados con horas extra | 0–3 al mes |
| Número de células, trabajadores y semana de entrada | 0–10 células |
| Dispositivo para la puerta y subcontratación de la puerta | Sí / no, con semana de entrada en operación |
| Tamaño de lote y tiempo de cambio de variante | 25–400 unidades; 5–40 min |
| Mezcla Pro | 20–50 % |
| Penalización por polivalencia, fallas y rendimiento de turnos | Según los rangos de los anexos |

## Indicadores (resultados que el tablero debe calcular):

| Grupo | Indicadores |
| --- | --- |
| Capacidad | Tiempo de ciclo por variante, cuello de botella, capacidad semanal bruta y de unidades buenas, takt time, utilización por estación |
| Flujo | Eficiencia del balance, inventario en proceso, tiempo de flujo (Ley de Little), inventario de producto terminado |
| Servicio | Demanda atendida, pedidos pendientes, ventas perdidas, nivel de servicio (%) por semana |


| Grupo | Indicadores |
| --- | --- |
| Economía | Coste de mano de obra por unidad, coste total semanal, margen de contribución, inversión acumulada, valor actual a 52 semanas |
| Riesgo | Resultado por escenario, valor esperado, peor caso, sensibilidad a las variables clave |

Vistas mínimas: (1) panel de la línea con utilización por estación y cuello de botella; (2) capacidad frente a demanda semana a semana; (3) comparación de al menos cuatro estrategias en los tres escenarios; (4) sensibilidad (por ejemplo, un gráfico de tornado) y umbrales de decisión.

## Fórmulas de referencia

| Concepto | Fórmula |
| --- | --- |
| Tiempo productivo semanal por línea y turno | T = horas productivas × 60 × días × rendimiento del turno |
| Contenido de trabajo | Σ tiempos de todas las estaciones (por variante) |
| Tiempo de ciclo de una variante | Máximo de los tiempos de estación de esa variante |
| Ciclo medio con mezcla | c̄ = (1 – %Pro) × ciclo Estándar + %Pro × ciclo Pro |
| Capacidad de una línea con cambios de variante | Cap = T / (c̄ + s / Q), con s = minutos por cambio y Q = lote |
| Unidades buenas | Cap × (1 – % fallas × % desechadas) |
| Takt time | Tiempo disponible / demanda |
| Eficiencia del balance | Contenido / (n.º de estaciones × ciclo) |
| Ley de Little | Inventario en proceso = tasa de producción × tiempo de flujo |
| Capacidad de un trabajador de célula | T / [contenido medio × (1 + penalización)] |
| Valor esperado | VE = Σ (probabilidad del escenario × resultado del escenario) |
| Valor actual | VA = Σ flujo semanal / (1 + i semanal)^semana + valor residual descontado – inversiones |

## Modelo de datos sugerido

| Tabla | Campos principales | Fuente |
| --- | --- | --- |
| Parametros | parametro, valor, unidad, minimo, maximo | Anexos 1, 2, 5, 7–10 |
| Estaciones | configuracion, estacion, operacion, t_estandar, t_pro, cv | Anexos 3, 4 y 6 |
| Puestos | puesto, salario_hora, cargas_pct, por_linea, por_turno | Anexo 2 |
| Opciones | opcion, inversion, plazo_semanas, efecto, personal, restriccion | Anexo 6 |
| Demanda | semana, fecha_inicio, escenario, unidades, pct_pro | Anexo 11 |
| Escenarios | escenario, probabilidad | Anexo 9 |
| Estrategias | estrategia, opcion, semana_activacion, cantidad | Diseño del estudiante |
| Resultados | estrategia, escenario, semana, capacidad, producido, atendido, perdido, inventario, costes, margen | Cálculo del modelo |

La tabla Demanda en formato largo (una fila por semana y escenario) facilita el uso de filtros y segmentadores en herramientas de BI.

## Valores de control del escenario actual

Antes de simular estrategias, el modelo debe reproducir estos valores para la configuración actual (2 líneas de 6 operadores, 1 turno, lote de 100 unidades, 30 % Pro):

| Indicador | Valor de control |
| --- | --- |
| Contenido de trabajo Estándar / Pro | 39,87 / 42,47 min |
| Tiempo de ciclo Estándar / Pro | 8,00 min (E3) / 8,60 min (E4) |
| Eficiencia del balance Estándar / Pro | 83,1 % / 82,3 % |
| Ciclo medio con la mezcla | 8,18 min |


| Indicador | Valor de control |
| --- | --- |
| Capacidad bruta por línea / planta | 268,5 / 537,0 unidades por semana |
| Unidades buenas por semana | 532,1 |
| Unidades a retrabajar por semana | 19,8 |
| Tiempo de flujo por línea (Ley de Little) | 6,42 horas |
| Takt time por línea en la semana 8 (escenario base) | 2,37 min |
| Coste semanal de mano de obra, con cargas y supervisor | US$ 5.990 |
| Coste de mano de obra por unidad buena | US$ 11,26 |
| Margen de contribución medio antes de mano de obra (30 % Pro) | US$ 78,20 por unidad |
| Capacidad bruta con un segundo turno (sin curva de aprendizaje) | 1.031,0 unidades por semana |

## Entregables

- Tablero simulador funcional, con las palancas y vistas mínimas, y el archivo fuente o el enlace.

- Nota técnica de una página con los supuestos adicionales del modelo y la validación contra los valores de control.

- Recomendación de dos máximos páginas para el consejo de dirección o la alta gerencia, el cual pudiera disponer de: estrategia elegida, resultado por escenario, valor esperado, peor caso, inversión, puntos de decisión y riesgos.

## Criterios de evaluación

| Criterio | Peso | Qué se valora |
| --- | --- | --- |
| Exactitud del modelo | 25 % | Reproduce los valores de control; fórmulas trazables |
| Profundidad del análisis | 25 % | Cuello de botella por variante, mezcla, lotes, curva de aprendizaje, calidad |
| Calidad de la decisión | 25 % | Comparación por escenarios, valor esperado, peor caso y visión secuencial |
| Diseño del tablero | 15 % | Claridad, interactividad y capacidad de responder las preguntas del caso |
| Comunicación | 10 % | Recomendación clara, breve y defendible ante el consejo |
