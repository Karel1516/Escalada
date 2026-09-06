Attribute VB_Name = "modRuleResolver"
Option Explicit

Public Function RulePrecedence(ByVal ruleType As String) As Long
    Select Case UCase$(ruleType)
        Case "SAFETY": RulePrecedence = 500
        Case "EXCLUSION": RulePrecedence = 400
        Case "ELIGIBILITY": RulePrecedence = 300
        Case "PRESCRIPTION": RulePrecedence = 200
        Case "PREFERENCE": RulePrecedence = 100
        Case Else: RulePrecedence = 150
    End Select
End Function

Public Function ProposalBeats(ByVal typeA As String, ByVal priorityA As Long, ByVal idA As String, ByVal typeB As String, ByVal priorityB As Long, ByVal idB As String) As Boolean
    If RulePrecedence(typeA) <> RulePrecedence(typeB) Then
        ProposalBeats = RulePrecedence(typeA) > RulePrecedence(typeB)
    ElseIf priorityA <> priorityB Then
        ProposalBeats = priorityA > priorityB
    Else
        ProposalBeats = StrComp(idA, idB, vbTextCompare) < 0
    End If
End Function
