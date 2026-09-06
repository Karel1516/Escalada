Attribute VB_Name = "modMain"
Option Explicit

Public Sub GuardarPerfil()
    If Not ValidarPerfil(False) Then MsgBox "Perfil incompleto o inválido.", vbExclamation: Exit Sub
    Dim row As Object: Set row = CreateObject("Scripting.Dictionary")
    row("UserID") = NamedValue("inpUserID"): row("Alias") = NamedValue("inpAlias"): row("Age") = NamedValue("inpAge")
    row("Sex") = NamedValue("inpSex"): row("WeightKg") = NamedValue("inpWeight"): row("HeightCm") = NamedValue("inpHeight")
    row("WingspanCm") = NamedValue("inpWingspan"): row("ExperienceYears") = NamedValue("inpExperienceYears")
    row("Modality") = NamedValue("inpModality"): row("CreatedAt") = Now: row("Status") = "ACTIVE"
    AppendRow "tblUsers", row
    MsgBox "Perfil guardado sin sobrescribir registros anteriores.", vbInformation
End Sub

Public Sub CrearNuevoCiclo()
    ThisWorkbook.Names("cfgCycleID").RefersToRange.Value = NewID("CYCLE")
    MsgBox "Nuevo ciclo creado. El historial anterior se conserva.", vbInformation
End Sub

Public Sub EjecutarReevaluacion()
    ThisWorkbook.Worksheets("05_EVALUACION").Activate
    MsgBox "Registre una nueva fila de test; los resultados anteriores no se sobrescriben.", vbInformation
End Sub

Public Sub MostrarTrazabilidad(): ThisWorkbook.Worksheets("21_LOG_DECISIONES").Activate: End Sub
