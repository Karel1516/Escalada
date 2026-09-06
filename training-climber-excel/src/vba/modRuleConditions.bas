Attribute VB_Name = "modRuleConditions"
Option Explicit

Public Function EvaluateCondition(ByVal actual As Variant, ByVal op As String, ByVal value1 As Variant, Optional ByVal value2 As Variant) As Boolean
    Select Case UCase$(Trim$(op))
        Case "EQ": EvaluateCondition = (CStr(actual) = CStr(value1))
        Case "NEQ": EvaluateCondition = (CStr(actual) <> CStr(value1))
        Case "GT": EvaluateCondition = (CDbl(actual) > CDbl(value1))
        Case "GTE": EvaluateCondition = (CDbl(actual) >= CDbl(value1))
        Case "LT": EvaluateCondition = (CDbl(actual) < CDbl(value1))
        Case "LTE": EvaluateCondition = (CDbl(actual) <= CDbl(value1))
        Case "BETWEEN": EvaluateCondition = (CDbl(actual) >= CDbl(value1) And CDbl(actual) <= CDbl(value2))
        Case "IN": EvaluateCondition = InPipeList(CStr(actual), CStr(value1))
        Case "NOT_IN": EvaluateCondition = Not InPipeList(CStr(actual), CStr(value1))
        Case "EXISTS": EvaluateCondition = Len(Trim$(CStr(actual))) > 0
        Case "NOT_EXISTS": EvaluateCondition = Len(Trim$(CStr(actual))) = 0
        Case Else: Err.Raise vbObjectError + 110, "EvaluateCondition", "Operador desconocido: " & op
    End Select
End Function

Private Function InPipeList(ByVal actual As String, ByVal pipeValues As String) As Boolean
    Dim item As Variant
    For Each item In Split(pipeValues, "|")
        If StrComp(Trim$(actual), Trim$(CStr(item)), vbTextCompare) = 0 Then InPipeList = True: Exit Function
    Next item
End Function
