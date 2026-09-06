Attribute VB_Name = "modTrainingEngine"
Option Explicit

Public Sub GenerarPlan()
    On Error GoTo Failed
    Dim planID As String: planID = GenerarPlanSilencioso()
    If Len(planID) = 0 Then MsgBox "Perfil o Ruleset inválido.", vbExclamation: Exit Sub
    ThisWorkbook.Worksheets("06_PLAN").Activate
    MsgBox "Plan generado: " & planID & ". Consulte advertencias y trazabilidad.", vbInformation
    Exit Sub
Failed:
    MsgBox "No se pudo generar el plan: " & Err.Description, vbCritical
End Sub

Public Function GenerarPlanSilencioso() As String
    On Error GoTo Failed
    If Not ValidarPerfil(False) Then Exit Function
    If Not ValidateRulePackage(False) Then Exit Function
    Dim context As Object: Set context = LoadContext()
    Dim planID As String: planID = NewID("PLAN"): context("PlanID") = planID
    Dim version As String: version = CStr(NamedValue("cfgRulesetVersion", "0.1.0-demo"))
    Dim state As Object: Set state = EvaluateRules(context, version)
    PersistPlan planID, context, version
    GenerateSessions planID, context, state, version
    GenerarPlanSilencioso = planID
    Exit Function
Failed:
    ThisWorkbook.Worksheets("23_DEBUG").Range("B20").Value = "GenerarPlanSilencioso: " & Err.Number & " - " & Err.Description
    GenerarPlanSilencioso = "ERROR:" & Err.Number & ":" & Err.Description
End Function

Public Sub GenerarSemana(): GenerarPlan: End Sub

Private Sub PersistPlan(ByVal planID As String, ByVal context As Object, ByVal version As String)
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("PlanID") = planID: row("UserID") = CStr(context("UserID")): row("CreatedAt") = Now
    row("Status") = "GENERATED": row("RulePackageVersionUsed") = version: row("PrimaryObjective") = CStr(context("PrimaryObjective"))
    AppendRow "tblPlans", row
End Sub

Private Sub GenerateSessions(ByVal planID As String, ByVal context As Object, ByVal state As Object, ByVal version As String)
    Dim ex As ListObject: Set ex = FindTable("tblExercises")
    Dim included As Object, excluded As Object, ruleMap As Object
    Set included = state.Item("include"): Set excluded = state.Item("exclude"): Set ruleMap = state.Item("rulemap")
    Dim key As Variant, eid As String, i As Long, dayNo As Long, minutesUsed() As Long
    ReDim minutesUsed(1 To CLng(context("DaysAvailable")))
    For Each key In included.Keys
        If Left$(CStr(key), 3) = "EX:" Then
            eid = CStr(included(key))
            If Not excluded.Exists("EX:" & eid) And ExerciseAvailable(eid, CStr(context("Equipment")), ex) Then
                dayNo = LeastLoadedDay(minutesUsed)
                i = ExerciseRow(eid, ex)
                If minutesUsed(dayNo) + CLng(CellValue(ex, i, "EstimatedMinutes")) <= CLng(context("SessionMinutes")) Then
                    PersistSessionExercise planID, dayNo, eid, state, version, CStr(ruleMap("EX:" & eid)), CellValue(ex, i, "Name")
                    minutesUsed(dayNo) = minutesUsed(dayNo) + CLng(CellValue(ex, i, "EstimatedMinutes"))
                End If
            End If
        End If
    Next key
    For dayNo = 1 To UBound(minutesUsed): PersistSession planID, dayNo, minutesUsed(dayNo), version: Next dayNo
End Sub

Private Function ExerciseAvailable(ByVal eid As String, ByVal equipment As String, ByVal lo As ListObject) As Boolean
    Dim i As Long: i = ExerciseRow(eid, lo)
    Dim required As String: required = CStr(CellValue(lo, i, "Equipment"))
    ExerciseAvailable = (Len(required) = 0 Or InStr(1, "|" & equipment & "|", "|" & required & "|", vbTextCompare) > 0)
End Function

Private Function ExerciseRow(ByVal eid As String, ByVal lo As ListObject) As Long
    Dim i As Long
    For i = 1 To lo.ListRows.count: If CStr(CellValue(lo, i, "ExerciseID")) = eid Then ExerciseRow = i: Exit Function
    Next i
    Err.Raise vbObjectError + 150, "ExerciseRow", "ExerciseID inexistente: " & eid
End Function

Private Function LeastLoadedDay(ByRef minutesUsed() As Long) As Long
    Dim i As Long, winner As Long: winner = 1
    For i = 2 To UBound(minutesUsed): If minutesUsed(i) < minutesUsed(winner) Then winner = i
    Next i
    LeastLoadedDay = winner
End Function

Private Sub PersistSession(ByVal planID As String, ByVal dayNo As Long, ByVal minutes As Long, ByVal version As String)
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("SessionID") = planID & "-S" & dayNo: row("PlanID") = planID: row("Date") = Date + dayNo - 1
    row("Day") = dayNo: row("Objective") = NamedValue("inpPrimaryObjective", "Técnica"): row("PlannedMinutes") = minutes: row("Ruleset") = version
    AppendRow "tblSessions", row
End Sub

Private Sub PersistSessionExercise(ByVal planID As String, ByVal dayNo As Long, ByVal eid As String, ByVal state As Object, ByVal version As String, ByVal ruleID As String, ByVal exerciseName As String)
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("SessionExerciseID") = NewID("SE"): row("SessionID") = planID & "-S" & dayNo: row("ExerciseID") = eid
    row("Exercise") = exerciseName: row("Sets") = state("sets"): row("Reps") = state("reps"): row("Duration") = state("duration")
    row("Intensity") = state("intensity"): row("Load") = state("load"): row("Rest") = state("rest"): row("RPEObjective") = state("rpe")
    row("Notes") = state("progression"): row("Ruleset") = version: row("RuleIDs") = ruleID
    AppendRow "tblSessionExercises", row
End Sub
