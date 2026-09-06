Attribute VB_Name = "modValidation"
Option Explicit

Public Function ValidarPerfil(Optional ByVal showMessage As Boolean = True) As Boolean
    Dim ok As Boolean: ok = Len(CStr(NamedValue("inpUserID", ""))) > 0 And Len(CStr(NamedValue("inpAlias", ""))) > 0
    ok = ok And IsNumeric(NamedValue("inpAge", "")) And CDbl(NamedValue("inpAge", 0)) >= 14
    ok = ok And IsNumeric(NamedValue("inpWeight", "")) And CDbl(NamedValue("inpWeight", 0)) > 0
    ValidarPerfil = ok
    If showMessage Then MsgBox IIf(ok, "Perfil válido.", "Complete UserID, alias, edad y peso con valores válidos."), IIf(ok, vbInformation, vbExclamation)
End Function

Public Sub ValidarPerfilMacro(): Call ValidarPerfil(True): End Sub
