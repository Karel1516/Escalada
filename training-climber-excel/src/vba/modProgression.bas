Attribute VB_Name = "modProgression"
Option Explicit

Public Sub ActualizarProgresion()
    Dim c As Object, s As Object: Set c = LoadContext(): c("PlanID") = "FEEDBACK"
    Set s = EvaluateRules(c, CStr(NamedValue("cfgRulesetVersion", "0.1.0-demo")))
    ThisWorkbook.Worksheets("09_PROGRESO").Range("B3").Value = s("progression")
    MsgBox "Decisión: " & s("progression"), vbInformation
End Sub

Public Sub RegistrarSesion()
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("FeedbackID") = NewID("FB"): row("SessionID") = NamedValue("inpFeedbackSession", "MANUAL")
    row("Status") = NamedValue("inpFeedbackStatus", "completada"): row("CompletionPct") = NamedValue("inpCompletion", 100)
    row("RPE") = NamedValue("inpSessionRPE", 5): row("Fatigue") = NamedValue("inpFatigue", 3): row("Quality") = NamedValue("inpQuality", 3)
    row("Pain") = NamedValue("inpSessionPain", 0): row("SetsDone") = NamedValue("inpSetsDone", ""): row("RepsDone") = NamedValue("inpRepsDone", "")
    row("LoadDone") = NamedValue("inpLoadDone", ""): row("TimeDone") = NamedValue("inpTimeDone", ""): row("Comments") = NamedValue("inpComments", ""): row("Timestamp") = Now
    AppendRow "tblSessionFeedback", row
    ActualizarProgresion
End Sub
