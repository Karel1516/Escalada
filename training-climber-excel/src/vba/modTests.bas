Attribute VB_Name = "modTests"
Option Explicit

Public Sub GuardarResultadoTest()
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("TestHistoryID") = NewID("TEST"): row("UserID") = NamedValue("inpUserID", "")
    row("TestID") = NamedValue("inpTestID", ""): row("Date") = Date: row("Result") = NamedValue("inpTestResult", "")
    row("Unit") = NamedValue("inpTestUnit", ""): row("Protocol") = NamedValue("inpTestProtocol", "")
    row("Ruleset") = NamedValue("cfgRulesetVersion", ""): row("Observations") = NamedValue("inpTestObservations", "")
    AppendRow "tblTestHistory", row
    MsgBox "Resultado añadido al historial.", vbInformation
End Sub
