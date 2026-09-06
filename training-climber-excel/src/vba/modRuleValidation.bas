Attribute VB_Name = "modRuleValidation"
Option Explicit

Public Function ValidateRulePackage(Optional ByVal showMessage As Boolean = True) As Boolean
    On Error GoTo Failed
    Dim errors As Collection: Set errors = New Collection
    Dim version As String: version = CStr(NamedValue("cfgRulesetVersion", "0.1.0-demo"))
    ValidateVersion version, errors
    ValidateRules version, errors
    ValidateConditions version, errors
    ValidateActions version, errors
    ValidateRulePackage = (errors.count = 0)
    WriteValidation errors, version
    If showMessage Then MsgBox IIf(errors.count = 0, "Ruleset válido: " & version, CStr(errors.count) & " error(es). Consulte 23_DEBUG."), IIf(errors.count = 0, vbInformation, vbExclamation)
    Exit Function
Failed:
    ValidateRulePackage = False
    If showMessage Then MsgBox "Error de validación: " & Err.Description, vbCritical
End Function

Private Sub ValidateVersion(ByVal version As String, ByVal errors As Collection)
    Dim re As Object: Set re = CreateObject("VBScript.RegExp")
    re.Pattern = "^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?$"
    If Not re.Test(version) Then errors.Add "Versión inválida: " & version
End Sub

Private Sub ValidateRules(ByVal version As String, ByVal errors As Collection)
    Dim lo As ListObject: Set lo = FindTable("tblRules")
    Dim seen As Object: Set seen = CreateObject("Scripting.Dictionary")
    Dim i As Long, rid As String, sources As Variant, source As Variant
    For i = 1 To lo.ListRows.count
        If CStr(CellValue(lo, i, "RulesetVersion")) = version Then
            rid = CStr(CellValue(lo, i, "RuleID"))
            If seen.Exists(rid) Then errors.Add "RuleID duplicado: " & rid Else seen(rid) = True
            If Not IsNumeric(CellValue(lo, i, "Priority")) Then errors.Add "Prioridad inválida: " & rid
            If Len(CStr(CellValue(lo, i, "SourceIDs"))) = 0 And Len(CStr(CellValue(lo, i, "Rationale"))) = 0 Then errors.Add "Regla sin origen: " & rid
            sources = Split(CStr(CellValue(lo, i, "SourceIDs")), "|")
            For Each source In sources
                If Len(CStr(source)) > 0 And Not ValueExists("tblEvidence", "SourceID", CStr(source)) Then errors.Add "SourceID inexistente: " & source
            Next source
        End If
    Next i
End Sub

Private Sub ValidateConditions(ByVal version As String, ByVal errors As Collection)
    Dim lo As ListObject: Set lo = FindTable("tblRuleConditions")
    Dim i As Long, op As String, allowed As String: allowed = "|EQ|NEQ|GT|GTE|LT|LTE|BETWEEN|IN|NOT_IN|EXISTS|NOT_EXISTS|"
    For i = 1 To lo.ListRows.count
        If CStr(CellValue(lo, i, "RulesetVersion")) = version Then
            op = UCase$(CStr(CellValue(lo, i, "Operator")))
            If InStr(allowed, "|" & op & "|") = 0 Then errors.Add "Operador inexistente: " & op
            If op = "BETWEEN" And IsNumeric(CellValue(lo, i, "Value1")) And IsNumeric(CellValue(lo, i, "Value2")) Then If CDbl(CellValue(lo, i, "Value1")) > CDbl(CellValue(lo, i, "Value2")) Then errors.Add "Rango inválido: " & CellValue(lo, i, "ConditionID")
        End If
    Next i
End Sub

Private Sub ValidateActions(ByVal version As String, ByVal errors As Collection)
    Dim lo As ListObject: Set lo = FindTable("tblRuleActions")
    Dim i As Long, actionName As String, target As String, value As String
    For i = 1 To lo.ListRows.count
        If CStr(CellValue(lo, i, "RulesetVersion")) = version Then
            actionName = CStr(CellValue(lo, i, "ActionType")): target = CStr(CellValue(lo, i, "Target")): value = CStr(CellValue(lo, i, "Value"))
            If Not ValueExists("tblActionCatalog", "ActionType", actionName) Then errors.Add "ActionType inexistente: " & actionName
            If Right$(actionName, 8) = "EXERCISE" And Not ValueExists("tblExercises", "ExerciseID", target) Then errors.Add "ExerciseID inexistente: " & target
            If Left$(value, 6) = "PARAM:" And Not ValueExists2("tblParameters", "ParameterID", Mid$(value, 7), "RulesetVersion", version) Then errors.Add "ParameterID inexistente: " & Mid$(value, 7)
        End If
    Next i
End Sub

Private Function ValueExists(ByVal tableName As String, ByVal columnName As String, ByVal wanted As String) As Boolean
    Dim lo As ListObject: Set lo = FindTable(tableName)
    Dim i As Long
    For i = 1 To lo.ListRows.count
        If StrComp(CStr(CellValue(lo, i, columnName)), wanted, vbTextCompare) = 0 Then ValueExists = True: Exit Function
    Next i
End Function

Private Function ValueExists2(ByVal tableName As String, ByVal col1 As String, ByVal val1 As String, ByVal col2 As String, ByVal val2 As String) As Boolean
    Dim lo As ListObject: Set lo = FindTable(tableName)
    Dim i As Long
    For i = 1 To lo.ListRows.count
        If CStr(CellValue(lo, i, col1)) = val1 And CStr(CellValue(lo, i, col2)) = val2 Then ValueExists2 = True: Exit Function
    Next i
End Function

Private Sub WriteValidation(ByVal errors As Collection, ByVal version As String)
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets("23_DEBUG")
    ws.Range("A8:B200").ClearContents: ws.Range("A8").Value = "Validación " & version
    Dim i As Long
    If errors.count = 0 Then ws.Range("B8").Value = "OK" Else For i = 1 To errors.count: ws.Cells(8 + i, 2).Value = errors(i): Next i
End Sub
