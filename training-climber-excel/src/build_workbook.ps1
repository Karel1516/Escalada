param([switch]$Visible)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $projectRoot 'dist'
$outputPath = Join-Path $distDir 'Entrenamiento_Escalada.xlsm'
$vbaDir = Join-Path $PSScriptRoot 'vba'

function Set-Title($sheet, $title, $subtitle) {
    $sheet.Cells.Font.Name = 'Aptos'
    $sheet.Range('A1:H1').Merge()
    $sheet.Range('A1').Value2 = $title
    $sheet.Range('A1').Font.Size = 22
    $sheet.Range('A1').Font.Bold = $true
    $sheet.Range('A1').Font.Color = 0xFFFFFF
    $sheet.Range('A1:H1').Interior.Color = 0x56331F
    $sheet.Range('A2:H2').Merge()
    $sheet.Range('A2').Value2 = $subtitle
    $sheet.Range('A2').Font.Color = 0x666666
    $sheet.Rows.Item(1).RowHeight = 34
    $sheet.Columns.Item('A:H').ColumnWidth = 18
}

function Add-Name($book, $name, $sheet, $address) {
    $book.Names.Add($name, "='$($sheet.Name)'!$address") | Out-Null
}

function Add-InputForm($book, $sheet, $startRow, $fields) {
    $row = $startRow
    foreach ($field in $fields) {
        $sheet.Cells.Item($row, 1).Value2 = $field.Label
        $sheet.Cells.Item($row, 1).Font.Bold = $true
        $sheet.Cells.Item($row, 2).Value2 = [string]$field.Default
        $sheet.Cells.Item($row, 2).Interior.Color = 0xCCFFFF
        $sheet.Cells.Item($row, 2).Borders.LineStyle = 1
        Add-Name $book $field.Name $sheet ('$B$' + $row)
        $row++
    }
}

function Add-Table($sheet, $name, $startCell, $headers, $data) {
    $start = $sheet.Range($startCell)
    $r0 = $start.Row; $c0 = $start.Column
    for ($c = 0; $c -lt $headers.Count; $c++) { $sheet.Cells.Item($r0, $c0 + $c).Value2 = [string]$headers[$c] }
    $r = 1
    foreach ($record in $data) {
        for ($c = 0; $c -lt $headers.Count; $c++) {
            $value = $record.($headers[$c])
            if ($null -ne $value) { $sheet.Cells.Item($r0 + $r, $c0 + $c).Value2 = [string]$value }
        }
        $r++
    }
    $lastRow = $r0 + [Math]::Max(0, $data.Count)
    $lastCol = $c0 + $headers.Count - 1
    $range = $sheet.Range($sheet.Cells.Item($r0, $c0), $sheet.Cells.Item($lastRow, $lastCol))
    $table = $sheet.ListObjects.Add(1, $range, $null, 1)
    $table.Name = $name
    $table.TableStyle = 'TableStyleMedium2'
    if ($data.Count -eq 0 -and $table.ListRows.Count -gt 0) { $table.ListRows.Item(1).Delete() }
    $sheet.Columns.AutoFit() | Out-Null
    return $table
}

function Read-Csv($relativePath) { return @(Import-Csv -LiteralPath (Join-Path $projectRoot $relativePath) -Encoding utf8) }

function Combine-PackageCsv($fileName) {
    $all = @()
    foreach ($folder in @('demo', '1.0.0-candidate')) {
        $meta = Get-Content -LiteralPath (Join-Path $projectRoot "rules\$folder\package.json") -Raw | ConvertFrom-Json
        foreach ($row in (Read-Csv "rules\$folder\$fileName")) {
            $row | Add-Member -NotePropertyName RulesetVersion -NotePropertyValue $meta.version -Force
            $all += $row
        }
    }
    return $all
}

function Add-Button($sheet, $caption, $macro, $left, $top, $width = 180, $height = 32) {
    $shape = $sheet.Shapes.AddShape(5, $left, $top, $width, $height)
    $shape.TextFrame2.TextRange.Text = $caption
    $shape.Fill.ForeColor.RGB = 0xD88735
    $shape.Line.ForeColor.RGB = 0x56331F
    $shape.TextFrame2.TextRange.Font.Fill.ForeColor.RGB = 0xFFFFFF
    $shape.TextFrame2.TextRange.Font.Bold = $true
    $shape.OnAction = $macro
}

