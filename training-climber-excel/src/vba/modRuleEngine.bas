Attribute VB_Name = "modRuleEngine"
Option Explicit

Public Function LoadContext() As Object
    Dim c As Object: Set c = CreateObject("Scripting.Dictionary")
    c.CompareMode = vbTextCompare
    c("UserID") = NamedValue("inpUserID", "USR-DEMO")
    c("PrimaryObjective") = NamedValue("inpPrimaryObjective", "Técnica")
    c("ExperienceYears") = CDbl(NamedValue("inpExperienceYears", 0))
    c("Equipment") = NamedValue("inpPrimaryEquipment", "Muro")
    c("HasBands") = CBool(NamedValue("inpHasBands", False))
    c("FingerPain") = CDbl(NamedValue("inpFingerPain", 0))
    c("PainStatus") = NamedValue("inpPainStatus", "ninguna")
    c("Modality") = NamedValue("inpModality", "Mixto")
    c("DaysAvailable") = CDbl(NamedValue("inpDaysAvailable", 2))
    c("SessionMinutes") = CDbl(NamedValue("inpSessionMinutes", 60))
    c("Completion") = CDbl(NamedValue("inpCompletion", 100))
    c("SessionRPE") = CDbl(NamedValue("inpSessionRPE", 5))
    c("SessionPain") = CDbl(NamedValue("inpSessionPain", 0))
    c("Fatigue") = CDbl(NamedValue("inpFatigue", 3))
    Set LoadContext = c
End Function

Public Function EvaluateRules(ByVal context As Object, ByVal version As String) As Object
    Dim state As Object, inc As Object, exc As Object, ruleMap As Object
    Set state = CreateObject("Scripting.Dictionary"): Set inc = CreateObject("Scripting.Dictionary")
    Set exc = CreateObject("Scripting.Dictionary"): Set ruleMap = CreateObject("Scripting.Dictionary")
    Set state("include") = inc: Set state("exclude") = exc: Set state("rulemap") = ruleMap
    state("sets") = 1: state("reps") = "": state("duration") = "": state("intensity") = ""
    state("rest") = 0: state("frequency") = 1: state("load") = "": state("rpe") = "": state("rir") = ""
    state("progression") = "MAINTAIN": state("warnings") = ""
    state("PlanID") = IIf(context.Exists("PlanID"), CStr(context("PlanID")), "EVALUATION")

    Dim rules As ListObject: Set rules = FindTable("tblRules")
    Dim matched() As Long, count As Long, i As Long
    ReDim matched(1 To Application.Max(1, rules.ListRows.count))
    For i = 1 To rules.ListRows.count
        If CStr(CellValue(rules, i, "RulesetVersion")) = version And IsTruthy(CellValue(rules, i, "Enabled")) Then
            If EvaluateRule(CStr(CellValue(rules, i, "RuleID")), context, version) Then count = count + 1: matched(count) = i
        End If
    Next i
    SortRuleRows matched, count, rules

    Dim actions As ListObject: Set actions = FindTable("tblRuleActions")
    Dim j As Long, rid As String, value As Variant, actionName As String, target As String
    For i = 1 To count
        rid = CStr(CellValue(rules, matched(i), "RuleID"))
        For j = 1 To actions.ListRows.count
            If CStr(CellValue(actions, j, "RulesetVersion")) = version And CStr(CellValue(actions, j, "RuleID")) = rid Then
                actionName = CStr(CellValue(actions, j, "ActionType")): target = CStr(CellValue(actions, j, "Target"))
                value = ResolveValue(CellValue(actions, j, "Value"), version)
                ExecuteAction actionName, target, value, state
                If actionName = "INCLUDE_EXERCISE" Then state("rulemap")("EX:" & target) = rid
                LogDecision CStr(context("UserID")), CStr(state("PlanID")), version, rid, ContextSummary(context), actionName & ":" & target, "", value
            End If
        Next j
    Next i
    Set EvaluateRules = state
End Function

