Attribute VB_Name = "modPersistence"
Option Explicit

Public Sub AppendRow(ByVal tableName As String, ByVal values As Object)
    Dim lo As ListObject, lr As ListRow, key As Variant
    Set lo = FindTable(tableName)
    If lo Is Nothing Then Err.Raise vbObjectError + 120, "AppendRow", "Tabla inexistente: " & tableName
    Set lr = lo.ListRows.Add
    For Each key In values.Keys
        lr.Range.Cells(1, ColIndex(lo, CStr(key))).Value = values(key)
    Next key
End Sub

Public Sub LogDecision(ByVal userID As String, ByVal planID As String, ByVal version As String, ByVal ruleID As String, ByVal inputs As String, ByVal actionName As String, ByVal oldValue As Variant, ByVal newValue As Variant)
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("DecisionID") = NewID("DEC"): row("UserID") = userID: row("PlanID") = planID
    row("RulePackageVersion") = version: row("RuleID") = ruleID: row("InputValues") = inputs
    row("Action") = actionName: row("PreviousValue") = oldValue: row("NewValue") = newValue: row("Timestamp") = Now
    AppendRow "tblDecisionLog", row
End Sub
