# PROYECTO
Sistema versionado de prescripción de entrenamiento para escaladores
Excel + VBA + motor de reglas + base de evidencia

# OBJETIVO

Construye desde cero un sistema funcional en Excel habilitado para macros (.xlsm)
capaz de generar, registrar, adaptar y auditar programas de entrenamiento para escaladores.

NO construyas una simple plantilla.

El resultado debe comportarse como una pequeña aplicación de escritorio dentro de Excel.

El usuario proporciona datos.

El sistema evalúa esos datos.

Un motor de reglas genera la prescripción.

El conocimiento deportivo vive principalmente en Rulesets versionados.

El código ejecuta las reglas.

Las tablas contienen el conocimiento.

Cada decisión importante debe poder rastrearse hasta:

- una regla;
- uno o varios parámetros;
- una versión del Ruleset;
- y, cuando corresponda, evidencia bibliográfica.


# PRINCIPIO RECTOR

EL CÓDIGO EJECUTA.

LAS TABLAS DECIDEN.

LOS RULESETS VERSIONAN EL CONOCIMIENTO.

LAS FUENTES JUSTIFICAN LAS REGLAS.

EL HISTORIAL CONSERVA QUÉ VERSIÓN TOMÓ CADA DECISIÓN.


# ROL

Actúa como:

- arquitecto de software;
- desarrollador senior de Excel/VBA;
- desarrollador Python cuando sea útil para construir o probar el archivo;
- especialista en motores de reglas;
- diseñador de modelos de datos;
- especialista en testing;
- investigador técnico;
- especialista en programación del entrenamiento;
- preparador físico especializado en escalada.

No supongas que tus conocimientos internos son suficientes para establecer
prescripciones deportivas.

Cuando una decisión deportiva requiera evidencia, INVESTIGA antes de convertirla
en una regla de producción.


======================================================================
1. ARQUITECTURA GENERAL
======================================================================

Separar estrictamente:

1. DATOS DEL USUARIO
2. BASE DE EJERCICIOS
3. MOTOR DE REGLAS
4. RULESETS
5. PARÁMETROS
6. EVIDENCIA
7. PLANES GENERADOS
8. HISTORIAL
9. FEEDBACK
10. TRAZABILIDAD
11. INTERFAZ
12. REPORTES


Conceptualmente:

USUARIO
+
CONTEXTO ACTUAL
+
RULESET
+
PARÁMETROS
+
BASE DE EJERCICIOS
=
PRESCRIPCIÓN


La prescripción produce:

- sesiones;
- ejercicios;
- series;
- repeticiones;
- duración;
- intensidad;
- carga;
- descanso;
- frecuencia;
- progresión;
- advertencias;
- reevaluaciones.


======================================================================
2. REQUERIMIENTOS FUNCIONALES
======================================================================


----------------------------
RF-001 – GESTIÓN DE USUARIO
----------------------------

El sistema debe permitir crear un perfil de escalador.

Campos mínimos:

- UserID
- nombre o alias
- edad
- sexo cuando tenga relevancia para un cálculo
- peso corporal
- estatura
- envergadura
- años escalando
- fecha de creación
- estado del usuario


----------------------------
RF-002 – NIVEL DE ESCALADA
----------------------------

Debe poder registrarse:

- principiante
- intermedio
- avanzado
- élite

y además grados reales.

Boulder:

- grado habitual
- máximo trabajado
- máximo encadenado

Deportiva:

- grado habitual
- máximo trabajado
- máximo encadenado

Las escalas de graduación deben almacenarse en tablas configurables.

No codificar una única escala dentro del VBA.


----------------------------
RF-003 – MODALIDAD
----------------------------

Permitir:

- Boulder
- Deportiva
- Mixto

Debe existir modalidad principal.


----------------------------
RF-004 – OBJETIVOS
----------------------------

Permitir uno o varios objetivos:

- fuerza máxima
- fuerza de dedos
- potencia
- potencia de contacto
- resistencia
- resistencia de fuerza
- power endurance
- técnica
- mejorar grado de Boulder
- mejorar grado de deportiva
- proyecto específico
- acondicionamiento general
- retorno progresivo

Debe existir un objetivo principal.

Permitir ponderación o prioridad entre objetivos.


----------------------------
RF-005 – DISPONIBILIDAD
----------------------------

Registrar:

