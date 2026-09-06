Attribute VB_Name = "modDebug"
Option Explicit

Public Sub LimpiarDebug()
    ThisWorkbook.Worksheets("23_DEBUG").Range("A3:Z1000").ClearContents
End Sub

Public Sub ProbarMotor()
    LimpiarDebug
    Call ValidateRulePackage(True)
    EvaluarReglas
End Sub
