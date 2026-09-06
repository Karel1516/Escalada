Attribute VB_Name = "modReports"
Option Explicit

Public Sub ExportarPlanPDF()
    On Error GoTo Failed
    Dim target As String: target = ThisWorkbook.Path & Application.PathSeparator & "Plan_" & Format$(Now, "yyyymmdd_hhnnss") & ".pdf"
    ThisWorkbook.Worksheets(Array("06_PLAN", "07_SESION_ACTUAL", "09_PROGRESO")).Select
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, Filename:=target, Quality:=xlQualityStandard, IncludeDocProperties:=True, IgnorePrintAreas:=False, OpenAfterPublish:=False
    ThisWorkbook.Worksheets("06_PLAN").Select
    MsgBox "PDF exportado: " & target, vbInformation
    Exit Sub
Failed:
    MsgBox "No se pudo exportar PDF: " & Err.Description, vbCritical
End Sub

Public Sub ExportarRuleset()
    MsgBox "Use el paquete CSV versionado en /rules. La exportación preserva package.json, rules.csv, conditions.csv, actions.csv y parameters.csv.", vbInformation
End Sub

Public Sub ImportarRuleset()
    MsgBox "Copie el nuevo paquete CSV a /rules y ejecute el constructor/importador. ValidateRulePackage impide activar referencias rotas.", vbInformation
End Sub