- número de días disponibles
- días concretos
- duración máxima de sesión
- disponibilidad de muro
- disponibilidad de gimnasio
- entrenamiento en casa
- descanso mínimo
- restricciones horarias

El planificador debe respetar estas restricciones.


----------------------------
RF-006 – EQUIPO
----------------------------

Registrar disponibilidad de:

- muro
- spray wall
- MoonBoard
- Kilter Board
- Tension Board
- campus board
- hangboard
- barra
- anillas
- TRX
- poleas
- discos
- mancuernas
- barra olímpica
- bandas
- gimnasio
- otro equipo configurable

Un ejercicio que requiera equipo no disponible debe ser excluido automáticamente.


----------------------------
RF-007 – MOLESTIAS Y LIMITACIONES
----------------------------

Registrar por región:

- dedos
- muñeca
- codo
- hombro
- espalda
- rodilla
- tobillo
- otra

Estados:

- ninguna
- leve
- limitación
- lesión/rehabilitación

El sistema NO debe diagnosticar.

Debe poder:

- excluir estímulos;
- excluir ejercicios;
- reducir carga;
- bloquear progresión;
- mostrar advertencias;
- sugerir valoración profesional.


----------------------------
RF-008 – PRIORIDAD DE SEGURIDAD
----------------------------

Las reglas de seguridad deben tener prioridad sobre:

- objetivo;
- rendimiento;
- preferencias;
- progresión.

Una regla de rendimiento jamás debe poder reactivar algo bloqueado por seguridad.


----------------------------
RF-009 – TESTS
----------------------------

Debe existir una base de tests.

Los tests no estarán fijos dentro del código.

Cada test debe poder declarar:

- TestID
- nombre
- objetivo
- nivel requerido
- equipo
- unidad
- protocolo
- criterios de elegibilidad
- riesgos/restricciones
- fuente bibliográfica


----------------------------
RF-010 – SELECCIÓN AUTOMÁTICA DE TESTS
----------------------------

El sistema debe poder determinar qué evaluaciones corresponden según:

- objetivo;
- nivel;
- experiencia;
- equipo;
- limitaciones;
- historial.


----------------------------
RF-011 – HISTORIAL DE TESTS
----------------------------

Nunca sobrescribir resultados anteriores.

Guardar:

- UserID
- TestID
- fecha
- resultado
- unidad
- protocolo utilizado
- Ruleset
- observaciones


----------------------------
RF-012 – BASE DE EJERCICIOS
----------------------------

Crear una tabla estructurada de ejercicios.

Campos mínimos:

ExerciseID
Nombre
Categoría
Subcategoría
Objetivo
NivelMin
NivelMax
Modalidad
Equipo
ZonaCorporal
StimulusType
PrescriptionUnit
MinSets
MaxSets
MinReps
MaxReps
Duration
IntensityType
RPE
RIR
Rest
Frequency
ProgressionRule
RegressionRule
Contraindications
EvidenceID
Tags
Notes


----------------------------
RF-013 – CATEGORÍAS
----------------------------

Como mínimo:

- escalada específica
- técnica
- fuerza de dedos
- tracción
- antagonistas
- core
- potencia
- power endurance
- resistencia
- movilidad
- prehabilitación
- recuperación


----------------------------
RF-014 – MOTOR DE REGLAS
----------------------------

Crear un Rule Engine genérico.

NO implementar cada decisión deportiva mediante un nuevo If en VBA.

El motor debe:

1. cargar contexto;
2. cargar Ruleset;
3. evaluar condiciones;
4. ejecutar acciones;
5. resolver conflictos;
6. producir un resultado determinista.


----------------------------
RF-015 – REGLAS DECLARATIVAS
----------------------------

Las reglas deben almacenarse como datos.

No guardar código VBA ejecutable dentro de celdas.

Una regla debe describir:

CUÁNDO APLICA

y

QUÉ ACCIÓN EJECUTAR.


----------------------------
RF-016 – CONDICIONES
----------------------------

Soportar como mínimo:

EQ
NEQ
GT
GTE
LT
LTE
BETWEEN
IN
NOT_IN
EXISTS
NOT_EXISTS


----------------------------
RF-017 – CONDICIONES COMPUESTAS
----------------------------

Soportar:

AND

OR

Ejemplo:

Objetivo = FingerStrength

AND

ExperienceYears >= X

AND

HangboardAvailable = TRUE

AND

FingerPain = 0