Public Function EvaluateRule(ByVal ruleID As String, ByVal context As Object, ByVal version As String) As Boolean
    Dim conds As ListObject: Set conds = FindTable("tblRuleConditions")
    Dim groups As Object: Set groups = CreateObject("Scripting.Dictionary")
    Dim i As Long, gid As String, fieldName As String, ok As Boolean, found As Boolean, actual As Variant
    For i = 1 To conds.ListRows.count
        If CStr(CellValue(conds, i, "RulesetVersion")) = version And CStr(CellValue(conds, i, "RuleID")) = ruleID Then
            found = True: gid = CStr(CellValue(conds, i, "GroupID")): fieldName = CStr(CellValue(conds, i, "Field"))
            If Not groups.Exists(gid) Then groups(gid) = True
            If context.Exists(fieldName) Then actual = context(fieldName) Else actual = Empty
            ok = EvaluateCondition(actual, CStr(CellValue(conds, i, "Operator")), CellValue(conds, i, "Value1"), CellValue(conds, i, "Value2"))
            groups(gid) = CBool(groups(gid)) And ok
        End If
    Next i
    If Not found Then EvaluateRule = True: Exit Function
    Dim key As Variant
    For Each key In groups.Keys
        If groups(key) Then EvaluateRule = True: Exit Function
    Next key
End Function

Private Sub SortRuleRows(ByRef rows() As Long, ByVal count As Long, ByVal lo As ListObject)
    Dim i As Long, j As Long, temp As Long
    For i = 1 To count - 1
        For j = i + 1 To count
            If ProposalBeats(CStr(CellValue(lo, rows(j), "RuleType")), CLng(CellValue(lo, rows(j), "Priority")), CStr(CellValue(lo, rows(j), "RuleID")), CStr(CellValue(lo, rows(i), "RuleType")), CLng(CellValue(lo, rows(i), "Priority")), CStr(CellValue(lo, rows(i), "RuleID"))) Then temp = rows(i): rows(i) = rows(j): rows(j) = temp
        Next j
    Next i
End Sub

Private Function ResolveValue(ByVal rawValue As Variant, ByVal version As String) As Variant
    Dim text As String: text = CStr(rawValue)
    If Left$(text, 6) <> "PARAM:" Then ResolveValue = rawValue: Exit Function
    Dim lo As ListObject: Set lo = FindTable("tblParameters")
    Dim i As Long, pid As String: pid = Mid$(text, 7)
    For i = 1 To lo.ListRows.count
        If CStr(CellValue(lo, i, "RulesetVersion")) = version And CStr(CellValue(lo, i, "ParameterID")) = pid Then ResolveValue = CellValue(lo, i, "Value"): Exit Function
    Next i
    Err.Raise vbObjectError + 140, "ResolveValue", "ParameterID inexistente: " & pid
End Function

Private Function ContextSummary(ByVal context As Object) As String
    Dim key As Variant, output As String
    For Each key In context.Keys
        If Len(output) > 0 Then output = output & ";"
        output = output & CStr(key) & "=" & CStr(context(key))
    Next key
    ContextSummary = output
End Function

Public Sub CargarRulePackage()
    MsgBox "Use ImportarRuleset para cargar CSV y ValidateRulePackage antes de activar.", vbInformation
End Sub

Public Sub EvaluarReglas()
    Dim c As Object, s As Object: Set c = LoadContext()
    Set s = EvaluateRules(c, CStr(NamedValue("cfgRulesetVersion", "0.1.0-demo")))
    ThisWorkbook.Worksheets("23_DEBUG").Range("B3").Value = "Incluidos: " & Join(s("include").Items, ", ")
    ThisWorkbook.Worksheets("23_DEBUG").Range("B4").Value = "Excluidos: " & Join(s("exclude").Items, ", ")
    ThisWorkbook.Worksheets("23_DEBUG").Range("B5").Value = s("warnings")
End Sub

Public Sub EvaluarRegla(): EvaluarReglas: End Sub
Public Sub EvaluarCondicion(): MsgBox "La evaluación se ejecuta sobre tblRuleConditions.": End Sub
Public Sub EjecutarAccion(): MsgBox "Las acciones se ejecutan desde tblRuleActions.": End Sub
Public Sub ResolverConflictos(): EvaluarReglas: End Sub