$excel = $null; $book = $null
try {
    New-Item -ItemType Directory -Path $distDir -Force | Out-Null
    if (Test-Path -LiteralPath $outputPath) { Remove-Item -LiteralPath $outputPath -Force }
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = [bool]$Visible
    $excel.DisplayAlerts = $false
    $excel.ScreenUpdating = $false
    $book = $excel.Workbooks.Add()

    $sheetNames = @('00_INICIO','01_PERFIL','02_OBJETIVOS','03_DISPONIBILIDAD','04_EQUIPO','05_EVALUACION','06_PLAN','07_SESION_ACTUAL','08_REGISTRO','09_PROGRESO','10_EJERCICIOS','11_TESTS','12_REGLAS','13_CONDICIONES','14_ACCIONES','15_PARAMETROS','16_RULESETS','17_EVIDENCIA','18_RULE_EVIDENCE','19_ESCALAS','20_HISTORIAL_TESTS','21_LOG_DECISIONES','22_CONFIGURACION','23_DEBUG')
    while ($book.Worksheets.Count -lt $sheetNames.Count) { $book.Worksheets.Add() | Out-Null }
    while ($book.Worksheets.Count -gt $sheetNames.Count) { $book.Worksheets.Item($book.Worksheets.Count).Delete() }
    for ($i = 0; $i -lt $sheetNames.Count; $i++) { $book.Worksheets.Item($i + 1).Name = $sheetNames[$i] }
    foreach ($sheet in $book.Worksheets) { Set-Title $sheet $sheet.Name 'Sistema versionado, auditable y explicable de prescripción para escalada' }

    $homeSheet = $book.Worksheets.Item('00_INICIO')
    $homeSheet.Range('A4:H4').Merge(); $homeSheet.Range('A4').Value2 = 'Panel principal'; $homeSheet.Range('A4').Font.Size = 16; $homeSheet.Range('A4').Font.Bold = $true
    $homeSheet.Range('A6').Value2 = 'Ruleset seleccionado'; $homeSheet.Range('B6').Formula = '=cfgRulesetVersion'
    $homeSheet.Range('A7').Value2 = 'Aviso'; $homeSheet.Range('B7:H8').Merge(); $homeSheet.Range('B7').Value2 = 'No diagnostica. Ante dolor o lesión, detenga estímulos agravantes y consulte a un profesional sanitario cualificado.'; $homeSheet.Range('B7').WrapText = $true
    Add-Button $homeSheet 'NUEVO USUARIO / PERFIL' 'IrPerfil' 20 190
    Add-Button $homeSheet 'GUARDAR PERFIL' 'GuardarPerfil' 220 190
    Add-Button $homeSheet 'EVALUACIONES' 'IrEvaluaciones' 420 190
    Add-Button $homeSheet 'GENERAR PLAN' 'GenerarPlan' 20 235
    Add-Button $homeSheet 'ENTRENAMIENTO DE HOY' 'IrSesionActual' 220 235
    Add-Button $homeSheet 'REGISTRAR ENTRENAMIENTO' 'IrRegistro' 420 235
    Add-Button $homeSheet 'PROGRESO' 'IrProgreso' 20 280
    Add-Button $homeSheet 'TRAZABILIDAD' 'MostrarTrazabilidad' 220 280
    Add-Button $homeSheet 'VALIDAR RULESET' 'ValidarRuleset' 420 280
    Add-Button $homeSheet 'EXPORTAR PLAN PDF' 'ExportarPlanPDF' 20 325
    Add-Button $homeSheet 'NUEVO CICLO' 'CrearNuevoCiclo' 220 325
    Add-Button $homeSheet 'DEBUG' 'ProbarMotor' 420 325

    $profile = $book.Worksheets.Item('01_PERFIL')
    Add-InputForm $book $profile 4 @(
        @{Label='UserID';Name='inpUserID';Default='USR-001'}, @{Label='Alias';Name='inpAlias';Default='Escalador'},
        @{Label='Edad';Name='inpAge';Default=30}, @{Label='Sexo (opcional)';Name='inpSex';Default=''},
        @{Label='Peso kg';Name='inpWeight';Default=70}, @{Label='Estatura cm';Name='inpHeight';Default=175},
        @{Label='Envergadura cm';Name='inpWingspan';Default=178}, @{Label='Años escalando';Name='inpExperienceYears';Default=3},
        @{Label='Modalidad';Name='inpModality';Default='Mixto'}, @{Label='Dolor dedos 0-10';Name='inpFingerPain';Default=0},
        @{Label='Estado limitación';Name='inpPainStatus';Default='ninguna'})
    Add-Table $profile 'tblUsers' 'A20' @('UserID','Alias','Age','Sex','WeightKg','HeightCm','WingspanCm','ExperienceYears','Modality','CreatedAt','Status') @() | Out-Null
    Add-Table $profile 'tblUserLimitations' 'M20' @('LimitationID','UserID','Region','Status','Severity','Notes','RecordedAt') @() | Out-Null

    $objectives = $book.Worksheets.Item('02_OBJETIVOS')
    Add-InputForm $book $objectives 4 @(@{Label='Objetivo principal';Name='inpPrimaryObjective';Default='Fuerza de dedos'})
    Add-Table $objectives 'tblObjectives' 'A8' @('ObjectiveEntryID','UserID','Objective','Priority','Weight','IsPrimary') @() | Out-Null

    $availability = $book.Worksheets.Item('03_DISPONIBILIDAD')
    Add-InputForm $book $availability 4 @(@{Label='Días disponibles';Name='inpDaysAvailable';Default=3},@{Label='Minutos por sesión';Name='inpSessionMinutes';Default=60},@{Label='Días concretos';Name='inpAvailableDays';Default='Lunes|Miércoles|Sábado'},@{Label='Descanso mínimo h';Name='inpMinRestHours';Default=24})

    $equipmentSheet = $book.Worksheets.Item('04_EQUIPO')
    Add-InputForm $book $equipmentSheet 4 @(@{Label='Equipo principal';Name='inpPrimaryEquipment';Default='Hangboard'},@{Label='Bandas disponibles';Name='inpHasBands';Default=$true})
    Add-Table $equipmentSheet 'tblUserEquipment' 'A10' @('UserEquipmentID','UserID','Equipment','Available','Notes') @() | Out-Null

    $eval = $book.Worksheets.Item('05_EVALUACION')
    Add-InputForm $book $eval 4 @(@{Label='TestID';Name='inpTestID';Default='T_MIFS20'},@{Label='Resultado';Name='inpTestResult';Default=''},@{Label='Unidad';Name='inpTestUnit';Default='N/kg'},@{Label='Protocolo';Name='inpTestProtocol';Default='Protocolo estandarizado sin dolor'},@{Label='Observaciones';Name='inpTestObservations';Default=''})
    Add-Button $eval 'GUARDAR RESULTADO' 'GuardarResultadoTest' 300 75

    $feedback = $book.Worksheets.Item('08_REGISTRO')
    Add-InputForm $book $feedback 4 @(
        @{Label='SessionID';Name='inpFeedbackSession';Default='MANUAL'},@{Label='Estado';Name='inpFeedbackStatus';Default='completada'},
        @{Label='Cumplimiento %';Name='inpCompletion';Default=100},@{Label='RPE';Name='inpSessionRPE';Default=6},@{Label='Fatiga 0-10';Name='inpFatigue';Default=3},
        @{Label='Calidad 1-5';Name='inpQuality';Default=4},@{Label='Dolor 0-10';Name='inpSessionPain';Default=0},@{Label='Series';Name='inpSetsDone';Default=''},
        @{Label='Reps';Name='inpRepsDone';Default=''},@{Label='Carga';Name='inpLoadDone';Default=''},@{Label='Tiempo';Name='inpTimeDone';Default=''},@{Label='Comentarios';Name='inpComments';Default=''})
    Add-Button $feedback 'REGISTRAR SESIÓN' 'RegistrarSesion' 300 75
    Add-Table $feedback 'tblSessionFeedback' 'A20' @('FeedbackID','SessionID','Status','CompletionPct','RPE','Fatigue','Quality','Pain','SetsDone','RepsDone','LoadDone','TimeDone','Comments','Timestamp') @() | Out-Null

    $plan = $book.Worksheets.Item('06_PLAN')
    Add-Table $plan 'tblPlans' 'A4' @('PlanID','UserID','CreatedAt','Status','RulePackageVersionUsed','PrimaryObjective') @() | Out-Null
    Add-Table $plan 'tblSessions' 'H4' @('SessionID','PlanID','Date','Day','Objective','PlannedMinutes','Ruleset') @() | Out-Null
    Add-Table $plan 'tblSessionExercises' 'P4' @('SessionExerciseID','SessionID','ExerciseID','Exercise','Sets','Reps','Duration','Intensity','Load','Rest','RPEObjective','Notes','Ruleset','RuleIDs') @() | Out-Null

    $book.Worksheets.Item('07_SESION_ACTUAL').Range('A4').Value2 = 'Consulte tblSessionExercises en 06_PLAN y filtre por fecha/sesión.'
    $book.Worksheets.Item('09_PROGRESO').Range('A3').Value2 = 'Decisión actual'; $book.Worksheets.Item('09_PROGRESO').Range('B3').Value2 = 'MAINTAIN'

    $exercises = Read-Csv 'evidence\exercises.csv'
    Add-Table $book.Worksheets.Item('10_EJERCICIOS') 'tblExercises' 'A4' @('ExerciseID','Name','Category','Subcategory','Objective','LevelMin','LevelMax','Modality','Equipment','BodyZone','StimulusType','PrescriptionUnit','MinSets','MaxSets','MinReps','MaxReps','Duration','IntensityType','RPE','RIR','Rest','Frequency','ProgressionRule','RegressionRule','Contraindications','EvidenceID','Tags','Notes','EstimatedMinutes') $exercises | Out-Null
    $tests = Read-Csv 'evidence\tests.csv'
    Add-Table $book.Worksheets.Item('11_TESTS') 'tblTests' 'A4' @('TestID','Name','Objective','RequiredLevel','Equipment','Unit','Protocol','Eligibility','Risks','SourceID','Validity','Reliability','Limitations') $tests | Out-Null

    $rules = Combine-PackageCsv 'rules.csv'
    Add-Table $book.Worksheets.Item('12_REGLAS') 'tblRules' 'A4' @('RulesetVersion','RuleID','RuleType','Priority','Description','Classification','EvidenceStatus','SourceIDs','Rationale','Enabled') $rules | Out-Null
    $conditions = Combine-PackageCsv 'conditions.csv'
    Add-Table $book.Worksheets.Item('13_CONDICIONES') 'tblRuleConditions' 'A4' @('RulesetVersion','ConditionID','RuleID','GroupID','Field','Operator','Value1','Value2') $conditions | Out-Null
    $actions = Combine-PackageCsv 'actions.csv'
    Add-Table $book.Worksheets.Item('14_ACCIONES') 'tblRuleActions' 'A4' @('RulesetVersion','ActionID','RuleID','ActionType','Target','Value') $actions | Out-Null
    $catalog = @('INCLUDE_EXERCISE','EXCLUDE_EXERCISE','INCLUDE_CATEGORY','EXCLUDE_CATEGORY','SET_SETS','SET_REPS','SET_DURATION','SET_INTENSITY','SET_REST','SET_MIN','SET_MAX','MULTIPLY_VOLUME','SET_FREQUENCY','SET_LOAD','SET_LOAD_PERCENT','SET_RPE','SET_RIR','ALLOW_PROGRESSION','BLOCK_PROGRESSION','TRIGGER_DELOAD','TRIGGER_REEVALUATION','SHOW_WARNING') | ForEach-Object { [pscustomobject]@{ActionType=$_;Description='Acción reconocida por el motor'} }
    Add-Table $book.Worksheets.Item('14_ACCIONES') 'tblActionCatalog' 'H4' @('ActionType','Description') @($catalog) | Out-Null
    $parameters = Combine-PackageCsv 'parameters.csv'
    Add-Table $book.Worksheets.Item('15_PARAMETROS') 'tblParameters' 'A4' @('RulesetVersion','ParameterID','Category','Name','Value','Unit','EvidenceIDs','EvidenceStatus') $parameters | Out-Null
    Add-Table $book.Worksheets.Item('15_PARAMETROS') 'tblRuleParameters' 'K4' @('RuleID','RulesetVersion','ParameterID','Purpose') @() | Out-Null

    $packages = @(
        [pscustomobject]@{Version='0.1.0-demo';Name='DEMO';Status='TESTING';Valid='TRUE';Default='TRUE';Immutable='TRUE';Notes='Pruebas técnicas, no prescripción validada'},
        [pscustomobject]@{Version='1.0.0-candidate';Name='Candidate';Status='RESEARCH';Valid='TRUE';Default='FALSE';Immutable='TRUE';Notes='Pendiente de revisión humana y activación'})
    Add-Table $book.Worksheets.Item('16_RULESETS') 'tblRulePackages' 'A4' @('Version','Name','Status','Valid','Default','Immutable','Notes') $packages | Out-Null

    $evidence = Read-Csv 'evidence\evidence.csv'
    Add-Table $book.Worksheets.Item('17_EVIDENCIA') 'tblEvidence' 'A4' @('SourceID','SourceType','Authors','Title','Year','Journal','Volume','Issue','Pages','DOI','PMID','URL','AccessedDate','EvidenceLevel','ClimbingSpecific','Population','MainFinding','Limitations','Notes') $evidence | Out-Null
    $ruleEvidence = Read-Csv 'evidence\rule_evidence.csv'
    Add-Table $book.Worksheets.Item('18_RULE_EVIDENCE') 'tblRuleEvidence' 'A4' @('RuleID','RulesetVersion','SourceID','RelationType','EvidenceStrength','Notes') $ruleEvidence | Out-Null

    $scales = @(
        [pscustomobject]@{ScaleID='FONT';Discipline='Deportiva';Code='6a';Order=1},[pscustomobject]@{ScaleID='FONT';Discipline='Deportiva';Code='7a';Order=2},
        [pscustomobject]@{ScaleID='V';Discipline='Boulder';Code='V3';Order=1},[pscustomobject]@{ScaleID='V';Discipline='Boulder';Code='V6';Order=2})
    Add-Table $book.Worksheets.Item('19_ESCALAS') 'tblGradeScales' 'A4' @('ScaleID','Discipline','Code','Order') $scales | Out-Null
    Add-Table $book.Worksheets.Item('20_HISTORIAL_TESTS') 'tblTestHistory' 'A4' @('TestHistoryID','UserID','TestID','Date','Result','Unit','Protocol','Ruleset','Observations') @() | Out-Null
    Add-Table $book.Worksheets.Item('21_LOG_DECISIONES') 'tblDecisionLog' 'A4' @('DecisionID','UserID','PlanID','RulePackageVersion','RuleID','InputValues','Action','PreviousValue','NewValue','Timestamp') @() | Out-Null

    $config = $book.Worksheets.Item('22_CONFIGURACION')
    $config.Range('A4').Value2 = 'RulesetVersion'; $config.Range('B4').Value2 = '0.1.0-demo'; $config.Range('B4').Interior.Color = 0xCCFFFF
    $config.Range('A5').Value2 = 'CycleID'; $config.Range('B5').Value2 = 'CYCLE-001'; $config.Range('A6').Value2 = 'Debug'; $config.Range('B6').Value2 = $true
    Add-Name $book 'cfgRulesetVersion' $config '$B$4'; Add-Name $book 'cfgCycleID' $config '$B$5'; Add-Name $book 'cfgDebug' $config '$B$6'

    $debug = $book.Worksheets.Item('23_DEBUG')
    $debug.Range('A3').Value2 = 'Resultado motor'; $debug.Range('A4').Value2 = 'Exclusiones'; $debug.Range('A5').Value2 = 'Advertencias'; $debug.Range('A8').Value2 = 'Validación'

    foreach ($sheet in $book.Worksheets) {
        $sheet.Application.ActiveWindow.DisplayGridlines = $false
        $sheet.Rows.Item(3).RowHeight = 8
        $sheet.UsedRange.VerticalAlignment = -4108
    }
    $book.Worksheets.Item('00_INICIO').Activate()
    $excel.ActiveWindow.FreezePanes = $false

    $book.SaveAs($outputPath, 52)
    $vbaEmbedded = $false
    try {
        $vbProject = $book.VBProject
        foreach ($modulePath in (Get-ChildItem -LiteralPath $vbaDir -Filter '*.bas' | Sort-Object Name)) { $vbProject.VBComponents.Import($modulePath.FullName) | Out-Null }
        $book.Save()
        $vbaEmbedded = ($vbProject.VBComponents.Count -gt 1)
    } catch {
        Write-Warning "Excel creó el XLSM, pero bloqueó la inserción VBA: $($_.Exception.Message)"
    }
    $book.Close($true)
    $excel.Quit()
    $book = $null; $excel = $null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    Set-Content -LiteralPath (Join-Path $distDir 'BUILD_STATUS.txt') -Value @(
        "Workbook=$outputPath", "Created=$(Get-Date -Format o)", "VBAEmbedded=$vbaEmbedded", "SourceModules=$((Get-ChildItem -LiteralPath $vbaDir -Filter '*.bas').Count)") -Encoding utf8
    Write-Output "CREATED $outputPath"
    Write-Output "VBA_EMBEDDED $vbaEmbedded"
} finally {
    if ($null -ne $book) { try { $book.Close($false) } catch {} }
    if ($null -ne $excel) { try { $excel.Quit() } catch {} }
}