----------------------------
RF-018 – ACCIONES
----------------------------

Soportar inicialmente acciones genéricas como:

INCLUDE_EXERCISE
EXCLUDE_EXERCISE

INCLUDE_CATEGORY
EXCLUDE_CATEGORY

SET_SETS
SET_REPS
SET_DURATION
SET_INTENSITY
SET_REST

SET_MIN
SET_MAX

MULTIPLY_VOLUME

SET_FREQUENCY

SET_LOAD

SET_LOAD_PERCENT

SET_RPE
SET_RIR

ALLOW_PROGRESSION
BLOCK_PROGRESSION

TRIGGER_DELOAD
TRIGGER_REEVALUATION

SHOW_WARNING


----------------------------
RF-019 – CATÁLOGO DE ACCIONES
----------------------------

Las acciones reconocidas por el motor deben tener catálogo propio.

No depender de cadenas arbitrarias repartidas por el código.


----------------------------
RF-020 – TIPOS DE REGLA
----------------------------

Soportar:

SAFETY
ELIGIBILITY
EXCLUSION
TEST_SELECTION
EXERCISE_SELECTION
PRESCRIPTION
VOLUME
INTENSITY
REST
FREQUENCY
SCHEDULING
PROGRESSION
REGRESSION
DELOAD
REEVALUATION
WARNING


----------------------------
RF-021 – PRIORIDAD
----------------------------

Cada regla debe tener Priority.

La resolución debe ser determinista.

No depender del número de fila.


----------------------------
RF-022 – RESOLUCIÓN DE CONFLICTOS
----------------------------

Definir formalmente precedencia.

Como mínimo:

SAFETY
>
EXCLUSION
>
ELIGIBILITY
>
PRESCRIPTION
>
PREFERENCE

Registrar conflictos detectados.


----------------------------
RF-023 – PARÁMETROS
----------------------------

Los números reutilizables deben almacenarse aparte.

Ejemplo:

ParameterID
Category
Name
Value
Unit
RulesetVersion

Los parámetros pueden representar:

- segundos
- porcentajes
- ratios
- repeticiones
- series
- límites
- RPE
- RIR
- frecuencias
- multiplicadores
- tolerancias


----------------------------
RF-024 – REFERENCIAS A PARÁMETROS
----------------------------

Una regla puede referenciar:

ParameterID

en lugar de duplicar el mismo valor muchas veces.


----------------------------
RF-025 – RULESETS
----------------------------

El conocimiento debe estar versionado.

Ejemplos:

1.0.0
1.1.0
1.2.0
2.0.0


----------------------------
RF-026 – INMUTABILIDAD
----------------------------

Una versión utilizada en producción no debe modificarse destructivamente.

Si cambia una regla:

crear nueva versión.


----------------------------
RF-027 – VERSIONADO SEMÁNTICO
----------------------------

Usar:

MAJOR.MINOR.PATCH

y documentar el criterio.


----------------------------
RF-028 – ESTADOS DEL RULESET
----------------------------

Soportar:

DRAFT
RESEARCH
TESTING
ACTIVE
DEPRECATED
ARCHIVED


----------------------------
RF-029 – RULESET ACTIVO
----------------------------

Solo un Ruleset válido y ACTIVE debe utilizarse por defecto para nuevos ciclos.


----------------------------
RF-030 – CONSERVACIÓN DE VERSIÓN
----------------------------

Cada plan generado debe guardar:

RulePackageVersionUsed


----------------------------
RF-031 – GENERACIÓN DEL PLAN
----------------------------

Crear:

GenerarPlan()

Debe producir una estructura global del ciclo.


----------------------------
RF-032 – GENERACIÓN SEMANAL
----------------------------

Crear:

GenerarSemana()

Debe generar como mínimo:

Fecha
Día
Sesión
Objetivo
Ejercicio
Series
Reps
Duración
Intensidad
Carga
Descanso
RPEObjetivo
Notas
Ruleset
RuleIDs


----------------------------
RF-033 – RESTRICCIÓN TEMPORAL
----------------------------

Ninguna sesión generada debe exceder sustancialmente el tiempo disponible.

Si no cabe:

el motor debe priorizar o reducir según reglas.


----------------------------
RF-034 – DISTRIBUCIÓN DE CARGAS
----------------------------

El planificador debe evaluar incompatibilidades entre días.

Las reglas establecerán:

- recuperación mínima;
- estímulos incompatibles;
- frecuencia máxima;
- frecuencia mínima.


----------------------------
RF-035 – REGISTRO DE SESIÓN
----------------------------

El usuario debe registrar:

- completada
- parcial
- omitida
- porcentaje completado
- RPE
- fatiga
- calidad
- dolor
- series
- repeticiones
- cargas
- tiempos
- comentarios


----------------------------
RF-036 – ADAPTACIÓN
----------------------------

La siguiente prescripción debe poder utilizar el feedback anterior.


----------------------------
RF-037 – PROGRESIÓN
----------------------------

Soportar decisiones:

PROGRESS
MAINTAIN
REGRESS
DELOAD
STOP
REEVALUATE

Los criterios concretos deben vivir en reglas.


----------------------------
RF-038 – NUEVO CICLO
----------------------------

Crear:

CrearNuevoCiclo()

Debe iniciar un nuevo ciclo sin destruir el anterior.


----------------------------
RF-039 – REEVALUACIÓN
----------------------------

Crear:

EjecutarReevaluacion()

Las reglas determinarán:

- cuándo;
- qué pruebas;
- qué variables actualizar.


----------------------------
RF-040 – TRAZABILIDAD
----------------------------

Toda decisión de prescripción relevante debe poder registrar:

DecisionID
UserID
PlanID
RulePackageVersion
RuleID
InputValues
Action
PreviousValue
NewValue
Timestamp


----------------------------
RF-041 – EXPLICABILIDAD
----------------------------

El usuario técnico debe poder preguntar:

¿Por qué se seleccionó este ejercicio?

¿Por qué estas series?

¿Por qué este descanso?

¿Por qué se bloqueó una progresión?

¿Por qué apareció esta advertencia?


----------------------------
RF-042 – DEBUG
----------------------------

Crear modo Debug capaz de mostrar:

- reglas evaluadas;
- reglas cumplidas;
- reglas fallidas;
- acciones generadas;
- conflictos;
- reglas ganadoras;
- parámetros utilizados;
- resultado final.


----------------------------
RF-043 – IMPORTACIÓN DE RULESETS
----------------------------

Permitir importar una nueva versión de reglas sin modificar el VBA.


----------------------------
RF-044 – EXPORTACIÓN DE RULESETS
----------------------------

Permitir exportar Rulesets.


----------------------------
RF-045 – VALIDACIÓN DEL RULESET
----------------------------

Crear:

ValidateRulePackage()

Debe comprobar al menos:

- RuleID duplicados
- operador inexistente
- ActionType inexistente
- ParameterID inexistente
- ExerciseID inexistente
- SourceID inexistente
- tipos incompatibles
- rangos inválidos
- prioridades inválidas
- referencias rotas
- versiones inválidas


----------------------------
RF-046 – ACTIVACIÓN
----------------------------

Un Ruleset que no pase la validación no puede pasar a ACTIVE.


----------------------------
RF-047 – DASHBOARD
----------------------------

Mostrar como mínimo:

- semana actual
- cumplimiento
- sesiones
- carga
- progresión
- tests
- grados
- indicadores relevantes
- fatiga reciente
- Ruleset activo


----------------------------
RF-048 – EXPORTACIÓN
----------------------------

Crear:

ExportarPlanPDF()


----------------------------
RF-049 – PROTECCIÓN DE HISTORIAL
----------------------------

Generar planes nuevos jamás debe borrar resultados anteriores.


----------------------------
RF-050 – INTERFAZ
----------------------------

Pantalla principal con:

NUEVO USUARIO
MI PERFIL
EVALUACIONES
GENERAR PLAN
ENTRENAMIENTO DE HOY
REGISTRAR ENTRENAMIENTO
PROGRESO
HISTORIAL
CONFIGURACIÓN


======================================================================
3. INVESTIGACIÓN CIENTÍFICA OBLIGATORIA
======================================================================

Esta sección es OBLIGATORIA.

No construyas las reglas deportivas finales únicamente con conocimiento interno.

Debes INVESTIGAR la evidencia disponible.


----------------------------
INV-001 – INVESTIGAR ANTES DE PRESCRIBIR
----------------------------

Antes de convertir un valor, protocolo, umbral o criterio deportivo en una
regla de producción:

buscar fuentes relevantes.


----------------------------
INV-002 – JERARQUÍA DE FUENTES
----------------------------

Priorizar, aproximadamente:

1. revisiones sistemáticas;
2. metaanálisis;
3. consensos o position statements de organizaciones reconocidas;
4. ensayos controlados;
5. estudios longitudinales;
6. estudios observacionales;
7. investigación específica de escalada;
8. libros académicos;
9. consenso profesional;
10. heurística de entrenador.

No tratar todas las fuentes como equivalentes.


----------------------------
INV-003 – INVESTIGACIÓN ESPECÍFICA DE ESCALADA
----------------------------

Buscar especialmente literatura relacionada con:

- climbing;
- sport climbing;
- bouldering;
- finger strength;
- fingerboard;
- hangboard;
- grip strength;
- forearm endurance;
- climbing performance;
- power endurance;
- campus board;
- climbing injuries;
- load management;
- strength training for climbers;
- physiological demands of climbing.


----------------------------
INV-004 – EVIDENCIA GENERAL
----------------------------

Cuando no exista evidencia específica suficiente en escalada:

puede utilizarse evidencia general de:

- entrenamiento de fuerza;
- potencia;
- resistencia;
- periodización;
- recuperación;
- RPE;
- RIR;
- gestión de carga;

pero debe etiquetarse como:

EVIDENCIA INDIRECTA.


----------------------------
INV-005 – NO INVENTAR FUENTES
----------------------------

PROHIBIDO:

- inventar DOI;
- inventar PMID;
- inventar autores;
- inventar títulos;
- afirmar que un estudio dice algo que no dice.


----------------------------
INV-006 – VERIFICACIÓN
----------------------------

Antes de guardar una referencia:

verificar que realmente existe.

Cuando sea posible registrar:

- DOI;
- PMID;
- URL editorial;
- URL PubMed;
- identificador equivalente.


----------------------------
INV-007 – FECHA DE CONSULTA
----------------------------

Registrar:

AccessedDate

para fuentes web.


----------------------------
INV-008 – BASE DE EVIDENCIA
----------------------------

Crear:

tblEvidence

con al menos:

SourceID
SourceType
Authors
Title
Year
Journal
Volume
Issue
Pages
DOI
PMID
URL
AccessedDate
EvidenceLevel
ClimbingSpecific
Population
MainFinding
Limitations
Notes


----------------------------
INV-009 – MAPEO REGLA → EVIDENCIA
----------------------------

No limitar Rule a un único SourceID.

Crear una tabla de relación:

tblRuleEvidence

con:

RuleID
RulesetVersion
SourceID
RelationType
EvidenceStrength
Notes


RelationType puede incluir:

DIRECT_SUPPORT
INDIRECT_SUPPORT
BACKGROUND
CONTRADICTS
SAFETY
RATIONALE


----------------------------
INV-010 – JUSTIFICACIÓN
----------------------------

Cada regla de producción debe tener:

Rationale

explicando:

- por qué existe;
- qué intenta conseguir;
- de dónde viene;
- qué grado de confianza tiene.


----------------------------
INV-011 – CLASIFICACIÓN
----------------------------

Cada regla deberá clasificarse como una de:

DIRECT_EVIDENCE
INDIRECT_EVIDENCE
CONSENSUS
EXPERT_HEURISTIC
DESIGN_DECISION
SAFETY_PRECAUTION


----------------------------
INV-012 – PARÁMETROS TAMBIÉN SE REFERENCIAN
----------------------------

No solo las reglas.

Los parámetros deportivos importantes también deben poder vincularse a evidencia.

Ejemplo:

descanso
frecuencia
volumen
intensidad
duración
progresión
umbral


----------------------------
INV-013 – EJERCICIOS
----------------------------

Para ejercicios relevantes registrar:

- objetivo;
- fundamento;
- contraindicación;
- fuente cuando exista.


----------------------------
INV-014 – TESTS
----------------------------

Para cada prueba utilizada:

investigar:

- qué mide;
- validez;
- confiabilidad cuando exista evidencia;
- población;
- protocolo;
- limitaciones.


----------------------------
INV-015 – SEGURIDAD
----------------------------

Las reglas relacionadas con riesgo requieren especial cuidado.

No inferir que ausencia de evidencia significa seguridad.


----------------------------
INV-016 – INCERTIDUMBRE
----------------------------

Cuando la literatura sea insuficiente o contradictoria:

NO escoger arbitrariamente una verdad.

Registrar:

EvidenceStatus = UNCERTAIN

y utilizar:

- rangos;
- configuración;
- heurística explícita;
- criterio conservador cuando corresponda.


----------------------------
INV-017 – CONTRADICCIONES
----------------------------

Si dos fuentes relevantes discrepan:

documentarlo.

No ocultar la contradicción.


----------------------------
INV-018 – REVISIÓN DE LITERATURA
----------------------------

Generar un documento:

/docs/EVIDENCE_REVIEW.md

Organizado por temas:

- demandas de la escalada;
- fuerza de dedos;
- fuerza general;
- potencia;
- resistencia;
- power endurance;
- periodización;
- recuperación;
- evaluación;
- prevención de lesiones;
- progresión.


----------------------------
INV-019 – MATRIZ DE EVIDENCIA
----------------------------

Generar:

/docs/RULE_EVIDENCE_MATRIX.md

o equivalente tabular.

Debe relacionar:

RuleID
Descripción
Valor/acción
Fuente
Tipo de evidencia
Confianza
Notas


----------------------------
INV-020 – BIBLIOGRAFÍA
----------------------------

Generar:

/docs/REFERENCES.md

con todas las fuentes utilizadas.


----------------------------
INV-021 – CITA EN DOCUMENTACIÓN
----------------------------

Cuando README o documentación afirme una decisión científica:

citar la fuente correspondiente.


----------------------------
INV-022 – NO CONFUNDIR CORRELACIÓN CON PRESCRIPCIÓN
----------------------------

Que una variable se correlacione con rendimiento NO significa automáticamente
que exista evidencia para prescribir un protocolo concreto.

Distinguir estas cosas explícitamente.


----------------------------
INV-023 – NO EXTRAPOLAR SIN MARCARLO
----------------------------

Si se extrapolan resultados de:

- levantadores;
- corredores;
- población general;
- atletas de otro deporte;

a escaladores:

marcarlo como evidencia indirecta.


----------------------------
INV-024 – REGLA DE PRODUCCIÓN
----------------------------

Una regla puede entrar al Ruleset de producción solo si tiene:

A) evidencia identificable;

o

B) una justificación explícita de que se trata de consenso, heurística,
precaución o decisión de diseño.

Nunca dejar origen desconocido.


======================================================================
4. RULESET DE INVESTIGACIÓN Y RULESET DE PRODUCCIÓN
======================================================================

No empieces fingiendo que ya conocemos todas las reglas.

Crear inicialmente:

Ruleset DEMO

Estado:

TESTING

Su propósito es comprobar técnicamente el motor.


Posteriormente crear:

Ruleset 1.0.0 Candidate

Estado:

RESEARCH

Después de revisar evidencia:

TESTING

y solo tras validación:

ACTIVE.


No mezclar:

“funciona técnicamente”

con

“está validado científicamente”.


======================================================================
5. ESTRUCTURA DE DATOS DEL MOTOR
======================================================================

Diseñar como mínimo:

tblRules
tblRuleConditions
tblRuleActions
tblRuleParameters
tblParameters
tblRulePackages
tblEvidence
tblRuleEvidence
tblExercises
tblTests
tblUsers
tblUserEquipment
tblUserLimitations
tblObjectives
tblPlans
tblSessions
tblSessionExercises
tblSessionFeedback
tblTestHistory
tblDecisionLog


======================================================================
6. ESTRUCTURA DEL EXCEL
======================================================================

Crear aproximadamente:

00_INICIO
01_PERFIL
02_OBJETIVOS
03_DISPONIBILIDAD
04_EQUIPO
05_EVALUACION
06_PLAN
07_SESION_ACTUAL
08_REGISTRO
09_PROGRESO
10_EJERCICIOS
11_TESTS
12_REGLAS
13_CONDICIONES
14_ACCIONES
15_PARAMETROS
16_RULESETS
17_EVIDENCIA
18_RULE_EVIDENCE
19_ESCALAS
20_HISTORIAL_TESTS
21_LOG_DECISIONES
22_CONFIGURACION
23_DEBUG

Las hojas técnicas pueden ocultarse.


======================================================================
7. ARQUITECTURA VBA
======================================================================

Separar aproximadamente:

modMain
modValidation

modRuleEngine
modRuleConditions
modRuleActions
modRuleResolver
modRuleValidation

modTrainingEngine
modPrescription
modScheduling
modProgression
modExercises
modTests

modCalculations
modPersistence

modUI
modReports

modDebug
modUtils


TODOS:

Option Explicit


No crear una macro monstruosa.


======================================================================
8. MACROS PRINCIPALES
======================================================================

Crear como mínimo:

GuardarPerfil()
ValidarPerfil()

GenerarPlan()
GenerarSemana()

CargarRulePackage()

EvaluarReglas()
EvaluarRegla()
EvaluarCondicion()
EjecutarAccion()
ResolverConflictos()

ValidateRulePackage()

RegistrarSesion()
ActualizarProgresion()

EjecutarReevaluacion()
CrearNuevoCiclo()

ImportarRuleset()
ExportarRuleset()

MostrarTrazabilidad()

ExportarPlanPDF()


======================================================================
9. REQUERIMIENTOS NO FUNCIONALES
======================================================================

RNF-001
Código modular.

RNF-002
No utilizar Select/Activate salvo necesidad justificada.

RNF-003
No usar referencias mágicas a celdas.

RNF-004
Preferir ListObjects y nombres estructurados.

RNF-005
Separar lógica y presentación.

RNF-006
Validación de entradas.

RNF-007
Manejo de errores.

RNF-008
Resultados deterministas.

RNF-009
Auditable.

RNF-010
Versionable.

RNF-011
Extensible.

RNF-012
Documentado.

RNF-013
No destruir historial.

RNF-014
No depender de modificación manual del VBA para cambiar una prescripción normal.

RNF-015
Interfaz utilizable por una persona sin conocimiento técnico.


======================================================================
10. TESTING
======================================================================

Crear pruebas del motor.

CASO A
Principiante
2 días
equipo limitado.

CASO B
Intermedio
3-4 días
objetivo fuerza.

CASO C
Avanzado
4-5 días
Boulder/potencia.

CASO D
Usuario con dolor o limitación.

CASO E
Usuario con 45 minutos.

CASO F
Mismo usuario:
Ruleset 1.0
contra
Ruleset 1.1.

CASO G
Regla de rendimiento permite ejercicio.
Regla Safety lo bloquea.
Debe ganar Safety.

CASO H
ParameterID inexistente.
Ruleset debe fallar validación.

CASO I
SourceID inexistente.
Detectar referencia rota.

CASO J
Regla sin evidencia ni justificación.
Debe quedar marcada para revisión.


Probar además:

EQ
NEQ
GT
GTE
LT
LTE
BETWEEN
IN
NOT_IN
AND
OR
prioridades
conflictos
acciones
parámetros
versionado
trazabilidad


======================================================================
11. CRITERIOS DE ACEPTACIÓN
======================================================================

El sistema NO está terminado hasta que:

CA-001
Puedo crear un usuario.

CA-002
Puedo registrar perfil.

CA-003
Puedo registrar disponibilidad.

CA-004
Puedo registrar equipo.

CA-005
Puedo registrar objetivos.

CA-006
Puedo registrar limitaciones.

CA-007
Puedo realizar evaluaciones.

CA-008
Puedo elegir un Ruleset válido.

CA-009
Puedo generar un plan.

CA-010
El motor calcula prescripción sin depender de rutinas fijas.

CA-011
Series, reps, intensidad y descansos proceden del sistema de reglas/parámetros.

CA-012
Puedo identificar exactamente qué RuleID influyó en una decisión.

CA-013
Puedo saber qué versión produjo el plan.

CA-014
Puedo consultar la fuente que justifica una regla.

CA-015
Las fuentes existen y han sido verificadas.

CA-016
Una regla sin evidencia está identificada explícitamente como heurística,
consenso, decisión de diseño o precaución.

CA-017
Puedo registrar lo realizado.

CA-018
El sistema usa el feedback.

CA-019
Puede progresar, mantener, reducir o descargar según reglas.

CA-020
No pierde historial.

CA-021
Puedo crear Ruleset 1.1 sin alterar 1.0.

CA-022
Puedo importar/exportar Rulesets.

CA-023
Un Ruleset inválido no puede activarse.

CA-024
Safety prevalece sobre rendimiento.

CA-025
El sistema conserva trazabilidad.

CA-026
No existen errores VBA conocidos.

CA-027
Existe README.

CA-028
Existe documentación de arquitectura.

CA-029
Existe revisión de evidencia.

CA-030
Existe matriz Rule → Evidence.

CA-031
Existe bibliografía.

CA-032
Existe registro de limitaciones e incertidumbres.


======================================================================
12. ENTREGABLES
======================================================================

Crear:

/training-climber-excel

    /src
        /vba
        /python

    /rules
        /demo
        /1.0.0-candidate

    /evidence

    /tests

    /docs
        ARCHITECTURE.md
        REQUIREMENTS.md
        RULE_ENGINE.md
        EVIDENCE_REVIEW.md
        RULE_EVIDENCE_MATRIX.md
        REFERENCES.md
        TEST_REPORT.md

    /dist

    README.md


Resultado esperado:

/dist/Entrenamiento_Escalada.xlsm


Si el entorno no permite generar directamente el .xlsm:

crear:

- workbook;
- módulos .bas;
- clases .cls;
- formularios;
- script instalador/importador;
- instrucciones exactas de compilación.

No fingir que openpyxl puede crear VBA desde cero.


======================================================================
13. FORMA DE TRABAJAR
======================================================================

FASE 1
Inspeccionar entorno.

FASE 2
Crear REQUIREMENTS.md a partir de estos requerimientos.

FASE 3
Diseñar arquitectura.

FASE 4
Diseñar modelo de datos.

FASE 5
Diseñar Rule Engine.

FASE 6
Diseñar versionado.

FASE 7
Construir infraestructura del workbook.

FASE 8
Implementar motor.

FASE 9
Implementar trazabilidad.

FASE 10
Construir Ruleset DEMO.

FASE 11
Probar técnicamente el motor.

FASE 12
Realizar investigación científica.

FASE 13
Crear EVIDENCE_REVIEW.md.

FASE 14
Crear REFERENCES.md.

FASE 15
Crear matriz Rule → Evidence.

FASE 16
Proponer Ruleset 1.0.0 Candidate.

FASE 17
Ejecutar pruebas sobre Ruleset Candidate.

FASE 18
Corregir inconsistencias.

FASE 19
Construir interfaz.

FASE 20
Completar reportes y dashboard.

FASE 21
Realizar pruebas integrales.

FASE 22
Crear TEST_REPORT.md.

FASE 23
Generar entregable final.


No me pidas autorización después de cada fase.

Continúa autónomamente mientras la decisión sea técnica y reversible.


======================================================================
14. REGLAS IMPORTANTES PARA CODEX
======================================================================

1. NO inventes evidencia.

2. NO inventes referencias.

3. NO conviertas automáticamente conocimiento interno del modelo en una regla
de producción.

4. INVESTIGA antes de establecer parámetros deportivos importantes.

5. REFERENCIA todo aquello que tenga una justificación científica.

6. Cuando una afirmación no tenga evidencia directa, indícalo.

7. Si utilizas una heurística, etiquétala como heurística.

8. Si una decisión es puramente de software, etiquétala como Design Decision.

9. Si la literatura contradice una regla propuesta, documenta el conflicto.

10. No escondas decisiones deportivas dentro de VBA.

11. Los números modificables pertenecen a parámetros o reglas.

12. Una actualización científica produce una NUEVA versión del Ruleset.

13. Una versión histórica nunca debe cambiar silenciosamente.

14. Los planes históricos deben seguir siendo reproducibles.

15. Cada decisión importante debe poder explicarse.


======================================================================
15. INSTRUCCIÓN FINAL
======================================================================

Empieza ahora.

NO respondas únicamente con una propuesta.

Trabaja directamente sobre el proyecto.

Primero genera y muestra brevemente:

1. matriz de requerimientos funcionales;
2. arquitectura;
3. modelo de datos;
4. diseño del Rule Engine;
5. estrategia de investigación;
6. estrategia de versionado.

Después comienza a crear los archivos sin esperar otra autorización.

Antes de declarar terminado el proyecto:

- ejecuta tests;
- verifica referencias;
- revisa Rule → Evidence;
- comprueba trazabilidad;
- revisa el archivo Excel;
- documenta limitaciones reales.

No declares una regla "basada en evidencia" si no puedes mostrar exactamente
qué evidencia la respalda.

El objetivo no es solamente construir un Excel que genere entrenamientos.

El objetivo es construir un SISTEMA DE PRESCRIPCIÓN VERSIONADO,
AUDITABLE, EXPLICABLE Y ACTUALIZABLE EN FUNCIÓN DE LA EVIDENCIA.